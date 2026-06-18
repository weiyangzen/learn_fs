# sources/distributed-fs/ceph-client/drivers/edac/bluefield_edac.c

## Purpose
This file implements the Mellanox/NVIDIA BlueField memory EDAC driver. It monitors the External Memory Interface ECC counters, reports single-bit and double-bit ECC events, and initializes DIMM metadata using BlueField SiP SMC calls and ACPI-provided platform properties.

## Important APIs, Types, And Functions
`struct bluefield_edac_priv` holds the parent device, DIMM rank counts, EMI register base, DIMMs-per-controller count, secure-register support state, and secure register table number. `smc_call1()` retrieves DIMM information. `secure_readl()` and `secure_writel()` access secure registers via Arm SMCCC when ACPI provides a `sec_reg_block`; otherwise `bluefield_edac_readl()` and `bluefield_edac_writel()` use direct MMIO.

Key flows are `bluefield_edac_mc_probe()`, `bluefield_edac_mc_remove()`, `bluefield_edac_init_dimms()`, `bluefield_edac_check()`, and `bluefield_gather_report_ecc()`. The ACPI match ID is `MLNXBF08`.

## Control Flow
Probe reads ACPI properties `mss_number` and `dimm_per_mc`, validates the DIMM count, gets the EMI memory resource, allocates a slot-layer EDAC topology, determines whether direct MMIO or secure SMC register access is required, maps or stores the EMI base, fills `mci` metadata, initializes DIMMs by calling `MLXBF_SIP_GET_DIMM_INFO`, registers with EDAC, and selects polling mode. During polling, `bluefield_edac_check()` reads ECC counters, extracts single and double counts, calls `bluefield_gather_report_ecc()` for each nonzero class, then writes `MLXBF_ECC_ERR` bits to clear reported errors.

`bluefield_gather_report_ecc()` starts a latch operation, reads syndrome bits, verifies that the latched type matches the requested CE/UE type, reads rank/additional information and 64-bit error address, chooses a DIMM based on physical rank and stored rank count, and reports to EDAC with PFN, offset, syndrome, and layer coordinates.

## State And Persistence
Hardware ECC counters and latched error information are consumed during polling and cleared after reporting. DIMM population, page counts, type, width, and rank counts are stored in EDAC `dimm_info` structures and the driver's private rank array. If all DIMMs are empty, `mci->edac_cap` is set to `EDAC_FLAG_NONE`, causing later checks to return early.

## Dependencies And Integration Points
The driver depends on ACPI platform devices, device properties, Arm SMCCC, BlueField SiP services, EDAC MC APIs, bitfield helpers, and MMIO mapping. It integrates with EDAC sysfs through `edac_mc_add_mc()` and with firmware-provided DIMM inventory and secure-register policy.

## Risks
SMC service version or access violations make secure-register systems fail probe or skip reports. DIMM selection from physical rank is heuristic and depends on `dimm_ranks[0]`. If the latch returns a different error type than requested, the driver reports only aggregate count without location. Because it is polling-based, delayed polling can collapse multiple events into one count with only one detailed address.

## Test Signals
Important signals include ACPI property validation, both direct-MMIO and secure-SMC access paths, empty-DIMM behavior, ECC counter clearing, correct PFN/offset formation from two address registers, and CE/UE sysfs counter updates. Firmware test coverage should include missing/old SiP service versions and access-denied secure register calls.
