# sources/distributed-fs/ceph-client/drivers/edac/armada_xp_edac.c

## Purpose
This file implements EDAC support for Marvell Armada XP-class hardware. It registers two platform drivers: one `mem_ctl_info` memory-controller driver for the Armada XP SDRAM controller and one `edac_device_ctl_info` driver for the Aurora L2/system-cache controller. The memory side reports SDRAM single-bit and double-bit ECC events; the L2 side reports cache correctable and uncorrectable/tag-parity events, with optional debugfs-based injection controls under `CONFIG_EDAC_DEBUG`.

## Important APIs, Types, And Functions
The memory-controller private state is `struct axp_mc_drvdata`, which stores the MMIO base, detected bus width, chip-select address-interleaving flags, and a fixed diagnostic message buffer. The L2 private state is `struct aurora_l2_drvdata`, which stores MMIO base, a message buffer, optional injection fields, and a debugfs dentry.

Key functions are `axp_mc_probe()`, `axp_mc_remove()`, `axp_mc_read_config()`, `axp_mc_check()`, and `axp_mc_calc_address()` for SDRAM EDAC. `aurora_l2_probe()`, `aurora_l2_remove()`, `aurora_l2_poll()`, `aurora_l2_check()`, and `aurora_l2_inject()` cover the cache EDAC path. Module initialization uses `platform_register_drivers()` after rejecting coexistence with GHES via `ghes_get_devices()`.

## Control Flow
`armada_xp_edac_init()` forces polling mode, registers both platform drivers, and exits early with `-EBUSY` if GHES owns error reporting. `axp_mc_probe()` maps SDRAM registers, verifies ECC is enabled, allocates a one-layer chip-select EDAC topology, fills `mci` metadata, reads chip-select/DIMM configuration, programs an SBE threshold, clears stale status/counters, and calls `edac_mc_add_mc()`. During polling, `axp_mc_check()` snapshots the error data, ECC, address, count, and cause registers; clears cause and count state; reports aggregate earlier errors without location; then decodes the most recent error into chip-select/bank/row/column, computes a PFN/offset, and reports CE or UE through `edac_mc_handle_error()`.

For Aurora L2, `aurora_l2_probe()` maps registers, warns if parity/ECC are not enabled, allocates an EDAC device with one `cpu` instance and two `L` blocks, clears counters/capture registers, adds the EDAC device, and optionally exposes injection registers in debugfs. `aurora_l2_poll()` calls `aurora_l2_check()` and then performs debug injection if configured. `aurora_l2_check()` reads counter/capture registers, clears counters, decodes source/transaction/error/address/index/way, emits either `edac_device_handle_ce()` or `edac_device_handle_ue()`, clears capture validity, and reports any remaining count as detail-less events.

## State And Persistence
Persistent runtime state lives in hardware registers and in EDAC core structures. Driver-private state caches bus width and chip-select interleaving because those values are needed to reconstruct addresses during later polling. Error counters are cleared after each poll to prevent duplicate reports. The L2 injection fields persist only while the device is bound and, under debug builds, are user-modifiable through debugfs.

## Dependencies And Integration Points
The driver depends on platform/OF matching (`marvell,armada-xp-sdram-controller` and `marvell,aurora-system-cache`), `devm_platform_ioremap_resource()`, Aurora/L2X0 register definitions, EDAC MC APIs, EDAC device APIs, EDAC module globals, and debugfs wrappers. It integrates with `/sys/devices/system/edac/mc` through `edac_mc_add_mc()` and with generic EDAC device sysfs through `edac_device_add_device()`.

## Risks
Address reconstruction is hardware-specific and sensitive to bus width and interleaving bits; incorrect width adjustments for Armada 380 and 98dx3236 would misattribute errors. The L2 `clear_remaining` loop reports remaining CE counts with `edac_device_handle_ue()` in the final loop, which is worth review because it appears to classify detail-less CEs as UEs. Error messages are assembled into fixed buffers; the code sizes them conservatively but relies on careful formatting. Polling clears hardware status, so races with other firmware or error handlers would lose events, hence the GHES exclusion.

## Test Signals
Useful signals include successful platform binding, EDAC sysfs nodes for `mc0` and the L2 `cpu` device, correct DIMM sizes from `axp_mc_read_config()`, no stale events after probe clears counters, and injected Aurora L2 events under `CONFIG_EDAC_DEBUG`. Hardware tests should cover SBE/DBE count handling, multiple-error aggregation, chip-select mapping, and L2 capture-register valid/invalid paths.
