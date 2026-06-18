# sources/distributed-fs/ceph-client/drivers/net/fjes/fjes_trace.h

## Purpose
`fjes_trace.h` declares FJES tracepoints for hardware command execution, endpoint buffer registration/unregistration, debug trace commands, and endpoint stop-request interrupt handling. These tracepoints provide structured observability around the driver's most failure-prone hardware protocol transitions.

## Important APIs and Trace Events
Hardware command events include `fjes_hw_issue_request_command`, `fjes_hw_request_info`, and request-info error tracing. Buffer command events include register/unregister request, result, and error events. Debug events include start-debug request/result/error and stop-debug result/error. Main-driver events include pre/post traces for TXRX stop request IRQs and device stop request IRQs. The footer sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` and includes `<trace/define_trace.h>`.

## Control Flow
When included normally, the header declares tracepoint call sites. When included by `fjes_trace.c` with `CREATE_TRACE_POINTS`, it emits definitions. The `TP_fast_assign` blocks copy register fields, response codes, endpoint statuses, zones, vmalloc-backed buffer physical addresses, stop bitmasks, and RX status values into trace records; `TP_printk` formats them for human-readable trace output.

## State, Dependencies, and Integration
The tracepoints depend on `struct fjes_hw`, command unions, register unions, endpoint shared-memory structures, `vmalloc_to_page()`, and tracepoint macros. They integrate directly with `fjes_hw.c` command paths and `fjes_main.c` interrupt stop-handshake paths.

## Risks and Test Signals
Risks include tracepoint ABI churn, dereferencing endpoint arrays while hardware is tearing down, costly physical-address derivation in trace assignment, and mismatches between dynamic array lengths and `max_epid`. Test signals should include enabling each tracepoint while issuing info/share/unshare/debug commands, triggering stop-request IRQ paths, validating dynamic zone/status arrays, and building with tracing/sparse configurations.
