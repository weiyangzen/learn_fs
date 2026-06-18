<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-dbg.c -->
# sources/distributed-fs/ceph-client/drivers/usb/host/ehci-dbg.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/usb/host/ehci-dbg.c` is included by `ehci-hcd.c` and provides EHCI dynamic-debug formatting plus optional debugfs snapshots of controller state. It is troubleshooting infrastructure for queue heads, transfer descriptors, bandwidth tables, periodic schedules, registers, and root-hub state. The source was read as a complete 1081-line file.

## Important APIs, Types, and Functions

When `CONFIG_DYNAMIC_DEBUG` is enabled, notable helpers include `dbg_hcs_params()`, `dbg_hcc_params()`, `dbg_qtd()`, `dbg_qh()`, `dbg_itd()`, `dbg_sitd()`, `dbg_status_buf()`, `dbg_intr_buf()`, `dbg_command_buf()`, `dbg_port_buf()`, `dbg_status()`, `dbg_cmd()`, and `dbg_port()`. Debugfs support uses `struct debug_buffer`, file operations for `async`, `bandwidth`, `periodic`, and `registers`, and fill functions `fill_async_buffer()`, `fill_bandwidth_buffer()`, `fill_periodic_buffer()`, and `fill_registers_buffer()`. `create_debug_files()` and `remove_debug_files()` are called from EHCI start/stop. Without dynamic debug, the file compiles to inline no-op stubs.

## Control Flow

EHCI setup and runtime code call debug formatting helpers directly for logging. On controller start, `create_debug_files()` creates a per-bus debugfs directory under the global EHCI debug root and four read-only files. Opening a debug file allocates a `debug_buffer`; the first read lazily vmallocs output space, calls the selected fill routine under a mutex, and serves data through `simple_read_from_buffer()`. Fill routines take EHCI locks while walking live schedules or reading registers, then render a bounded snapshot.

## State and Persistence Behavior

The only owned state is transient debugfs dentries and per-open `debug_buffer` allocations. Debug output is a snapshot and not persisted. It reads live EHCI schedule state, register values, bandwidth accounting, and TT lists without modifying controller behavior.

## Dependencies and Integration Points

The file depends on internal EHCI structures from `ehci.h`, debugfs, dynamic debug, USB bus/HCD conversion helpers, PCI config access for extended capability reporting, and schedule structures owned by `ehci-q.c` and `ehci-sched.c`. It is not a standalone compilation unit; it is part of `ehci-hcd.c`.

## Risks and Edge Cases

Schedule snapshots race with hardware and software changes, so output is diagnostic rather than authoritative. Buffer sizes are bounded; long periodic or TT lists can be truncated. Some helpers return zero or no-op when dynamic debug is disabled, so tests must cover both build modes. Register dumping avoids MMIO access when `HCD_HW_ACCESSIBLE` is false, which is important during suspend.

## Test Signals

Build with and without `CONFIG_DYNAMIC_DEBUG` and debugfs. On a running EHCI controller, verify `/sys/kernel/debug/usb/ehci/<bus>/{async,bandwidth,periodic,registers}` opens, reads, truncates safely, closes without leaks, and reports suspended controllers without MMIO access. Exercise active bulk, interrupt, and isochronous transfers to populate schedule dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/host/ehci-dbg.c -->
