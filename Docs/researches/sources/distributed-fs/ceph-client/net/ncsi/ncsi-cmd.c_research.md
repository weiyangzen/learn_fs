# sources/distributed-fs/ceph-client/net/ncsi/ncsi-cmd.c

## Purpose
This file builds and transmits NCSI command packets. It converts `struct ncsi_cmd_arg` requests into correctly sized skb payloads, fills NCSI and Ethernet headers, calculates checksums, allocates request tracking slots, and starts response timers.

## APIs, Types, and Functions
Public internal APIs are `ncsi_calculate_checksum()` and `ncsi_xmit_cmd()`. Static helpers include `ncsi_cmd_build_header()`, one command-specific builder per payload shape (`sp`, `dc`, `rc`, `ae`, `sl`, `svf`, `ev`, `sma`, `ebf`, `egmf`, `snfc`, `oem`, and default), `ncsi_cmd_handlers[]`, and `ncsi_alloc_command()`.

## Control Flow
`ncsi_xmit_cmd()` chooses a handler by command type, forcing the OEM builder for netlink-driven raw commands, derives fixed payload sizes unless the handler declares variable payload, allocates an `ncsi_request`, records netlink reply metadata when needed, builds the packet, prepends an Ethernet header, starts a one-second timer, and queues the skb with `dev_queue_xmit()`. `ncsi_alloc_command()` reserves link-layer headroom and tailroom, sizes the skb for NCSI header, aligned payload, checksum, and minimum Ethernet padding, then associates it with a request slot.

## State and Persistence
State is persisted in the allocated `ncsi_request`: command skb pointer, request ID, flags, timer enabled bit, and optional netlink sequence/port/header. The skb carries the NCSI command until response receipt or timeout frees the request.

## Dependencies and Integration
The file depends on `internal.h`, `ncsi-pkt.h`, Ethernet device properties, generic netlink metadata, `ncsi_alloc_request()`/`ncsi_free_request()`, and device transmit. Command builders are driven by `ncsi-manage.c` state machines and by raw netlink command requests from `ncsi-netlink.c`.

## Risks
Packet sizing and checksum offset must match the NCSI spec, especially for variable-length OEM payloads and 32-bit alignment padding. `unsafe_memcpy()` in the OEM builder assumes prior allocation accounted for caller-provided payload length. Timer/request state must be freed exactly once on TX error, timeout, or response. Broadcast source MAC is used until GMA succeeds, which may matter for devices with stricter filtering.

## Test Signals
Useful signals are byte-for-byte command packet tests for each handler, checksum verification, minimum-frame padding, variable OEM payload alignment, netlink-driven command replies/timeouts, timer cleanup on TX failure, and integration tests that probe/configure real or emulated NCSI channels.
