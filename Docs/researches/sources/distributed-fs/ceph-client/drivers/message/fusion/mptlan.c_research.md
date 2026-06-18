# sources/distributed-fs/ceph-client/drivers/message/fusion/mptlan.c

## Purpose
`mptlan.c` implements IP-over-Fibre-Channel networking for Fusion MPT adapters whose firmware exposes the LAN protocol. It registers a Fibre Channel network device, posts receive bucket buffers to firmware, maps outbound skbs into LAN send requests, processes turbo and normal LAN replies, and converts FC encapsulated frames into Linux network packets.

## Important APIs, Types, and Functions
Important private types are `BufferControl`, `mpt_lan_priv`, and `mpt_lan_ohdr`. The netdev operations are `mpt_lan_open()`, `mpt_lan_close()`, `mpt_lan_sdu_send()`, and `mpt_lan_tx_timeout()`. Firmware callbacks and handlers include `lan_reply()`, `mpt_lan_send_turbo()`, `mpt_lan_send_reply()`, `mpt_lan_receive_post_turbo()`, `mpt_lan_receive_post_reply()`, `mpt_lan_receive_post_free()`, `mpt_lan_post_receive_buckets()`, `mpt_lan_reset()`, `mpt_lan_ioc_reset()`, and `mpt_lan_event_process()`. Device lifecycle is `mpt_lan_init()`, `mpt_lan_exit()`, `mptlan_probe()`, `mptlan_remove()`, and `mpt_register_lan_device()`.

## Control Flow
Module init registers a base callback context, reset handler, and MPT protocol driver. Probe scans IOC ports for `MPI_PORTFACTS_PROTOCOL_LAN`, allocates an FC netdev, initializes MTU and MAC address from LAN config Page1, and registers the device. Open sends a LAN reset, allocates TX/RX context stacks and buffer-control arrays, posts receive buckets, registers event handling, and starts the queue. Transmit pops a TX context, obtains an MPT frame, maps skb payload for DMA, builds a LAN send request with a transaction context and 64-bit SGE, posts the frame, and frees the skb when firmware returns a turbo or normal send reply. Receive replies identify bucket contexts, optionally copy small or multi-bucket packets into new skbs, recycle contexts, decrement posted-bucket counts, deliver the skb to `netif_rx()`, and schedule bucket refill when low.

## State and Persistence
Per-netdev state in `mpt_lan_priv` tracks the adapter pointer, port number, posted-bucket count, bucket threshold, free TX/RX context stacks, TX/RX `BufferControl` arrays, firmware queue limits, posted/received counters, delayed refill work, and active flag. Per-buffer state holds skb, DMA address, and length. Adapter state stores `ioc->netdev`. All state is volatile and rebuilt on open/probe; close/reset returns or frees outstanding DMA buffers.

## Dependencies and Integration Points
The driver depends on the Linux netdevice and FC device helpers (`alloc_fcdev`, FC address length, FC LLC/SNAP parsing), DMA mapping APIs, delayed work, the Fusion base message-frame/callback system, and MPI LAN request/reply definitions. It consumes port facts and LAN config pages populated by the base driver.

## Risks and Edge Cases
The code has fragile context-stack accounting for TX and RX buckets; underflow stops queues or fails posting. DMA mapping return values are not checked. Receive path comments and warnings document firmware bucket-count mismatch and a broadcast-byte-swap firmware bug. Some debug text is old and noisy. Reset and close paths must avoid double-freeing posted skbs while firmware still owns buckets. Multi-bucket and small-packet copy paths must recycle contexts correctly or leak buckets.

## Test Signals
Validation should include netdev registration for LAN-capable ports, open/close leak checks, TX completion for turbo and normal replies, RX for single, small-copy, and multi-bucket packets, bucket refill threshold behavior, IOC reset pre/post behavior, MTU boundary traffic from 96 to 65280 bytes, DMA mapping fault injection, and packet type/protocol parsing for broadcast, multicast, IP, ARP, and 802.2 frames.
