# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_trace.h

## Purpose

`i40e_trace.h` defines Linux ftrace/tracepoint instrumentation for i40e. It provides wrapper macros so shared code can call tracepoints by logical name, then declares trace events for NAPI polling, Tx cleanup, Rx cleanup, and transmit attempts/drops. The header follows kernel tracepoint conventions for loadable modules by using a special include guard and `TRACE_INCLUDE_FILE`/`TRACE_INCLUDE_PATH` before including `trace/define_trace.h`.

## Important APIs, Types, and Functions

- `TRACE_SYSTEM i40e` names the trace subsystem.
- `i40e_trace(trace_name, args...)` expands to `trace_i40e_<trace_name>(args...)`.
- `i40e_trace_enabled(trace_name)` expands to the generated enabled predicate for a tracepoint.
- `TRACE_EVENT(i40e_napi_poll)` records NAPI budget, per-ring budget, Rx/Tx cleaned counts, completion booleans, interrupt number, current CPU, q-vector name, netdev name, and IRQ affinity mask.
- `DECLARE_EVENT_CLASS(i40e_tx_template)` is reused by `i40e_clean_tx_irq` and `i40e_clean_tx_irq_unmap`, recording ring, descriptor, buffer, and netdev.
- `DECLARE_EVENT_CLASS(i40e_rx_template)` is reused by `i40e_clean_rx_irq` and `i40e_clean_rx_irq_rx`, recording ring, RX descriptor, XDP buffer, and netdev.
- `DECLARE_EVENT_CLASS(i40e_xmit_template)` is reused by `i40e_xmit_frame_ring` and `i40e_xmit_frame_ring_drop`, recording skb, ring, and netdev.

## Control Flow

The header has compile-time tracepoint generation flow rather than normal runtime control flow. During compilation, the trace macros generate event structures, fast assignment code, print formats, and `trace_i40e_*` call sites. At runtime, when call sites invoke `i40e_trace()`, the generated tracepoint either records the fields if enabled or is skipped by the tracepoint machinery. The first fields in the Tx event class intentionally match `TP_PROTO` to support BCC `tplist` argument parsing.

## State and Persistence Behavior

No driver state is persisted here. Tracepoints expose transient runtime state: NAPI scheduling and completion, queue vector CPU/IRQ affinity, descriptor and buffer addresses, skb pointers, and netdev names. The `NO_DEV` fallback avoids dereferencing a missing NAPI netdev name. When tracing is disabled, overhead should remain low; when enabled, trace buffers outside the driver persist event samples according to kernel tracing configuration.

## Dependencies and Integration Points

The file depends on Linux `tracepoint.h` and on i40e types visible at inclusion sites: `struct napi_struct`, `struct i40e_q_vector`, `struct i40e_ring`, `struct i40e_tx_desc`, `struct i40e_tx_buffer`, `union i40e_16byte_rx_desc`, `struct xdp_buff`, and `struct sk_buff`. It integrates with the kernel tracing subsystem, ftrace/perf/BPF tooling, and i40e datapath call sites in NAPI, Tx cleanup, Rx cleanup, and xmit/drop paths. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE i40e_trace` are required because this trace header lives in the driver directory rather than `include/trace/events`.

## Risks

- Tracepoint field expressions dereference ring and netdev pointers. Call sites must only invoke these tracepoints when those objects are valid.
- Trace output includes kernel pointers. Pointer formatting is standard for tracepoints, but observability policy depends on kernel pointer restrictions and tracing permissions.
- Changing event field order or names can break BPF/perf scripts that rely on the existing tracepoint ABI.
- The include guard intentionally differs from normal headers. Simplifying it can break multi-read trace generation.
- Tracepoint overhead is usually low when disabled, but enabled tracing in high-rate Tx/Rx paths can perturb performance.

## Test Signals

Build success is the first signal because trace headers are sensitive to macro ordering. Runtime validation includes enabling `i40e:i40e_napi_poll`, `i40e:i40e_clean_tx_irq`, `i40e:i40e_clean_rx_irq`, and `i40e:i40e_xmit_frame_ring*` via ftrace/perf, generating traffic, and confirming events include expected netdev names, queue names, budgets, cleaned counts, descriptor pointers, and drops. BPF `tplist` compatibility should be checked after changing event prototypes or field ordering.
