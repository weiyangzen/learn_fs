# sources/distributed-fs/ceph-client/tools/testing/selftests/net/tcp_ao/seq-ext.c

## Purpose
`seq-ext.c` verifies TCP-AO sequence-number extension behavior when 32-bit TCP sequence numbers wrap. It forces both directions near wraparound through TCP repair, migrates the connection to new ports to avoid stale packets, then confirms the connection survives and SNE counters increment.

## Important APIs, Types, And Functions
Key functions are `test_adjust_seqs()`, `test_sk_restore()`, `server_fn()`, and `client_fn()`. The test uses TCP repair checkpoint/restore helpers, AO repair helpers, `trace_ao_event_sne_expect()`, netstat counter reads, echo verification, and `test_assert_counters()`.

## Control Flow
The server and client first establish a normal AO connection and exchange `quota` bytes. Both sides then checkpoint TCP and AO state, kill their old sockets, increment their local ports, adjust incoming and outgoing sequence fields close to `UINT32_MAX`, restore onto the new endpoints, and exchange another `quota` bytes. The adjustments are asymmetric so send and receive rollover occur on different segments. The server registers expected send and receive SNE update tracepoints for both directions before the post-restore traffic.

## State, Persistence, And Dependencies
All state is transient socket state, repair images, AO repair images, and the global `client_new_port` used by the server restore. Netstat counters `TCPAOGood` and `TCPAOBad` provide namespace-level verification. Dependencies include TCP-AO repair ABI support, ftrace SNE tracepoint helpers, and the shared two-thread namespace harness.

## Integration Points
This is a high-value integration point between TCP repair, AO sequence extension tracking, port migration, counter accounting, and authenticated data transfer. It tests behavior that would be hard to reach through normal traffic alone.

## Risks
The test relies on exact sequence-state fields in `struct tcp_sock_state`; kernel repair ABI changes can break the setup. Barrier ordering between the two restored endpoints is critical. It checks `TCPAOBad` as a whole namespace counter after the test, so prior unexpected AO failures in the namespace would taint the result.

## Test Signals
`main()` plans 8 checks. Passing signals are successful pre- and post-migration echo, `TCPAOGood` increasing, `TCPAOBad` remaining zero, per-socket counters showing only good packets, expected SNE tracepoints, and nonzero `snd_sne` and `rcv_sne` in the final AO checkpoint.
