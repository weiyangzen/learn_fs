# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_5_regs.h

## Purpose
`nif_rtr_ctrl_5_regs.h` is the generated Gaudi register-address header for `NIF_RTR_CTRL_5`, another instance of the Network Interface `RTR_CTRL` router-control block. It defines 437 `mmNIF_RTR_CTRL_5_*` register constants over `0x3D6108..0x3D6CBC`. The layout is the same as other NIF router-control instances after normalizing the controller number and base address.

The symbols cover controller-5 routing permissions, HBM/SRAM hashing polynomials, scrambler controls, rate-limit controls, E2E credit and counter controls, non-linear memory steering, secure/privileged route-range controls, RGL control state, and HBM performance-counter selectors.

## Important APIs, types, and functions
There are no runtime APIs, only generated macros:

- `mmNIF_RTR_CTRL_5_PERM_SEL` for permission selection.
- `mmNIF_RTR_CTRL_5_HBM_POLY_H3_0..27` and `mmNIF_RTR_CTRL_5_SRAM_POLY_H3_0..14` for distribution polynomial registers.
- `mmNIF_RTR_CTRL_5_SCRAM_SRAM_EN` and `mmNIF_RTR_CTRL_5_SCRAM_HBM_EN` for SRAM/HBM scrambler enablement.
- `mmNIF_RTR_CTRL_5_RL_HBM_*`, `RL_PCI_*`, and `RL_SRAM_*` for rate-limit state.
- `mmNIF_RTR_CTRL_5_E2E_*` for HBM/PCI E2E sizes, enables, counters, and wrap indicators.
- `mmNIF_RTR_CTRL_5_NL_*` for non-linear SRAM/HBM steering and performance counter selection.
- `mmNIF_RTR_CTRL_5_RANGE_SEC_*` and `mmNIF_RTR_CTRL_5_RANGE_PRIV_*` for secure/privileged range base/mask tables and hit status on AW/AR channels.
- `mmNIF_RTR_CTRL_5_RGL_*` for RGL configuration, latency, token, bank-id, and watchdog controls.

## Control flow
Consumer flow follows the same pattern as other NIF controller maps. In non-secure, driver-owned setup, `gaudi_init_scrambler_sram()` and `gaudi_init_scrambler_hbm()` write controller-5 scrambler enable registers. `gaudi_init_e2e()` programs controller-5 with minimal HBM and PCI credit sizes: HBM write `1`, HBM read `1`, PCI write `1`, and PCI read `32`, then enables HBM and PCI E2E.

The security code lists controller-5 secure range and hit registers in high-bandwidth route-range arrays. A shared setup path can then configure or inspect controller 5 without special-case code.

## State and persistence
All named values are hardware register locations. Written configuration persists until reset or later writes. Counters and hit-status registers reflect current hardware activity and should be considered volatile. The header has no storage, initialization, or teardown of its own.

Driver state outside this file controls whether the registers are written: firmware security and boot-status bits can cause the Linux driver to skip direct programming, while `hw_cap_initialized` prevents duplicate scrambler initialization.

## Dependencies and integration points
The file is included by `gaudi_regs.h` and consumed primarily by `gaudi.c` and `gaudi_security.c`. Correct use depends on generated mask/shift headers, Gaudi register accessors, firmware boot-status contracts, and the broader security/protection infrastructure that maps all high-bandwidth route-range registers into ordered arrays.

## Risks and edge cases
- Controller 5 shares the minimal E2E profile with controller 2, so blanket copying from adjacent controller 4 or 6 would be wrong.
- The range-register surface is large and repetitive; mistakes can compile while compromising security behavior.
- Hardware counter and hit semantics must be checked before using values for persistent diagnostics.
- Firmware-owned setup paths mean tests that only cover non-secure boot may miss integration issues.
- Manual edits should not be made to this generated register map.

## Test signals
Look for clean probe/reset logs, correct behavior of non-secure scrambler/E2E initialization, stable NIC traffic through controller 5, and expected protection behavior when AW/AR ranges are intentionally violated. Static validation should confirm the `0x3D6xxx` address window, 437 symbol count, and normalized equality with other NIF router-control headers.
