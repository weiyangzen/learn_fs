# sources/distributed-fs/ceph-client/drivers/edac/pasemi_edac.c

## Purpose
Implements EDAC memory-controller support for PA Semi PWRficient on-chip memory controllers. It probes the controller via PCI, enables ECC error logging/correction bits, builds csrow/channel DIMM geometry, polls error status, and reports SBE/MBE/rank-fail events.

## Important APIs, Types, And Functions
- `pasemi_edac_get_error_info` reads and clears `MCDEBUG_ERRSTA`, and clears SBE overflow through `MCDEBUG_ERRCNT1`.
- `pasemi_edac_process_error_info` reads `MCDEBUG_ERRLOG1A`, extracts chip-select, and reports CE or UE through EDAC.
- `pasemi_edac_check` is the polling callback.
- `pasemi_edac_init_csrows` reads rank configuration registers and fills EDAC csrow/dimm metadata.
- `pasemi_edac_probe` enables logging/correction, allocates `mem_ctl_info`, computes capabilities, initializes rows, clears old status, and registers the MC.

## Control Flow
PCI probe first verifies `MCCFG_MCEN_MMC_EN`. It enables SBE, MBE, and rank-fail logging, creates a two-layer chip-select/channel EDAC topology, reads ECC correction and scrub configuration, fills EDAC capability fields, and initializes present rank sizes from `MCDRAM_RANKCFG`. After clearing stale status, it adds the MC to the EDAC core. Periodic checks read pending status, clear it, decode the chip-select from the error log, and report UE for MBE/rank-fail and CE for SBE.

## State And Persistence
`last_page_in_mmc` and `system_mmc_id` are global counters used while probing controllers. Per-controller state is held in the EDAC MC object; there is no custom private data. Hardware logging/correction/scrub bits persist in PCI config space and are not restored by remove.

## Dependencies And Integration Points
Depends on PCI config access, PA Semi PCI IDs, EDAC MC APIs, and EDAC polling/NMI opstate initialization. It registers as a `pci_driver` for vendor PA Semi device `0xa00a`.

## Risks And Edge Cases
`last_page_in_mmc` is global and monotonically accumulates across controllers, so remove/reprobe or unusual multi-controller ordering can affect page ranges. The driver enables ECC correction/logging without saving previous register state. Only one channel per csrow is modeled. Unknown rank sizes abort probe, and error reporting uses the first page of the chip-select rather than precise captured address data.

## Test Signals
Probe with controller disabled/enabled, each rank size encoding, SECDED versus EC capability bits, scrub flag combinations, SBE overflow clearing, MBE and rank-fail UE reporting, and remove after failed or successful EDAC registration.
