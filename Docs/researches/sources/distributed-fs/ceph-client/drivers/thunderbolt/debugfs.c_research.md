# sources/distributed-fs/ceph-client/drivers/thunderbolt/debugfs.c

## Purpose

`debugfs.c` exposes Thunderbolt/USB4 diagnostic and debug controls under debugfs. It can dump switch, port, path, counter, sideband, retimer, DROM, and service state; optionally write raw config and sideband registers; and optionally drive USB4 lane margining operations for ports and retimers.

## Important APIs, Types, and Functions

Public entry points are `tb_debugfs_init/exit()`, `tb_switch_debugfs_init/remove()`, `tb_xdomain_debugfs_init/remove()`, `tb_service_debugfs_init/remove()`, and `tb_retimer_debugfs_init/remove()`.

Register helpers include `validate_and_copy_from_user()`, `parse_line()`, `regs_write()`, `port_regs_show()`, `switch_regs_show()`, `path_show()`, `counters_show()`, `counters_write()`, `sb_regs_show()`, `port_sb_regs_show()`, and `retimer_sb_regs_show()`. `port_sb_regs` and `retimer_sb_regs` enumerate USB4 sideband registers and their supported byte widths.

When `CONFIG_USB4_DEBUGFS_MARGINING` is enabled, `struct tb_margining` tracks lane margining capabilities, current settings, result buffers, lane selection, BER contour, software dwell time, error-counter mode, voltage/time mode, and Gen4 eye selection. Margining file operations expose `caps`, `lanes`, `mode`, `run`, `results`, `test`, `margin`, `eye`, and software-only tuning attributes.

## Control Flow

Initialization creates a global `thunderbolt` debugfs root. Each switch creates a directory named after the device, a switch `regs` file, an optional `drom` blob, and per-port directories for active ports. Port directories expose config registers, path tables, counters, sideband registers for USB4 ports, and optional margining files. Retimers get sideband and optional margining entries under a retimer-specific directory.

Show paths acquire runtime PM on the target device, take the domain mutex, read config or sideband registers, format data as offset-relative tables, then release the mutex and runtime PM reference. Write paths copy at most one page from userspace, parse one line at a time, taint the kernel for raw hardware writes, and write registers under the same runtime PM and domain lock.

Margining allocation reads link generation, asymmetric width capability, and USB4 margining capabilities, then creates only the files supported by the device. Running a margining operation validates lane settings, temporarily disables CL states on the downstream switch if present, clears prior results, executes software or hardware margining through USB4 helpers, restores CL states, and stores raw results for later reads.

## State and Persistence Behavior

The file keeps a global debugfs root and per-device dentries. It also stores `struct tb_margining` objects in USB4 port or retimer state while debugfs entries exist. Result arrays persist until the next margining run, explicit result clear, or device removal.

Most reads are observational, but writes can change live hardware configuration, clear counters, alter sideband registers, and run margining tests. These operations are not persisted by this file, but some hardware effects can persist until reset, link retraining, or firmware action. `add_taint(TAINT_USER)` marks raw user-triggered hardware writes.

## Dependencies and Integration Points

The file depends on debugfs, seq_file, uaccess, runtime PM, the Thunderbolt domain mutex, config-space helpers (`tb_sw_read/write`, `tb_port_read/write`), USB4 sideband helpers, USB4 margining helpers, CL-state helpers, retimer objects, XDomain objects, and DROM blobs populated by EEPROM/NVM code.

It integrates with switch/port discovery and removal through the public init/remove hooks. Service drivers such as `dma_test.c` create their own directories under service debugfs directories.

## Risks and Edge Cases

Raw debugfs write support is intentionally dangerous and compile-time gated. Misuse can desynchronize driver state from hardware; the taint marker documents that risk. The parser accepts only numeric fields in expected short or long formats and stops silently when lines no longer parse.

In `sb_regs_write()`, the size check uses `bytes_read > sb_regs->size` instead of `sb_reg->size`. Since `sb_regs` points to the first table element, writes to later registers may be checked against the first register's size, which is a bug signal for sideband write validation.

Several user-buffer handlers set `buf[count - 1] = '\0'` after copying a page-sized bounded buffer. Zero `count` is rejected by `validate_and_copy_from_user()`, so underflow is avoided, but inputs larger than one page are truncated.

Margining division uses capability-derived step counts. If firmware reports zero voltage or time steps, result formatting can divide by zero. Link state can change between allocation and run; `validate_margining()` rechecks RX2 asymmetric width but other capability assumptions remain cached.

## Test Signals

Tests should cover debugfs creation/removal for switches, ports, retimers, services, and XDomains; register table reads with partial access failures; raw write parsing under `CONFIG_USB4_DEBUGFS_WRITE`; counter clearing; sideband write size validation; runtime PM failure paths; and device removal while files are open.

Margining tests need hardware or mocked USB4 helpers for software/hardware modes, lane selection, RX2 asymmetry, Gen4 eye selection, CL disable/enable restoration, interrupted runs, result clearing, and unsupported capability combinations. Static analysis should flag the sideband size-check bug and any unchecked debugfs lookup references.
