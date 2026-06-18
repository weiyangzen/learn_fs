# sources/distributed-fs/ceph-client/net/openvswitch/openvswitch_trace.h

## Purpose
`openvswitch_trace.h` declares trace events for key Open vSwitch datapath operations. The events expose packet, datapath, flow key, action, and upcall metadata to ftrace/perf-style tracing.

## Important APIs and Types
`TRACE_EVENT(ovs_do_execute_action)` records datapath pointer/name, skb device/name, skb length/data_len/truesize/frags/GSO fields, key hash/recirc/eth type/conntrack fields/validity, action type/length/data pointer, and whether the action is last in the list. `actions.c` emits it around action execution when the tracepoint is enabled.

`TRACE_EVENT(ovs_dp_upcall)` records similar datapath, skb, and key details plus upcall command, portid, and MRU. `datapath.c` emits it before queueing an upcall.

Both tracepoints use `ovs_dp_name(dp)`, `skb->dev->name`, `nla_type()`, `nla_len()`, `nla_data()`, and OVS key fields. The header ends with the standard trace include path/file macros and `include <trace/define_trace.h>`.

## Control Flow and Integration
The header is included normally by callers for tracepoint declarations and included once from `openvswitch_trace.c` with `CREATE_TRACE_POINTS` for definitions. Callers use the generated `trace_..._enabled()` checks to avoid unnecessary work.

## State and Persistence
Trace events are transient. Their field names and print formats are externally visible tracing ABI and useful for diagnostics.

## Dependencies
It depends on Linux tracepoint infrastructure and `datapath.h`. Because it references skb, netlink attribute, datapath, and flow key internals, changes to those structures can require trace field updates.

## Risks
Tracepoints must not dereference invalid skb, action, or key pointers. They are placed in hot paths, so enabled checks and field collection cost matter. Field naming typos or format mismatches can break trace consumers. The header must keep include guards and `TRACE_HEADER_MULTI_READ` semantics intact.

## Test Signals
Kernel build, trace event registration, enabling both events while running OVS traffic, and verifying printed key/action/upcall fields in tracefs are the main signals.
