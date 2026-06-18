# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeontx2/af/rvu_trace.h

## Purpose

`rvu_trace.h` declares tracepoints for RVU/OTX2 mailbox and parse-debug observability. It defines event payloads and print formats for message allocation, sends, response checking, interrupts, processing, wait timeouts, status reports, and NIX parse dumps.

## Important APIs, Types, And Functions

- `TRACE_SYSTEM rvu` places events under the RVU tracing subsystem.
- `otx2_msg_alloc` records PCI device, mailbox id/name, message size, and pcifunc.
- `otx2_msg_send` records number of messages, payload size, id, and pcifunc.
- `otx2_msg_check` records request/response ids and response code.
- `otx2_msg_interrupt` records the device, mailbox interrupt description, and interrupt bits.
- `otx2_msg_process` records mailbox processing result per id and pcifunc.
- `otx2_msg_wait_rsp` records response wait timeouts.
- `otx2_msg_status` records status strings and message counts.
- `otx2_parse_dump` records six 64-bit words from a NIX parse dump.

## Control Flow

The header follows the Linux trace event pattern. The guarded `TRACE_EVENT()` declarations are read once by normal includes and a second time through `trace/define_trace.h` when `CREATE_TRACE_POINTS` is set by `rvu_trace.c`. Call sites execute generated `trace_otx2_*()` functions, which are low overhead when disabled and copy event fields into trace buffers when enabled.

## State And Persistence

The header defines trace event metadata but no driver state. Event records contain copies of message ids, strings, device names, response codes, interrupt masks, and parse words at emission time. Persistence depends on external tracing buffers and tools.

## Dependencies And Integration Points

It includes Linux tracepoint and PCI headers plus `mbox.h` for mailbox id-to-name conversion. It is included by AF and NIC code that emits mailbox trace events, notably mailbox interrupt handlers and message allocation/processing paths.

## Risks

- `otx2_parse_dump` dereferences six words from the passed pointer without length checking; callers must provide a valid six-word buffer.
- `TP_printk` calls `otx2_mbox_id2name()` at formatting time, so mailbox id tables must remain available and stable.
- Trace strings expose mailbox flow details; that is useful for debug but can increase trace volume under heavy mailbox traffic.
- `TRACE_INCLUDE_PATH .` assumes the build include path resolves the trace header correctly.

## Test Signals

Enable each event through ftrace/perf while exercising PF/AF and PF/VF mailbox traffic. Confirm event fields show correct PCI names, mailbox message names, pcifunc values, response errors, and parse dump words. Build tests should include modular and built-in configurations.
