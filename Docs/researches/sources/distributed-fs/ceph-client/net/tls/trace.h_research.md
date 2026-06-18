<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/trace.h -->
# sources/distributed-fs/ceph-client/net/tls/trace.h

## Purpose
`trace.h` declares trace events for TLS device offload setup, device-decrypted records, RX resynchronization, and TX resynchronization. These events provide low-level observability for hardware kTLS behavior.

## Important APIs, Types, and Functions
- `TRACE_SYSTEM tls` names the trace event subsystem.
- `tls_device_offload_set` records socket, direction, TCP sequence, record number, and setup result.
- `tls_device_decrypted` records socket, TCP sequence, record number, record length, and encrypted/decrypted flags.
- `tls_device_rx_resync_send`, `tls_device_rx_resync_nh_schedule`, and `tls_device_rx_resync_nh_delay` describe RX resync activity.
- `tls_device_tx_resync_req` and `tls_device_tx_resync_send` describe TX resync requests and responses.
- `get_unaligned_be64()` converts record number bytes into printable `u64` values.

## Control Flow
Each `TRACE_EVENT` expands into static tracepoint metadata and helper code. Device TLS code calls the generated `trace_tls_*` functions at offload and resync points; formatting occurs when a trace consumer enables the event.

## State and Persistence
No persistent state is stored in the header. Trace entries capture transient socket pointers, TCP sequence numbers, record numbers, lengths, booleans, and return codes into ring buffers managed by ftrace/perf.

## Dependencies and Integration Points
The header integrates with the Linux tracepoint framework and is instantiated by `trace.c`. It is specifically oriented to TLS device offload code, not software-only kTLS.

## Risks and Edge Cases
Tracepoint ABI names and field layouts are consumed by debugging tools, so changes can break scripts. Socket pointers are printed with `%p` and are subject to kernel pointer hashing/security policy. Record-number pointers must reference at least 8 bytes when events are emitted.

## Test Signals
Enable events under `events/tls`, exercise TLS device offload setup and resync paths, and verify that expected fields appear with sane TCP sequence and record-number progression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/trace.h -->
