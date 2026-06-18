# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace.c

## Purpose

`trace.c` provides the implementation backing HFI1 tracepoint formatting helpers and debug trace functions. With `CREATE_TRACE_POINTS` defined before including `trace.h`, it instantiates the tracepoints declared across the HFI1 trace headers. It also parses and formats packet headers, extended verbs headers, SDMA flags, TID entries, and receive-context histogram output used by trace events.

## Important APIs and Functions

Header sizing and parsing:

- `hfi1_trace_packet_hdr_len()` and `hfi1_trace_opa_hdr_len()` compute dynamic extended header lengths for incoming packets and outgoing OPA headers, supporting both 9B and 16B formats.
- `hfi1_trace_parse_9b_bth()`, `hfi1_trace_parse_16b_bth()`, `hfi1_trace_parse_9b_hdr()`, and `hfi1_trace_parse_16b_hdr()` extract fields into trace entry storage.
- `hfi1_trace_fmt_lrh()` and `hfi1_trace_fmt_rest()` format LRH/16B and BTH/L4 portions into `trace_seq` buffers.

Extended header formatting:

- `parse_everbs_hdrs()` decodes immediate data, RETH, AETH, DETH, IETH, atomic headers, and HFI1 TID RDMA headers for WRITE_REQ, WRITE_RESP, WRITE_DATA, READ_REQ, READ_RESP, ACK, and RESYNC.
- `parse_syndrome()` converts AETH syndrome classes to ACK, RNRNAK, or NAK labels.
- `hfi1_trace_get_tid_ctrl()`, `hfi1_trace_get_tid_len()`, and `hfi1_trace_get_tid_idx()` expose TID entry fields to trace headers.

Other helpers:

- `parse_sdma_flags()` prints SDMA descriptor state.
- `print_u32_array()` formats arrays for trace output.
- `hfi1_trace_print_rsm_hist()` maintains and prints an atomic receive-side mapping histogram.
- `__hfi1_trace_fn(...)` instances implement formatted debug trace functions for AFFINITY, PKT, PROC, SDMA, LINKVERB, DEBUG, SNOOP, CNTR, PIO, DC8051, FIRMWARE, RCVCTRL, TID, MMU, and IOCTL.

## Control Flow and State

Trace events in headers capture raw fields in `TP_fast_assign` and call these helpers from `TP_printk`. The helper functions do not drive device behavior, but they are part of runtime observability and must be safe when tracing arbitrary packets. The file keeps only a small static `hfi1_ctxt_hist` counter array for RSM histogram traces; other state is derived from packet/header arguments.

## Dependencies and Integration Points

The file depends on HFI1 packet structures, InfiniBand header accessors, opcode length tables, TID RDMA header layouts, expected receive TID-entry macros, SDMA descriptor masks, and Linux tracepoint/trace_seq APIs. It integrates with `trace_ibhdrs.h`, `trace_ctxts.h`, `trace_tx.h`, and `trace_dbg.h`.

## Risks and Test Signals

Formatting code can still break kernel tracing if dynamic header lengths are wrong, if opcode-specific unions are decoded with the wrong layout, or if endian conversion differs from packet encoding. TID RDMA decoding is especially useful for validating `tid_rdma.c`: packet traces should show matching TID flow PSNs, flow QPs, JKEYs, verbs PSNs, AETH syndromes, and TID entry fields through read/write success and retry paths. Tests should exercise trace formatting for 9B, 16B, management packets, ordinary RC packets, and every TID RDMA opcode.
