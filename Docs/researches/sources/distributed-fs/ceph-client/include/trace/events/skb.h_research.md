
# sources/distributed-fs/ceph-client/include/trace/events/skb.h

## Purpose
Defines socket-buffer lifecycle tracepoints for packet drops, skb consumption, and datagram copy faults, with symbolic drop-reason decoding.

## Important APIs, Types, and Functions
The header expands `DEFINE_DROP_REASON()` into `TRACE_DEFINE_ENUM()` exports and symbolic drop strings. Events are `kfree_skb`, `consume_skb`, and `skb_copy_datagram_iovec`. `kfree_skb` records skb pointer, drop location, protocol, and `enum skb_drop_reason`; `consume_skb` records skb and location; `skb_copy_datagram_iovec` records skb pointer, length, and error.

## Control Flow
Networking code emits `kfree_skb` when an skb is dropped with a reason, `consume_skb` when it is successfully consumed, and `skb_copy_datagram_iovec` when copying packet data to userspace iovecs completes or fails.

## State and Persistence
The header stores no skb state. Trace records snapshot pointers, protocol, reason, locations, lengths, and errors into tracing buffers. Pointer values are lifetime-limited diagnostics and must not be dereferenced by consumers.

## Dependencies and Integration Points
Depends on `linux/skbuff.h`, `linux/netdevice.h`, `linux/tracepoint.h`, and drop-reason definitions. Integrates with core networking, drop monitor tooling, perf/BPF packet-drop analysis, and protocol stacks.

## Risks
Drop-reason enum/string drift can break tooling. Hot packet paths can generate large trace volume. Pointer/location fields can expose kernel addresses depending on formatting restrictions. Consumers must handle `NOT_SPECIFIED` and evolving drop reasons.

## Test Signals
Signals include packet drop tests across protocol layers, drop_monitor/BPF consumers, skb consume tracing under normal traffic, datagram copy fault injection, and build checks when drop reasons are added.
