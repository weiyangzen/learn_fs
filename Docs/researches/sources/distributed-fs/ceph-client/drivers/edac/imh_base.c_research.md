# sources/distributed-fs/ceph-client/drivers/edac/imh_base.c Research

## Purpose
`imh_base.c` is the EDAC base driver for Intel server processors with Integrated Memory/IO Hub-based memory controllers, currently matching Diamond Rapids. It discovers per-package IMH MMIO bases through local package views, enumerates DDR memory-controller units on north/south IMHs, registers them through shared `skx_common` helpers, and wires MCE decode into the SKX-family EDAC reporting path.

## Important APIs, Types, and Functions
`struct local_reg` describes a register in a package-local MMIO view. `read_local_reg()` finds an online CPU in the target package, maps the local physical base, and uses `smp_call_function_single()` to read the register from that package's view. `DEFINE_LOCAL_REG()` constructs these descriptors from the large `struct res_config` layout shared with `skx_common`.

Discovery starts with `imh_get_tolm_tohm()`, `imh_get_imc_num()`, and `imh_get_all_mmio_base_h()`. `__get_ddr_munits()` maps each present DDR IMC's channel MMIO, creates a device object for EDAC identity, and programs physical-to-logical MC mapping with `skx_set_mc_mapping()`. `imh_get_munits()` sets channel/dimm counts and global MC indexes. `imh_get_dimm_config()` reads MCMTR and DIMMMTR registers per channel/DIMM, delegates sizing to `skx_get_dimm_info()`, and rejects populated channels without ECC enabled. `imh_register_mci()` registers each IMC via `skx_register_mci()`.

The `dmr_cfg` resource configuration specifies Diamond Rapids DDR5 parameters, local MMIO bases/sizes, register offsets/widths for Ubox, PCU, SCA, and HA blocks, and channel/DIMM layout. The module uses `skx_mce_check_error` as its MCE notifier callback.

## Control Flow
Module init rejects GHES ownership, other EDAC owners, hypervisors, and non-matching CPUs. It installs the resource config, reads TOLM/TOHM into SKX shared state, discovers present IMCs and MMIO bases, maps memory units, checks 2-level memory mode through HA registers, registers MCs, obtains ADXL address decode support, initializes opstate, registers the MCE notifier, and sets up SKX debug support. Exit tears down debug, MCE notifier, ADXL, and all SKX-managed registrations/mappings.

## State and Persistence
Runtime state is mostly managed through shared `skx_common`: the EDAC list, SKX device/IMC structures, mappings, high/low memory limits, and debug state. This file also creates per-IMC `struct device` instances and MMIO mappings. No persistent storage exists.

## Dependencies and Integration Points
The driver depends heavily on `skx_common.h`/shared SKX EDAC helpers, x86 CPU matching, package topology, SMP cross-calls, IO mapping, x86 MCE notifiers, ADXL decode, GHES and EDAC owner arbitration.

## Risks and Edge Cases
Local-view register reads require at least one online CPU per target package; offline packages fail discovery. North IMH MMIO base is mandatory while south is optional. Allocation failure in `__get_ddr_munits()` after mapping can rely on later `skx_remove()` cleanup. Config register offsets must match hardware exactly. The driver skips virtualized environments, so test coverage requires bare-metal server hardware.

## Test Signals
Signals include CPU match on Diamond Rapids, correct local Ubox/PCU/SCA/HA reads per package, DDR IMC bitmap matching hardware, EDAC MC count and DIMM geometry matching populated DDR5, ECC-disabled rejection, 2LM detection, MCE decode through `skx_mce_check_error`, ADXL acquisition/release, and clean `skx_remove()` cleanup on failed init paths.
