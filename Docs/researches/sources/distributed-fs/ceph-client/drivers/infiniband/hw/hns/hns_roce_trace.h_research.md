# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hns/hns_roce_trace.h

## Purpose
`hns_roce_trace.h` defines ftrace tracepoints for HNS RoCE diagnostics. It captures CQE flush heads, SQ/RQ/SRQ WQE contents, async event queue entries, MR metadata, MTR buffer attributes, and command queue requests/responses.

## Important APIs, Types, And Functions
The file uses `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, and `TRACE_EVENT` to define `hns_sq_flush_cqe`, `hns_rq_flush_cqe`, `hns_sq_wqe`, `hns_rq_wqe`, `hns_srq_wqe`, `hns_ae_info`, `hns_mr`, `hns_buf_attr`, `hns_cmdq_req`, and `hns_cmdq_resp`. It references `enum hns_roce_trace_type`, `struct hns_roce_mr`, `struct hns_roce_buf_attr`, `struct hns_roce_cmq_desc`, HNS SGE sizes, and v2 EQE size constants.

## Control Flow
Trace events are passive instrumentation compiled through `trace/define_trace.h`. WQE and AEQE tracepoints copy little-endian 32-bit words into trace entries before printing arrays. MR and buffer-attribute tracepoints snapshot key fields from software structures. Command queue tracepoints record opcode, flags, return value, and six data words with the device name.

## State And Persistence
There is no owned driver state. Trace records are transient kernel tracing data controlled by ftrace/perf infrastructure. The tracepoint arrays impose fixed maximum captured sizes: WQE capture is capped by `MAX_WQE_SIZE`, and AEQE capture by `HNS_ROCE_V3_EQE_SIZE`.

## Dependencies And Integration Points
The header depends on Linux tracepoint infrastructure, `string_choices.h`, HNS device and v2 hardware headers, and the build convention that `TRACE_INCLUDE_FILE` and `TRACE_INCLUDE_PATH` match this header. It is included by MR and command paths that emit diagnostics.

## Risks
`wqe_template` stores `len / sizeof(__le32)` words into a fixed array without an explicit clamp in the trace assignment; callers must pass lengths no larger than `MAX_WQE_SIZE`. `hns_buf_attr` unconditionally reads `region[0..2]`, which is safe only if the array has at least three entries. Trace format strings become user-visible ABI for tracing tools. High-rate WQE/command tracing can expose traffic metadata and impose overhead.

## Test Signals
Test tracepoint compilation with `CREATE_TRACE_POINTS`, enabling each event through ftrace, WQE length boundaries, AEQE dump length, MR and buffer-attribute output during MR/QP/SRQ creation, command request/response output, and trace parsing compatibility after structure or enum changes.
