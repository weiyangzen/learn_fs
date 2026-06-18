# sources/distributed-fs/ceph-client/drivers/staging/octeon/ethernet-rx.c

## Purpose
NAPI receive path for Octeon Ethernet packets delivered by POW/SSO work queues.

## Important APIs, Types, And Functions
Defines `struct oct_rx_group` and exports `cvm_oct_rx_initialize()`, `cvm_oct_rx_shutdown()`, and `cvm_oct_poll_controller()` when netpoll is enabled. Important internals include `cvm_oct_do_interrupt()`, `cvm_oct_napi_poll()`, `cvm_oct_poll()`, `cvm_oct_check_rcv_error()`, and `copy_segments_to_skb()`.

## Control Flow
Initialization chooses an existing netdev for NAPI ownership, creates a NAPI instance per configured POW receive group, requests work-queue IRQs, configures interrupt thresholds, disables IRQs, and schedules NAPI to prime receive. IRQs disable themselves and schedule NAPI. Polling restricts the current core to the group, optionally uses async IOBDMA, fetches work entries up to budget, handles receive errors, either reuses an skb stored in the hardware packet pool for single-buffer packets or copies packet data into a fresh skb, maps the hardware port to `cvm_oct_device[]`, sets checksum status, delivers with `netif_receive_skb()`, and frees or refills hardware resources.

## State And Persistence
Static `oct_rx_group[16]` holds IRQ/group/NAPI state, and `oct_rx_ready` gates netpoll. FPA refill debt is tracked through FAU counters. State is runtime-only.

## Dependencies And Integration Points
Depends on netdev/NAPI, POW/SSO work queues, CVMX WQE and FPA structures, global `cvm_oct_device[]`, FPA memory helpers, and hardware group mask CSRs.

## Risks
Zero-copy receive depends on skb pointers stored before FPA buffers and on single-buffer WQEs. Error workaround rewrites packet pointers for bad 10Mbps preambles. Group-mask save/restore and scratch-space save/restore are required to avoid corrupting other users. Invalid or down ports drop packets.

## Test Signals
Single and multi-segment packets, WQE-contained packets, checksum flags, receive errors including length/FCS/alignment, down or unknown ports, multiple receive groups, CN68XX versus older POW paths, NAPI budget completion, netpoll, and FPA refill under pressure.
