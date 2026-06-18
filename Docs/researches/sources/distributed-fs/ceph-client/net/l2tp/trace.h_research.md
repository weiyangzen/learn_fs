# sources/distributed-fs/ceph-client/net/l2tp/trace.h

## Purpose
`trace.h` defines the L2TP tracepoint surface. It gives tracing consumers stable events for tunnel/session registration and deletion, session sequence-number changes, and packet discard cases without embedding ad hoc debug logging in the hot paths.

## Important APIs, Types, and Functions
The file uses Linux tracepoint macros: `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, and `DEFINE_EVENT`. Shared event classes include `tunnel_only_evt`, `session_only_evt`, `session_seqnum_evt`, and `session_pkt_discard_evt`. Symbol formatting helpers map `enum l2tp_encap_type` and `enum l2tp_pwtype` values to readable names with `__print_symbolic()`.

## Control Flow
There is no runtime control flow beyond generated tracepoint code. L2TP core code includes this header and calls generated `trace_*` sites. `register_tunnel` captures tunnel identity, fd, ids, version, and encapsulation. `register_session` captures session/tunnel ids and pseudowire type. Delete/free events share name-only classes. Sequence and discard events capture `ns`, `nr`, packet sequence, expected receive sequence, and reorder queue length.

## State and Persistence
Trace events snapshot volatile L2TP state into the tracing ring buffer. They do not own tunnel/session references or persist configuration. String arrays copy fixed-size tunnel/session names into trace entries, avoiding pointer lifetime issues after free events.

## Dependencies and Integration Points
The header depends on `linux/tracepoint.h`, public `linux/l2tp.h`, and local `l2tp_core.h`. The `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and final `trace/define_trace.h` include integrate with the kernel trace generation model.

## Risks and Edge Cases
Trace formats become user-observable ABI for tooling, so field meaning and print format changes can break scripts. The `register_session` print format appears to print `sid`/`psid` in the final `tid`/`ptid` slots, which is a diagnostic accuracy risk. Event handlers must avoid dereferencing nullable tunnel pointers; the session registration event already falls back to zero ids when `session->tunnel` is absent.

## Test Signals
Enable L2TP trace events with ftrace/perf, create/delete tunnels and sessions, trigger sequence-number updates and reorder discards, and verify emitted fields match the live L2TP objects. A targeted test should validate the `register_session` printed tunnel ids because the format arguments are suspicious.
