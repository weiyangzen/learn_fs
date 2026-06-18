# sources/distributed-fs/ceph-client/kernel/trace/trace_mmiotrace.c

## Purpose
Implements the `mmiotrace` tracer, which records memory-mapped I/O reads, writes, maps, unmaps, PCI device metadata, and textual marks in a custom text format consumed by MMIO tracing tools.

## APIs, Control Flow, and State
The tracer is registered by `init_mmio_trace()` as `mmiotrace` with init, reset, start, pipe-open, close, read, and print-line callbacks. `mmio_trace_init()` stores the active `trace_array`, resets overrun state, and calls `enable_mmiotrace()`. Reset disables mmiotrace, clears data, and drops the active trace array. Export-facing recording functions are `mmio_trace_rw()`, `mmio_trace_mapping()`, and `mmio_trace_printk()`, which append `TRACE_MMIO_RW`, `TRACE_MMIO_MAP`, or `TRACE_PRINT` records.

State includes `mmio_trace_array`, `overrun_detected`, `prev_overruns`, atomic `dropped_count`, and per-reader `struct header_iter` stored in `iter->private` for iterating PCI devices. `mmio_pipe_open()` emits the format version and starts PCI enumeration. `mmio_read()` first reports ring-buffer or reservation losses as `MARK ... Lost N events`, then prints one `PCIDEV` line per PCI device until enumeration completes. Event formatting is handled by `mmio_print_rw()`, `mmio_print_map()`, and `mmio_print_mark()`; unknown event types are ignored to keep the stream parser-compatible.

## Dependencies, Integration, Risks, and Tests
The file depends on the architecture MMIO tracing backend, PCI enumeration, the tracing ring buffer, `trace_output.h`, and `trace_vprintk()`. It integrates with tracefs current tracer selection, `trace_pipe`, PCI resource reporting, and MMIO instrumentation that calls the recording hooks.

Risks include a NULL or stale `mmio_trace_array` if record hooks are called outside the enabled tracer lifetime, event loss under high MMIO rates, the noted close-path caveat for pipe readers, PCI device reference leaks if iteration is not destroyed, and strict output-format compatibility with existing parsers. Test signals include enabling/disabling `mmiotrace`, reading the version and `PCIDEV` header stream, generating MMIO read/write/map/unmap records, forcing buffer overruns to see loss markers, and checking that PCI device references are released when the pipe closes or enumeration ends.
