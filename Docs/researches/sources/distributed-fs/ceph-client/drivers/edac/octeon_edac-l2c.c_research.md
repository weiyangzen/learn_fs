# sources/distributed-fs/ceph-client/drivers/edac/octeon_edac-l2c.c

## Purpose
Implements EDAC device support for Cavium Octeon secondary cache ECC. It polls Octeon I tag/data error CSRs and Octeon II per-TAD L2C tag/data/VBF error CSRs, reports CE/UE events, and clears handled hardware bits.

## Important APIs, Types, And Functions
- `octeon_l2c_poll_oct1` handles Octeon I `CVMX_L2T_ERR` and `CVMX_L2D_ERR`.
- `_octeon_l2c_poll_oct2` decodes one Octeon II TAD's `ERR_TDTX` and `ERR_TTGX` registers.
- `octeon_l2c_poll_oct2` iterates all EDAC instances/TADs.
- `octeon_l2c_probe` allocates the EDAC device, chooses the polling function by CPU model, disables Octeon I L2 interrupts, and registers with EDAC.

## Control Flow
The platform probe allocates an EDAC device with one or four TAD instances and two blocks, tag and data. On Octeon I, it disables single/double-error interrupt enable bits because the driver polls and assigns `octeon_l2c_poll_oct1`; otherwise it assigns the Octeon II polling function. Polling reads status registers, builds short diagnostic strings for syndrome/type/way, calls CE handlers for single-bit errors and UE handlers for double-bit errors, then writes a reset mask back to the CSR to re-arm only bits that were seen.

## State And Persistence
No custom private state is stored. EDAC control state persists in `edac_device_ctl_info`, and hardware error state lives in Octeon CSRs until cleared by the poll path. Remove deletes the EDAC device and frees the control info.

## Dependencies And Integration Points
Depends on Octeon model macros, CVMX CSR definitions, EDAC device APIs, and the platform driver named `octeon_l2c_edac`. It integrates as a polling EDAC device rather than an IRQ-driven driver.

## Risks And Edge Cases
The Octeon I path writes `l2d_err` back through `CVMX_L2T_ERR`, which is suspicious and should be checked against upstream or hardware expectations. Polling frequency determines detection latency. Octeon II diagnostic strings are fixed-size and could truncate details if fields grow. A failed `edac_device_add_device` returns `-ENXIO` after freeing state.

## Test Signals
Inject or emulate tag/data SEC/DED bits on Octeon I, TDTX/TTGX SBE/DBE/VBF bits on Octeon II, confirm only observed bits are cleared, verify TAD count on CN68XX, and unload/reload without EDAC device leaks.
