# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_dbg.h

## Purpose

`trace_dbg.h` defines the HFI1 formatted debug trace facility. It provides a shared trace event template for printf-style debug messages and generates one trace function/event pair per debug category.

## Important APIs

`hfi1_trace_template` stores the caller function name and formatted message using `__vstring`. `__hfi1_trace_def(lvl)` declares `__hfi1_trace_<lvl>()` and defines the corresponding `hfi1_<lvl>` trace event. `__hfi1_trace_fn(lvl)` provides the implementation body used in `trace.c`.

The file declares categories including AFFINITY, PKT, PROC, SDMA, LINKVERB, DEBUG, SNOOP, CNTR, PIO, DC8051, FIRMWARE, RCVCTRL, TID, MMU, and IOCTL. `hfi1_cdbg(which, fmt, ...)` and `hfi1_dbg(fmt, ...)` are the call-side macros. `hfi1_dbg_early()` can map to `trace_printk()` when `HFI1_EARLY_DBG` is explicitly enabled.

## Control Flow and State

Callers invoke the macros with a category and format string. The generated function packages the varargs into `struct va_format`, calls the tracepoint, and returns. The tracepoint stores only event data; no driver state is mutated.

## Dependencies and Risks

The file depends on Linux tracepoint support, `trace_seq`, `va_format`, and HFI1 headers. It suppresses GCC `-Wsuggest-attribute=format` around the trace template declarations because the generated trace machinery does not match normal format attribute inference.

Risks include format-string/type mismatches in callers, overly long messages making console trace output hard to read, and accidentally enabling early debug tracing in committed code. Test signals are successful compilation of all generated trace functions and readable category-specific events during driver debug sessions.
