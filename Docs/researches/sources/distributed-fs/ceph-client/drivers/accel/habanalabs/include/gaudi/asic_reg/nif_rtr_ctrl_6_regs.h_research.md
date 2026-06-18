# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_6_regs.h

## Purpose
`nif_rtr_ctrl_6_regs.h` is the generated Gaudi register-address header for `NIF_RTR_CTRL_6`, a Network Interface router-control block generated from the `RTR_CTRL` prototype. It defines 437 `mmNIF_RTR_CTRL_6_*` constants in the address range `0x3E6108..0x3E6CBC`. The symbol layout matches the other NIF router-control blocks with a controller-specific address base.

The register families cover permission selection, HBM/SRAM hashing polynomials, scrambler enables, HBM/PCI/SRAM rate limiting, E2E credit and counter controls, non-linear memory steering, secure and privileged route-range tables, RGL latency/token controls, and HBM performance-counter selectors.

## Important APIs, types, and functions
The file declares no functions or data structures. Its interface is the macro set:

- `mmNIF_RTR_CTRL_6_PERM_SEL` for permission selection.
- `mmNIF_RTR_CTRL_6_HBM_POLY_H3_0..27` and `mmNIF_RTR_CTRL_6_SRAM_POLY_H3_0..14` for HBM/SRAM polynomial routing configuration.
- `mmNIF_RTR_CTRL_6_SCRAM_SRAM_EN` and `mmNIF_RTR_CTRL_6_SCRAM_HBM_EN` for scrambler enablement.
- `mmNIF_RTR_CTRL_6_RL_HBM_*`, `mmNIF_RTR_CTRL_6_RL_PCI_*`, and `mmNIF_RTR_CTRL_6_RL_SRAM_*` for rate-limit control.
- `mmNIF_RTR_CTRL_6_E2E_*` for HBM/PCI E2E enable, size, counter set, counter wrap, and counter count registers.
- `mmNIF_RTR_CTRL_6_NL_*` for non-linear steering and HBM performance-counter selection.
- `mmNIF_RTR_CTRL_6_RANGE_SEC_*` and `mmNIF_RTR_CTRL_6_RANGE_PRIV_*` for secure/privileged AW/AR range control and hit status.
- `mmNIF_RTR_CTRL_6_RGL_*` for RGL configuration, expected latency, token, bank-id, and watchdog controls.

## Control flow
The header itself only contributes an include guard. Runtime control flow is in consumers. `gaudi_init_scrambler_sram()` and `gaudi_init_scrambler_hbm()` write controller-6 scrambler enable registers as part of the all-router setup when firmware security is disabled and firmware has not already enabled the feature.

`gaudi_init_e2e()` programs controller 6 with the same E2E size profile as controller 1: HBM write/read sizes `275 >> 3` and `614 >> 3`, PCI write size `1`, and PCI read size `39`. It then enables HBM and PCI E2E. `gaudi_security.c` includes controller-6 secure AW/AR hit, base, and mask registers in the high-bandwidth route-range arrays used by common security programming logic.

## State and persistence
The constants name hardware state. Scrambler, E2E, route-range, rate-limit, non-linear, and RGL configuration persists in the register block until reset or reprogramming. E2E counters and route-range hit registers are volatile hardware state. The header has no storage or persistence beyond the generated source definitions.

External state determines use: firmware security and boot-status fields decide whether the Linux driver programs these registers, and driver hardware-capability bits track completed scrambler initialization.

## Dependencies and integration points
`gaudi_regs.h` includes this file. The main runtime integration points are `gaudi.c` for initialization and `gaudi_security.c` for route-range setup and fault attribution. Correct writes also require generated field/shift macros and the common HabanaLabs register accessor layer. The block participates with NIF controllers 0-7, SIF router controls, and DMA interface controls in Gaudi's high-bandwidth protection and routing fabric.

## Risks and edge cases
- Address constants have no runtime validation; using a register map from the wrong ASIC revision can cause silent misconfiguration.
- Controller 6 uses the controller-1 E2E profile, not the profiles from controllers 0, 2, 3, 4, or 5.
- Secure range arrays depend on the stable order and existence of all `RANGE_SEC_*` symbols.
- Counter and hit-status reads can be timing-sensitive under active traffic.
- The generated-file warning should be treated as authoritative: fixes belong in the generator or ASIC database, not hand edits.

## Test signals
Expected signals are clean probe/reset, successful non-secure scrambler and E2E initialization when applicable, working NIC traffic through controller 6, and no unexpected protection faults. Security tests should confirm AW/AR range programming and hit reporting for controller 6. Static checks should verify the 437-symbol count, the `0x3E6xxx` address range, and normalized equality with the other NIF router-control maps.
