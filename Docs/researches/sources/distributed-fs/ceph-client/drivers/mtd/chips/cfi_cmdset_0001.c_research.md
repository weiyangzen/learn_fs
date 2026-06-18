# sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_cmdset_0001.c

## Purpose

`cfi_cmdset_0001.c` implements the MTD NOR flash command-set driver for CFI command set 0001, the Intel/Sharp extended command set, with aliases for command sets 0003 and 0200. It turns probed CFI/Jedec map data into an `mtd_info`, supplies read/write/erase/lock/OTP/suspend/resume/reset operations, handles Intel/Sharp-specific status polling and suspend behavior, and applies many vendor/device fixups.

## Important APIs, Types, and Functions

The exported entry points are `cfi_cmdset_0001`, `cfi_cmdset_0003`, and `cfi_cmdset_0200`, all registered with `EXPORT_SYMBOL_GPL`. `cfi_intelext_chipdrv` names the chip driver and points destruction to `cfi_intelext_destroy`.

Setup is split between `read_pri_intelext`, `cfi_cmdset_0001`, `cfi_intelext_setup`, and `cfi_intelext_partition_fixup`. Fixups include Atmel PRI conversion, FWH lock support, ST buffer-write corrections, Sharp LH28F640BF partition reset, point support for linear maps, write-buffer enablement, and power-up lock handling.

Operational methods installed into `mtd_info` include `_read`, `_write`, `_writev`, `_erase`, `_sync`, `_lock`, `_unlock`, `_is_locked`, `_suspend`, `_resume`, and optional OTP hooks under `CONFIG_MTD_OTP`. Core helpers are `get_chip`, `chip_ready`, `put_chip`, `do_read_onechip`, `do_write_oneword`, `do_write_buffer`, `do_erase_oneblock`, `do_xxlock_oneblock`, and `cfi_intelext_otp_walk`.

## Control Flow

Binding starts when generic CFI code calls `cfi_cmdset_0001(map, primary)`. The driver allocates `mtd_info`, installs default operations, reads the Intel/Sharp primary query extension for real CFI devices, validates versions 1.0 through 1.5, endian-swaps feature fields and OTP/partition extension data, applies CFI/Jedec/generic fixups, initializes per-chip write/erase timeout fields and waitqueues, sets `map->fldrv`, and calls `cfi_intelext_setup`.

`cfi_intelext_setup` computes total MTD size and erase regions from CFI geometry, allocates per-region lock maps, installs OTP callbacks when enabled, optionally rewrites the CFI chip model for hardware partitions, takes a module reference, and registers a reboot notifier. Hardware partition fixup can replace one physical `cfi_private` with virtual `flchip` entries sharing `flchip_shared` arbitration state.

Read and point operations acquire chips with `get_chip` in `FL_READY` or `FL_POINT`, switch to array mode with command `0xff` when necessary, copy from the map, and release with `put_chip`. Write paths handle unaligned bytes by constructing partial `map_word` values, then issue Intel word program (`0x40` or performance `0x41`) or write-buffer program (`0xe8`/`0xe9`, count, data, `0xd0`). Erase issues clear status (`0x50`), block erase (`0x20`, `0xd0`), waits, reads status, retries selected failures, and maps protection/VPP/status failures to Linux errors.

## State and Persistence Behavior

Persistent hardware state includes programmed flash contents, erased blocks, block lock bits, and OTP protection registers. Runtime state is held in `cfi_private`, `flchip`, `flchip_shared`, `mtd_erase_region_info.lockmap`, and the `mtd_info` callbacks. `flchip->state` tracks modes such as `FL_READY`, `FL_STATUS`, `FL_ERASING`, `FL_WRITING`, `FL_POINT`, `FL_PM_SUSPENDED`, and `FL_SHUTDOWN`; `oldstate`, suspend flags, and in-progress block fields allow erase/write suspend and resume.

For chips flagged `MTD_POWERUP_LOCK`, suspend saves lock state into per-region bitmaps and resume unlocks blocks that were previously unlocked, compensating for chips that power up locked. Reboot and destroy reset all chips to read-array mode so firmware can execute from flash after soft reboot.

## Dependencies and Integration Points

The driver depends on MTD map, CFI, XIP, reboot notifier, bitmap, and waitqueue/mutex infrastructure. It consumes CFI probe data from `map->fldrv_priv`, uses map callbacks for command writes and memory copies, and exposes standard MTD operations to filesystems, UBI, block facades, and user tools. `fwh_lock.h` supplies firmware-hub lock fixups. `CONFIG_MTD_XIP` changes wait behavior to suspend flash operations around pending interrupts while code executes from flash.

## Risks and Edge Cases

This file is a dense hardware state machine. Major risks are incorrect CFI tables, erase-region sums not matching device size, mishandled hardware partitions, suspend interactions across shared partitions, and chips that report support for features with errata. The code contains explicit workarounds for buggy Micron/Numonyx erase suspend on small blocks, Sharp partition registers, Atmel PRI layout, and power-up lock behavior.

Write-buffer programming must not cross write-buffer boundaries and must clear status bits before starting. OTP writes and locks are irreversible. XIP paths disable interrupts and require `__xipram`-safe code; mistakes can deadlock systems executing from flash. Lock/unlock commands may take up to 1.5 seconds on older Intel flashes.

## Test Signals

Build signals include `CONFIG_MTD_CFI_INTELEXT`, optional `CONFIG_MTD_OTP`, and optional `CONFIG_MTD_XIP`. Hardware validation should cover CFI and JEDEC probe binding, erase-region layout, linear-map point/unpoint reference counts, word and buffer writes including unaligned boundaries, erase suspend while reading/writing another block, block lock/unlock/is_locked, suspend/resume preserving lock state, OTP read/write/lock on expendable parts, reboot reset to array mode, and failure injection for VPP/protection/status timeout paths. MTD test modules can exercise read/write/erase behavior but must be used only on disposable flash.
