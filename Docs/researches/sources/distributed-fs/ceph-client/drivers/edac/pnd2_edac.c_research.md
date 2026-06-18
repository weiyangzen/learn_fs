# sources/distributed-fs/ceph-client/drivers/edac/pnd2_edac.c

## Purpose
Implements EDAC support for Intel Atom SoCs using the Pondicherry2 memory controller, covering Apollo Lake and Denverton. It decodes machine-check memory errors from system physical addresses into channel, DIMM, rank, bank, row, and column by reading memory-controller topology registers and registering an MCE decode notifier.

## Important APIs, Types, And Functions
- `struct dunit_ops` abstracts Apollo Lake versus Denverton register access, ECC checks, DIMM discovery, and PMI-to-DRAM decode.
- `_apl_rd_reg`, `apl_rd_reg`, and `dnv_rd_reg` read controller registers through hidden P2SB sideband or MMIO/config-space paths.
- `get_registers` reads static memory layout registers and derives asymmetric, symmetric, MOT, slice, channel, and hash state.
- `sys2pmi` performs first-stage system-address to PMI channel/address translation, including MMIO gap removal and interleave bit removal.
- `apl_pmi2mem` and `dnv_pmi2mem` perform second-stage PMI address to DRAM location decode.
- `pnd2_mce_check_error` filters MCEs, and `pnd2_mce_output_error` reports decoded events through EDAC.
- `pnd2_register_mci`, `pnd2_init`, and `pnd2_exit` manage EDAC MC and MCE notifier lifetime.

## Control Flow
Initialization rejects GHES ownership, other EDAC owners, hypervisors, and unsupported CPU models. It selects `apl_ops` or `dnv_ops`, initializes opstate, reads topology registers, checks ECC is active, registers one EDAC MC, registers the MCE decode notifier, and optionally creates debugfs decode-test files. On an MCE, the notifier ignores already handled and non-memory errors, logs raw machine-check metadata, then calls the output routine. The output routine classifies corrected/uncorrected/fatal status, requires a valid address, calls `get_memory_error_data`, and reports the decoded channel/DIMM/rank/row/bank/column or a decode failure message.

## State And Persistence
The driver uses substantial file-scope topology state: TOLUD/TOUUD-derived `top_lm`/`top_hm`, region descriptors `mot`, `as0`, `as1`, `as2`, channel masks, selectors, hash masks, and cached Apollo Lake/Denverton register structures. `pnd2_mci` is the active EDAC controller. Debugfs state stores a fake address and last decode result. Hardware topology is read once at probe and assumed stable.

## Dependencies And Integration Points
Depends on x86 CPU matching, MCE notifier chain, EDAC MC APIs, GHES/EDAC ownership arbitration, PCI config access, P2SB sideband helpers, MMIO mapping, and register bitfield definitions from `pnd2_edac.h`. It integrates with the kernel MCE path by marking handled memory errors with `MCE_HANDLED_EDAC`.

## Risks And Edge Cases
Address decode is sensitive to firmware-provided interleave registers, MOT masks, asymmetric regions, hash masks, and DIMM geometry tables. Apollo Lake P2SB access temporarily unhides a hidden PCI device and must restore hide state. Register and topology state is global, so multiple controllers are not modeled. Debugfs decode calls the normal output path with synthetic MCE fields. Error classification ignores MCEs without `ADDRV`; decode failures still emit EDAC events with unknown coordinates.

## Test Signals
Test Apollo Lake and Denverton CPU matches, GHES/owner/hypervisor rejection, P2SB busy and timeout paths, invalid MOT mask/base validation, addresses in MMIO gaps and above TOHM, symmetric/asymmetric/MOT interleaves, APL and DNV DIMM geometries, ECC-disabled channels, MCE filtering, debugfs fake-address decode, and notifier unregister on exit.
