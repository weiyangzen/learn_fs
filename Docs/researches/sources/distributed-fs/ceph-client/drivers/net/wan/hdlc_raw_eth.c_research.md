# sources/distributed-fs/ceph-client/drivers/net/wan/hdlc_raw_eth.c

## Purpose
`hdlc_raw_eth.c` presents an HDLC link as an Ethernet-like netdevice. It uses Ethernet header parsing for receive and pads short transmit frames before delegating to the hardware HDLC transmitter.

## Important APIs, Types, And Functions
The protocol callback object sets `.type_trans = eth_type_trans`, `.xmit = eth_tx`, and `.ioctl = raw_eth_ioctl`. `eth_tx()` pads frames shorter than `ETH_ZLEN`, growing tailroom if required, then calls `dev_to_hdlc(dev)->xmit()`. `raw_eth_ioctl()` mirrors raw HDLC setup but calls `ether_setup()` and assigns a random Ethernet address.

## Control Flow
`IF_PROTO_HDLC_ETH` requires admin privileges and a down device. Defaults are normalized to NRZ and CRC16 PR1 CCITT. After successful hardware attach and protocol attach, the module stores settings, preserves the old TX queue length across `ether_setup()`, disables TX skb sharing, randomizes MAC address, notifies the type change, and marks the device non-dormant. Outbound packets go through `hdlc_start_xmit()`, which calls this module's `eth_tx()`.

## State And Persistence
Per-device state stores only `raw_hdlc_proto` settings. MAC address is generated for the current netdevice instance and is not made durable by this file. No timers or child objects are used.

## Dependencies And Integration Points
This module integrates with generic HDLC, Ethernet netdevice setup, `eth_type_trans()`, skb head/tail management, netdevice stats, and WAN protocol ioctls.

## Risks
The module changes a WAN HDLC device into an Ethernet-shaped device; generic HDLC detach must reset all altered netdevice fields, which `hdlc_setup_dev()` explicitly handles. Padding failures update `tx_dropped` and consume the skb. Protocol correctness depends on both endpoints agreeing to Ethernet emulation over HDLC.

## Test Signals
Test attach/detach restores device shape, random MAC assignment, TX padding to `ETH_ZLEN`, behavior when `pskb_expand_head()` fails, receive classification via `eth_type_trans()`, and `IF_GET_PROTO` returning the stored line settings.
