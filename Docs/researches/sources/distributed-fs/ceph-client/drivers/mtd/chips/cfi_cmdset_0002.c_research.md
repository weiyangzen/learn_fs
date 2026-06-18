# sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_cmdset_0002.c

## Purpose

`cfi_cmdset_0002.c` implements the MTD NOR flash command-set driver for CFI command set 0002, the AMD/Fujitsu/Spansion standard command set, with aliases for command sets 0006 and 0701. It provides MTD read, word write, write-buffer write, erase, panic write, OTP/SecSi access, lock support for selected protection schemes, power management, and reset handling for AMD-style command sequences.

## Important APIs, Types, and Functions

The exported entry points are `cfi_cmdset_0002`, `cfi_cmdset_0006`, and `cfi_cmdset_0701`. `cfi_amdstd_chipdrv` registers the driver name and destroy method. The command-set setup path is `cfi_cmdset_0002` followed by `cfi_amdstd_setup`.

Operational callbacks installed in `mtd_info` include `_read`, `_write`, `_erase`, `_sync`, `_suspend`, `_resume`, `_panic_write`, OTP info/read/write/lock callbacks, and optionally `_lock`, `_unlock`, and `_is_locked` for Atmel or PPB protection schemes. Important helpers include `chip_ready`, `chip_good`, `cfi_check_err_status`, `get_chip`, `put_chip`, `do_read_onechip`, `do_write_oneword`, `do_write_buffer`, `cfi_amdstd_panic_write`, `do_erase_chip`, `do_erase_oneblock`, `do_atmel_lock`, `do_ppb_xxlock`, and `cfi_amdstd_otp_walk`.

## Control Flow

Binding allocates `mtd_info`, installs default operations, reads the AMD/Fujitsu extended query table for CFI-mode devices, validates versions 1.0 through 1.5, stores it as `cmdset_priv`, applies fixups, configures optional advanced sector protection from the device tree property `use-advanced-sector-protection`, normalizes boot-block region order, and sets default unlock addresses. If no PRI exists, no-PRI SST fixups can still provide geometry and unlock details. JEDEC mode applies FWH lock fixups for selected SST devices.

`cfi_amdstd_setup` computes total size and erase regions from CFI geometry, validates the sum against chip size, registers the reboot notifier, and returns the ready `mtd_info`. Unlike the Intel driver, this file does not allocate per-region lock maps by default.

Read operations reset to AMD array mode with `0xf0` when needed and copy from map memory. Word writes use the AMD unlock sequence `AA`/`55`/`A0`, skip no-op writes where the old word already equals the new word, retry failures up to `MAX_RETRIES`, and use toggle-bit or status-register polling depending on CFI software features. Write-buffer operations use `AA`/`55`, buffer load `0x25`, word count, data, confirm `0x29`, and a dedicated wait/reset sequence. Erase operations use the AMD erase unlock sequence ending in chip erase `0x10` or sector erase command, poll until ready or timeout, and retry failures.

## State and Persistence Behavior

Hardware persistence includes flash contents, erased sectors, SecSi/OTP contents, OTP lock register bits, Atmel locks, and PPB sector protection bits. Runtime state lives in `cfi_private`, `flchip`, and `mtd_info`. `flchip->state`, `oldstate`, waitqueues, suspend flags, and in-progress block fields serialize operations and allow erase suspend for reads/points and, on capable chips, writes.

The panic write path deliberately bypasses normal locking because it is intended for `mtdoops` during kernel panic. It repeatedly resets and polls the chip, then writes words with the same AMD command sequence to maximize odds of preserving panic logs.

## Dependencies and Integration Points

The driver depends on MTD CFI/map infrastructure, reboot notifiers, optional Open Firmware device-tree data, and XIP support. It integrates with generic CFI and JEDEC probes through exported command-set symbols and with MTD users through standard `mtd_info` callbacks. It uses `fwh_lock.h` for firmware-hub locking on selected SST devices. OTP/SecSi hooks are exposed through the MTD protection-register API.

## Risks and Edge Cases

The AMD-style status model is subtle: some chips use DQ polling while newer devices advertise status-register polling, and `CFI_QUIRK_DQ_TRUE_DATA` changes expected-data checks. Incorrect CFI boot-block data is common enough that the file has extensive boot-location and sector-count fixups for AMD, AMIC, Macronix, SST, Samsung, and Spansion parts. M29EW devices need dummy-cycle and resume-delay workarounds around erase suspend.

Write-buffer mode notes that interleaved mode is not tested and probably unsupported. PPB unlock is especially risky because the hardware unlock command unlocks all sectors on the chip; the driver snapshots other sector lock states and relocks them, but failures in the middle can temporarily expose sectors. OTP writes and locks are irreversible. Panic writes trade synchronization safety for crash-time logging.

## Test Signals

Build signals include `CONFIG_MTD_CFI_AMDSTD`, optional XIP, and platform/device-tree PPB configuration. Hardware tests should cover CFI and JEDEC binding, top/bottom boot-region swapping, SST no-PRI fixups, normal reads, unaligned and aligned word writes, write-buffer writes across boundaries, chip erase versus sector erase, erase suspend/resume, status-register polling devices, panic write on a disposable partition, Atmel and PPB lock/unlock/is_locked paths, OTP/SecSi read/write/lock where safe, suspend/resume, and reboot reset to array mode. MTD test modules can validate erase/read/write behavior on sacrificial devices.
