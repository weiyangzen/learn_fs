# sources/distributed-fs/ceph-client/drivers/edac/loongson_edac.c Research

## Purpose
`loongson_edac.c` is a compact ACPI/platform EDAC driver for a Loongson memory controller. It maps one MMIO resource, reads a cumulative corrected-error counter across chip-select fields, computes deltas between polls, and reports corrected errors to the EDAC core.

## Important APIs, Types, and Functions
`struct loongson_edac_pvt` stores the mapped ECC base and the last observed corrected-error count. `read_ecc()` reads `ECC_CS_COUNT_REG` with `readq()`, sums four 8-bit chip-select count fields, and returns the total. `edac_check()` reads the current total, subtracts `last_ce_count`, updates the baseline, and reports a corrected event count when the delta is positive. `dimm_config_init()` creates a single channel/slot DIMM entry with placeholder full-size pages, label, and grain. `pvt_init()` stores MMIO base and initializes the baseline counter.

`edac_probe()` maps the platform resource through `devm_platform_ioremap_resource()`, allocates a two-layer one-channel/one-slot EDAC topology, fills controller metadata, installs `edac_check`, initializes private and DIMM state, registers the MC, and forces polling mode. `edac_remove()` unregisters and frees the MC.

## Control Flow
The module uses `module_platform_driver()`. ACPI ID `LOON0010` binds the driver. Probe allocates and registers one EDAC controller per platform device. EDAC polling invokes `edac_check()` to turn monotonically increasing hardware counters into event deltas. Remove deletes the EDAC MC by platform device and frees it.

## State and Persistence
The hardware counter cannot be zeroed, so the driver's only persistent runtime state is `last_ce_count`, held in memory. The MMIO mapping is devm-managed. No filesystem state exists.

## Dependencies and Integration Points
The driver depends on ACPI platform enumeration, platform resource mapping, EDAC MC APIs, `io-64-nonatomic-lo-hi`, and Loongson-specific counter layout. It integrates only with EDAC polling, not interrupts or MCE notifiers.

## Risks and Edge Cases
Counter wraparound is not handled: if the summed 8-bit fields wrap, the delta becomes negative and the event is skipped. DIMM size/type data is placeholder rather than decoded from hardware. Only corrected errors are reported; uncorrected/fatal paths are absent. The summed counter loses chip-select attribution.

## Test Signals
Signals include ACPI binding to `LOON0010`, successful resource mapping, initial baseline preventing stale count reports, corrected-error delta reports under polling, no report when counts do not increase, behavior across counter wrap, and clean EDAC unregister on platform removal.
