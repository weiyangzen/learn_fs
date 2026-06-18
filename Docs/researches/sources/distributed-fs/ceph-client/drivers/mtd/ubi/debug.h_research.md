# sources/distributed-fs/ceph-client/drivers/mtd/ubi/debug.h

## Purpose
`debug.h` defines UBI assertion/logging macros, dump/debugfs prototypes, legacy random failure helpers, fault-injection masks, and inline predicates consumed throughout UBI.

## Important APIs, Types, And Functions
The header exports dump and debugfs prototypes implemented in `debug.c`, `ubi_self_check_all_ff()`, and `ubi_dbg_power_cut()`. It defines `ubi_assert()`, `ubi_dbg_msg()`, subsystem logging macros (`dbg_gen`, `dbg_eba`, `dbg_wl`, `dbg_io`, `dbg_bld`), and `ubi_dbg_print_hex_dump()`. Fault masks include power-cut at EC/VID/data writes, bitflips, ECC errors, read/write/erase failures, all-FF header reads, all-FF-with-bitflips, bad header, and bad-header-with-ECC variants. Inline checks include `ubi_dbg_is_power_cut()`, `ubi_dbg_is_bitflip()`, `ubi_dbg_is_write_failure()`, `ubi_dbg_is_erase_failure()`, `ubi_dbg_is_eccerr()`, `ubi_dbg_is_read_failure()`, `ubi_dbg_is_ff()`, `ubi_dbg_is_ff_bitflips()`, `ubi_dbg_is_bad_hdr()`, `ubi_dbg_is_bad_hdr_ebadmsg()`, `ubi_dbg_is_bgt_disabled()`, `ubi_dbg_chk_io()`, `ubi_dbg_chk_gen()`, `ubi_dbg_chk_fastmap()`, and `ubi_enable_dbg_chk_fastmap()`.

## Control Flow
Callers use the `ubi_dbg_is_*()` predicates in hot paths. Each predicate first checks legacy random/debugfs controls where applicable, then consults the structured Linux fault-injection path when `CONFIG_MTD_UBI_FAULT_INJECTION` is enabled. Without that config, the structured `ubi_dbg_fail_*()` macros compile to `false`, keeping production overhead low. Fastmap debug checking is a direct flag in `ubi->dbg`.

## State And Persistence
The header itself stores no state, but it standardizes access to `ubi->dbg` fields that are mutable through debugfs. These controls do not persist across module/device lifetime, but they influence persistent media operations during tests by injecting failures into writes, erases, reads, and fastmap checks.

## Dependencies And Integration Points
It depends on Linux random helpers and UBI core/media types being visible through including code. It is included broadly by UBI internals through `ubi.h`, making its inline behavior part of I/O, WL, EBA, attach, and fastmap semantics. The fault-injection externs are defined in `debug.c`.

## Risks
Because these are inline predicates, semantic changes affect many subsystems at once. `ubi_assert()` logs and dumps a stack but does not halt execution, so callers must not rely on it as runtime validation. Legacy random failure probabilities are fixed, which can make tests nondeterministic unless debugfs controls are managed carefully. Fault masks share a single bitfield, so tests should avoid ambiguous combinations unless specifically validating compound failures.

## Test Signals
Compile both with and without `CONFIG_MTD_UBI_FAULT_INJECTION`, verify no unresolved `should_fail_*` references in non-injection builds, confirm masks invoke the intended fault attributes, check fastmap debug enablement through `fm_debug`, and ensure assertion/log macros produce useful subsystem tags.
