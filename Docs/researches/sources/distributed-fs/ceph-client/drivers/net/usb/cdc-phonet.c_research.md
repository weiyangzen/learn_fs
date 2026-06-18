# sources/distributed-fs/ceph-client/drivers/net/usb/cdc-phonet.c

## Purpose

`cdc-phonet.c` implements a USB CDC Phonet host network interface for Nokia-style Phonet links. It creates an `ARPHRD_PHONET` point-to-point netdev rather than an Ethernet netdev, claims a paired CDC data interface, toggles data altsettings on open/close, and transfers Phonet packets over bulk endpoints.

## Important APIs, types, and functions

`struct usbpn_dev` stores the netdev, control and data interfaces, USB device, TX/RX pipes, active altsetting, disconnect flag, TX queue count, locks, an in-progress fragmented RX SKB, and a flexible array of RX URBs. `usbpn_setup()` configures the netdev type, header ops, MTU bounds, one-byte media address, queue length, and free-on-unregister behavior. Netdev ops are `usbpn_open()`, `usbpn_close()`, `usbpn_xmit()`, and `usbpn_siocdevprivate()`.

USB lifecycle is handled by `usbpn_probe()` and `usbpn_disconnect()`. RX/TX URB completions are `rx_complete()` and `tx_complete()`, with `rx_submit()` allocating page-backed receive buffers.

## Control flow

Probe parses CDC descriptors from the control interface with `cdc_parse_cdc_header()`, requiring both a union descriptor and Phonet magic. It finds the data interface from the union slave interface, verifies exactly two altsettings with one inactive and one active endpoint pair, allocates a netdev sized for `rxq_size` URB pointers, chooses RX/TX bulk pipes by endpoint direction, claims the data interface, forces inactive mode, and registers the netdev.

Opening switches the data interface to the active altsetting, allocates and submits 17 RX URBs using full pages, and wakes the TX queue. TX allocates one URB per SKB, rejects non-Phonet protocols, submits bulk output with `URB_ZERO_PACKET`, increments an internal queue count, and stops the queue at `tx_queue_len`. TX completion updates packet/error counters, decrements the queue count, wakes the queue, frees the SKB, and frees the URB. RX completion chains full-page fragments into `pnd->rx_skb` until a short transfer marks the last fragment, then strips the one-byte media header, sets Phonet protocol, updates stats, and delivers via `netif_rx()`.

## State and persistence

The only persistent runtime state is in `struct usbpn_dev`, including claimed interfaces, active altsetting, active URBs, TX queue depth, and a partially assembled RX SKB. There is no hardware nonvolatile programming or filesystem persistence.

## Dependencies and integration points

The driver depends on USB CDC descriptor parsing, Phonet header operations, Phonet ioctl constants, netdev registration, page-backed SKB fragments, spinlocks, and USB interface claiming/releasing. It shares the USB driver across both the control and claimed data interfaces.

## Risks

Risk centers on fragmented RX assembly and disconnect ordering. A stream of full-page URBs can accumulate fragments until `MAX_SKB_FRAGS`; overflow drops the assembled SKB and increments length errors. `usbpn_disconnect()` assumes `usb_get_intfdata()` is valid and uses a `disconnected` flag to handle double callbacks from the two claimed interfaces. TX queues can stall if URB completion is lost, but normal completion always wakes the queue.

## Test signals

Important tests include CDC descriptor rejection paths, alternate data-interface layouts, open/close altsetting toggles, fragmented RX across multiple pages, short-packet finalization, non-Phonet TX drop behavior, queue stop/wake under multiple TX URBs, private Phonet autoconf ioctl, and disconnect through either control or data interface.
