# sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/onenand_base.c

## Purpose
`onenand_base.c` is the generic MTD OneNAND core. It translates MTD read, write, erase, bad-block, lock, suspend/resume, panic write, and optional OTP operations into OneNAND register commands, and exposes `onenand_scan()` / `onenand_release()` for platform glue drivers. It also handles Flex-OneNAND address conversion, SLC/MLC boundary management, BufferRAM caching, OOB layout selection, ECC status interpretation, and bad block table integration.

## Important APIs, Types, and Functions
The exported entry points are `onenand_scan()`, `onenand_release()`, `onenand_addr()`, and `flexonenand_region()`. The core works through `struct onenand_chip` callbacks: `read_word`, `write_word`, `command`, `wait`, `bbt_wait`, `read_bufferram`, `write_bufferram`, `chip_probe`, `unlock_all`, `scan_bbt`, and `block_markbad`. Generic helpers include `onenand_command()`, `onenand_wait()`, `onenand_read_ops_nolock()`, `onenand_mlc_read_ops_nolock()`, `onenand_write_ops_nolock()`, `onenand_erase()`, `onenand_do_lock_cmd()`, and the OTP walker functions under `CONFIG_MTD_ONENAND_OTP`.

Key state lives in `struct onenand_chip`: register base, device/version IDs, geometry shifts, DDP density masks, Flex-OneNAND boundaries/diesizes, BufferRAM tags, page/OOB/verify buffers, lock/waitqueue state, ECC/feature option bits, and bad-block management. Module parameters `flex_bdry[]` and `otp` can alter Flex-OneNAND boundary programming and OTP lock behavior at load time.

## Control Flow
`onenand_scan()` fills missing callbacks with defaults, probes IDs with `onenand_probe()`, allocates buffers, initializes locks, selects an OOB layout by OOB size/Flex mode, wires MTD methods, unlocks blocks unless skipped, scans the BBT, and optionally applies requested Flex-OneNAND boundaries. Reads acquire the device with `onenand_get_device()`, use BufferRAM hits when possible, issue `ONENAND_CMD_READ` / `READOOB`, wait for completion, copy DataRAM/SpareRAM, and translate ECC stats into return codes. Writes enforce subpage alignment, fill DataRAM and SpareRAM, program pages, optionally cache-program, verify if configured, and invalidate BufferRAM on errors. Erase validates block alignment and bad blocks, then chooses block-by-block or multi-block erase plus verify. Lock/unlock issues either continuous-range or per-block commands depending on feature bits.

## State and Persistence
Persistent flash effects are page/OOB programming, block erasure, block lock state, OTP writes/locks, bad-block marker writes, and Flex-OneNAND PI boundary changes. Volatile kernel state includes BufferRAM cache tags, MTD ECC counters, allocated buffers, BBT RAM, current chip state, waitqueue/completion state, and feature flags. Flex-OneNAND boundary changes are especially persistent because `flexonenand_set_boundary()` erases/programs PI metadata after checking that converted blocks are erased.

## Dependencies and Integration Points
The file depends on the Linux MTD core, `linux/mtd/onenand.h`, `linux/mtd/partitions.h`, waitqueues, completions, IRQs, jiffies, and I/O accessors. Platform drivers integrate by pre-populating callbacks before calling `onenand_scan()`. Bad-block support integrates through `onenand_default_bbt()` and `onenand_bbt_read_oob()`. MTD clients use the installed `_read_oob`, `_write_oob`, `_erase`, `_sync`, `_lock`, `_unlock`, `_suspend`, `_resume`, `_block_isbad`, and `_block_markbad` methods.

## Risks
This code is hardware-stateful and sensitive to register ordering, BufferRAM selection, and DDP/Flex address translation. Alignment checks reject invalid writes, but partial-page paths still depend on correct subpage geometry. Multi-block erase must not cross DDP boundaries incorrectly. Flex boundary programming can corrupt data if erase-state checks are wrong. `onenand_get_device()` waits uninterruptibly, so stuck state transitions can hang callers. ECC accounting intentionally returns success for corrected data but may surface `-EBADMSG` after full-length reads. OTP lock behavior is controlled by a module parameter and is irreversible on real devices.

## Test Signals
Useful signals are successful `onenand_scan()` and `mtd_device_register()` in platform drivers, correct geometry/OOB layout logs, BBT scan results, ECC corrected/failed counters, lock/unlock status logs, erase verify failures, and boot tests across normal read/write/erase, OOB-only access, panic write, suspend/resume, DDP boundary access, and Flex-OneNAND boundary changes. Kconfig variants with `CONFIG_MTD_ONENAND_VERIFY_WRITE` and `CONFIG_MTD_ONENAND_OTP` should be compiled when touching those paths.
