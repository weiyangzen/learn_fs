# sources/distributed-fs/ceph-client/drivers/usb/host/ohci-dbg.c

## Purpose
`ohci-dbg.c` provides debug logging and debugfs snapshots for the generic OHCI host driver. It formats controller registers, root-hub status, endpoint descriptors, transfer descriptors, asynchronous schedules, periodic schedules, and frame timing into either kernel debug logs or per-controller debugfs files.

## Important APIs, types, and functions
Formatting macros include `edstring()`, `pipestring()`, `ohci_dbg_sw()`, `ohci_dbg_nosw()`, and `dbg_port_sw()`. Register and state dump helpers include `ohci_dump_intr_mask()`, `maybe_print_eds()`, `hcfs2string()`, `rh_state_string()`, `ohci_dump_status()`, `ohci_dump_roothub()`, and `ohci_dump()`. Descriptor dump helpers are `ohci_dump_td()` and `ohci_dump_ed()`.

Debugfs support uses `struct debug_buffer`, file operations for `async`, `periodic`, and `registers`, and helpers `show_list()`, `fill_async_buffer()`, `fill_periodic_buffer()`, `fill_registers_buffer()`, `alloc_buffer()`, `fill_buffer()`, `debug_output()`, `debug_close()`, `debug_async_open()`, `debug_periodic_open()`, `debug_registers_open()`, `create_debug_files()`, and `remove_debug_files()`. The file also uses the global `ohci_debug_root` dentry as the parent directory for per-bus debug directories.

## Control flow
Debug dumping is demand-driven. Kernel logging paths call `ohci_dump()`, `ohci_dump_td()`, or `ohci_dump_ed()` directly. Debugfs open allocates a small `debug_buffer` bound to the selected fill function and stores it in `file->private_data`. The first read calls `fill_buffer()`, which lazily allocates one zeroed page and invokes the fill function. Subsequent reads use `simple_read_from_buffer()` over the cached page until close frees it.

`fill_async_buffer()` locks `ohci->lock` and dumps the control and bulk ED chains through `show_list()`. `fill_periodic_buffer()` allocates a bounded `seen` array, locks the OHCI state, walks `NUM_INTS` periodic slots, prints load and ED metadata, and avoids expanding duplicate ED chains beyond the first observation. `fill_registers_buffer()` locks OHCI state, prints bus/device/driver identity, skips MMIO reads when `HCD_HW_ACCESSIBLE()` is false, then dumps status, HCCA frame, frame interval/remaining/threshold registers, hub-poll state, and root-hub registers.

## State and persistence behavior
Debug output is a snapshot, not live streaming. Each open debugfs file has one `struct debug_buffer`, one mutex, an optional allocated page, and a byte count. Hardware/software state is read under the OHCI spinlock where needed. The debugfs directory pointer is stored in `ohci->debug_dir` and removed recursively by `remove_debug_files()`. No data persists beyond the file lifetime.

## Dependencies and integration points
The file is meant to be included by or compiled with the OHCI core context and relies on `ohci.h` internals: `struct ohci_hcd`, `struct ohci_regs`, ED/TD layouts, root-hub helper macros, `ohci_readl()`, `ohci_frame_no()`, `ohci_to_hcd()`, `hc32_to_cpu()`, `hc32_to_cpup()`, and debug/logging macros. It depends on debugfs, file operations, mutexes, spinlocks, page allocation, and user-copy read helpers.

## Risks and edge cases
All debugfs fill functions are page-sized; large schedules can be truncated by `scnprintf()` size exhaustion. The periodic debug path limits duplicate ED tracking to `DBG_SCHED_LIMIT` entries, so complex schedules may omit repeated chain expansion. Some helpers print kernel pointers, which is acceptable for debug builds but sensitive from an information-disclosure perspective depending on debugfs permissions and pointer hashing configuration. Register reads are skipped when hardware is inaccessible, but async/periodic schedule dumps still depend on coherent in-memory OHCI structures.

## Test signals
With OHCI debugfs enabled, each controller should create `async`, `periodic`, and `registers` files under its bus directory. Reading them while idle, under bulk/control traffic, and under interrupt/ISO periodic traffic should produce coherent ED/TD chains and register snapshots without lock warnings, sleeping-in-atomic reports, or page overflows. Suspend reads should show the explicit inaccessible-hardware message in `registers` instead of faulting on MMIO.
