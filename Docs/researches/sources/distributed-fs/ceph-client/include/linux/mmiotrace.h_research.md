# sources/distributed-fs/ceph-client/include/linux/mmiotrace.h

## Purpose
`mmiotrace.h` declares kernel MMIO tracing and kmmio probe interfaces. It lets tracing code intercept MMIO page faults, observe ioremap/iounmap mappings, record MMIO reads/writes, and insert trace markers.

## Important APIs, Types, And Functions
Key types are `kmmio_pre_handler_t`, `kmmio_post_handler_t`, `struct kmmio_probe`, `enum mm_io_opcode`, `struct mmiotrace_rw`, and `struct mmiotrace_map`. APIs include `register_kmmio_probe()`, `unregister_kmmio_probe()`, `kmmio_init()`, `kmmio_cleanup()`, `is_kmmio_active()`, `kmmio_handler()`, `mmiotrace_ioremap()`, `mmiotrace_iounmap()`, `mmiotrace_printk()`, `enable_mmiotrace()`, `disable_mmiotrace()`, `mmio_trace_rw()`, `mmio_trace_mapping()`, and `mmio_trace_printk()`.

## Control Flow And State
When enabled, registered `kmmio_probe` entries describe address ranges and pre/post handlers. The page fault handler calls `kmmio_handler()` for trapped MMIO accesses, ioremap/iounmap hooks report mappings, and trace code emits `mmiotrace_rw` or `mmiotrace_map` records. `kmmio_count` indicates active probe count. Without `CONFIG_MMIOTRACE`, runtime helpers become inert stubs and report no active tracing.

## Dependencies And Integration Points
Dependencies include types and lists, plus `pt_regs`, resource sizes, and `__iomem` annotations from broader kernel headers. Integration points include page fault handling, ioremap/iounmap code, ftrace tracing output, driver MMIO debugging, PCI register tracing, and architecture fault semantics.

## Risks And Test Signals
Risks include trapping the wrong range, probe lifetime/list races, recursion from tracing MMIO while handling MMIO, address/width mismatches, and stale map IDs. Test signals include enabling/disabling tracing, registering overlapping probes, ioremap/iounmap trace records, read/write trace validation against a test driver, fault handler coverage, and non-`CONFIG_MMIOTRACE` build stubs.
