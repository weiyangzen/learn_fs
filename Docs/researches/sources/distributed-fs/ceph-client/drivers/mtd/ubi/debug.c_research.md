# sources/distributed-fs/ceph-client/drivers/mtd/ubi/debug.c

## Purpose
`debug.c` provides UBI diagnostics, debugfs controls, erase-count inspection, and optional fault-injection hooks. It is not part of normal data I/O, but it strongly affects testing and failure simulation.

## Important APIs, Types, And Functions
Dump helpers include `ubi_dump_flash()`, `ubi_dump_ec_hdr()`, `ubi_dump_vid_hdr()`, `ubi_dump_vol_info()`, `ubi_dump_vtbl_record()`, `ubi_dump_av()`, `ubi_dump_aeb()`, and `ubi_dump_mkvol_req()`. Debugfs lifecycle functions are `ubi_debugfs_init()`, `ubi_debugfs_exit()`, `ubi_debugfs_init_dev()`, and `ubi_debugfs_exit_dev()`. Debugfs file handlers are `dfs_file_read()`, `dfs_file_write()`, and the `detailed_erase_block_info` seq-file operations. `ubi_dbg_power_cut()` implements legacy power-cut countdown behavior. With `CONFIG_MTD_UBI_FAULT_INJECTION`, `should_fail_*()` wrappers are generated from Linux fault attributes.

## Control Flow
Global debugfs initialization creates `/sys/kernel/debug/ubi` and, when enabled, a `fault_inject` subtree. Per-device initialization creates `ubiX` files for generic checks, I/O checks, fastmap checks, background-thread disablement, legacy bitflip/I/O/power-cut emulation, power-cut min/max counters, detailed erase counts, and optional bitmask-driven fault injection.

`dfs_file_read()` maps the dentry being read to a field in `ubi->dbg`, formats booleans or numeric masks/counters, and holds a UBI device reference while reading. `dfs_file_write()` copies a short user buffer, parses either boolean `0/1` controls or integer mask/counter values, and updates `ubi->dbg`. The erase-block seq-file takes a device reference on open and iterates every physical eraseblock, skipping bad blocks and printing known erase counters from `ubi->lookuptbl` under `wl_lock`.

## State And Persistence
Most state is transient debug state in `struct ubi_debug_info`: check toggles, background-thread disable flag, legacy failure controls, `emulate_failures` mask, and power-cut countdown values. Dump helpers read flash or print in-memory structures without changing persistent state. Fault injection can deliberately cause lower I/O paths to simulate ECC, bitflip, read, write, erase, header, all-FF, and power-cut failures, which can indirectly alter persistent UBI state through recovery code under test.

## Dependencies And Integration Points
This file integrates with debugfs, seq_file, Linux fault-injection framework, MTD reads, WL lookup tables, UBI device refcounting, and the debug header inline hooks used by I/O, EBA, WL, and fastmap code. `build.c` calls global and per-device debugfs lifecycle functions during module/device attach and detach.

## Risks
Debugfs controls are privileged by filesystem permissions rather than ioctl capability checks. Race safety depends on `ubi_get_device()` holding the device alive while a debugfs file is accessed. `dfs_file_write()` accepts only small buffers and only checks the first byte for boolean toggles, which is intentional but easy to misuse in tests. Erase-count iteration returns errors from `ubi_io_is_bad()`, so debugfs reads can fail on MTD-level errors. Fault-injection combinations can produce destructive scenarios and must be isolated to test media.

## Test Signals
Signals include debugfs root/per-device creation and recursive removal, read/write round-trips for every toggle and counter, erase-count output stability while WL state changes, power-cut countdown behavior across min/max ranges, and fault-injection masks triggering the expected lower-layer failure paths.
