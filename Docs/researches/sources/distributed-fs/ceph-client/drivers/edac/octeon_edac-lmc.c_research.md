# sources/distributed-fs/ceph-client/drivers/edac/octeon_edac-lmc.c

## Purpose
Provides EDAC memory-controller support for Cavium Octeon LMC DRAM controllers. It polls controller ECC status, reports DIMM/rank/bank/row/column information, and exposes sysfs injection controls for software-driven decode/reporting tests.

## Important APIs, Types, And Functions
- `struct octeon_lmc_pvt` stores injection state and synthetic DIMM address fields.
- `octeon_lmc_edac_poll` handles Octeon I `MEM_CFG0` SEC/DED status and `FADR` capture.
- `octeon_lmc_edac_poll_o2` handles Octeon II `LMCX_INT`, supports synthetic injection, and clears or resets status.
- `TEMPLATE_SHOW` and `TEMPLATE_STORE` generate sysfs controls for injection and address fields.
- `octeon_lmc_edac_probe` checks ECC enablement, allocates the EDAC MC, registers sysfs groups, and disables hardware ECC interrupts because polling is used.

## Control Flow
Probe calls `opstate_init`, builds a one-channel EDAC topology, and branches by Octeon generation. If ECC is disabled, it logs and returns success without registering EDAC. Otherwise it allocates `mem_ctl_info` with private injection state, fills names, chooses the poll function, registers with `edac_mc_add_mc_with_groups`, disables hardware SEC/DED interrupts, and saves the MCI in platform data. The poll path reads hardware or synthetic status, builds an address message from `FADR` fields or sysfs-provided values, reports CE/UE, then clears the hardware interrupt bits or resets `pvt->inject`.

## State And Persistence
Persistent state includes the EDAC MC object and `octeon_lmc_pvt` injection fields. Hardware capture/status registers persist until the poll function writes them back with re-arm bits. Sysfs attribute values persist in memory only for the life of the EDAC MC.

## Dependencies And Integration Points
Depends on Octeon CSR definitions, EDAC MC APIs, generated device attribute groups, and platform devices named `octeon_lmc_edac`. It integrates with EDAC as a memory-controller driver with polling, not interrupts.

## Risks And Edge Cases
The Octeon II interrupt-disable block reads `CVMX_LMCX_MEM_CFG0` into a `union cvmx_lmcx_int_en`, which deserves hardware-layout scrutiny. Sysfs injection stores accept numeric strings only when the first byte is a digit and otherwise return zero. The driver reports unknown page/offset/syndrome and uses the decoded location in the message, so consumers relying on normalized EDAC coordinates get limited data.

## Test Signals
Check ECC-disabled platforms return without registering, Octeon I and II CE/UE polling paths, sysfs injection of single and double errors with selected DIMM/rank/bank/row/col, status clearing/re-arming, and EDAC MC teardown.
