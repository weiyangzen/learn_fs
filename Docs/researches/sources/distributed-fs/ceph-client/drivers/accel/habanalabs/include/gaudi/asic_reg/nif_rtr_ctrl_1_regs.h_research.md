# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_1_regs.h

## Purpose
`nif_rtr_ctrl_1_regs.h` is an auto-generated Gaudi ASIC register-address header for `NIF_RTR_CTRL_1`, the second Network Interface router-control block using the shared `RTR_CTRL` prototype. It defines 437 `mmNIF_RTR_CTRL_1_*` MMIO/config register symbols in the address window `0x396108..0x396CBC`. Normalizing the controller id and high address nibble shows the same register layout as controllers 0 and 2-6, shifted by the Gaudi router-control stride.

The symbols cover the full NIF router-control surface for this block: permission selection, HBM/SRAM distribution polynomial registers, scrambler enables, HBM/PCI/SRAM rate limiting, HBM/PCI E2E credit and counter controls, non-linear memory steering, secure and privileged route-range tables, RGL latency/token controls, and HBM performance-counter selectors.

## Important APIs, types, and functions
There are no C functions or types. The API is the generated macro set:

- `mmNIF_RTR_CTRL_1_PERM_SEL` names the block permission selector.
- `mmNIF_RTR_CTRL_1_HBM_POLY_H3_0..27` and `mmNIF_RTR_CTRL_1_SRAM_POLY_H3_0..14` identify router hashing/distribution polynomial registers.
- `mmNIF_RTR_CTRL_1_SCRAM_SRAM_EN` and `mmNIF_RTR_CTRL_1_SCRAM_HBM_EN` are direct driver initialization targets for SRAM and HBM scrambling.
- `mmNIF_RTR_CTRL_1_RL_HBM_*`, `RL_PCI_*`, and `RL_SRAM_*` expose rate-limit controls.
- `mmNIF_RTR_CTRL_1_E2E_HBM_EN`, `E2E_PCI_EN`, E2E size registers, and E2E counter set/wrap/count registers support end-to-end credit setup and observation.
- `mmNIF_RTR_CTRL_1_NL_*` covers non-linear HBM/SRAM selection, banks, offsets, and HBM performance-counter selection.
- `mmNIF_RTR_CTRL_1_RANGE_SEC_*` and `mmNIF_RTR_CTRL_1_RANGE_PRIV_*` define secure and privileged range base/mask tables for AW and AR channels plus hit registers.
- `mmNIF_RTR_CTRL_1_RGL_*` defines RGL configuration, expected-latency, token, bank-id, and watchdog registers.

## Control flow
This header contributes symbolic addresses to initialization and security loops. `gaudi_init_scrambler_sram()` and `gaudi_init_scrambler_hbm()` write the controller-1 scrambler enable registers only when firmware security is disabled, firmware did not already enable the feature, and the corresponding hardware capability bit has not been set.

`gaudi_init_e2e()` programs controller-1 E2E sizes before enabling credits. For this block the driver uses HBM write/read sizes `275 >> 3` and `614 >> 3`, PCI write size `1`, and PCI read size `39`, then enables HBM and PCI E2E. In `gaudi_security.c`, controller-1 secure AW/AR hit, base, and mask registers are listed in the common high-bandwidth route-range arrays so the protection setup code can handle all NIF/SIF/DMA router blocks with a shared indexed flow.

## State and persistence
The macros name hardware registers, so state persists in the Gaudi register block rather than in this header. Scrambler and E2E enablement remains active until reset or later programming. Route-range tables persist as hardware access-control state and are expected to be programmed during security/protection initialization. E2E counter count/wrap registers and range hit registers are volatile hardware-observation points.

The software state tied to these registers is external: `gaudi->hw_cap_initialized` records scrambler setup completion, while security code uses arrays of these addresses to program or inspect protected ranges.

## Dependencies and integration points
`gaudi_regs.h` includes this generated header for use by Gaudi driver compilation units. Runtime consumers include `gaudi.c` scrambler/E2E setup, `gaudi_security.c` route-range and hit-status handling, and generated field mask headers that provide shifts such as `IF_RTR_CTRL_E2E_HBM_EN_VAL_SHIFT`. The register block is part of the broader Gaudi NIF/SIF/DMA routing and protection fabric.

## Risks and edge cases
- The header must match the ASIC register database. Address drift in generated constants can misprogram the router while still compiling cleanly.
- Controller 1 shares E2E tuning with controller 6 but not with every NIF controller. Bulk edits should preserve the explicit per-controller values in `gaudi_init_e2e()`.
- Security arrays assume identical relative layout for the secure range registers across DMA, SIF, and NIF blocks. Missing or reordered symbols would break common indexed programming.
- Volatile counter and hit registers should not be treated as stable software state.
- Manual edits conflict with the file's generated nature.

## Test signals
Probe/reset tests should show scrambler and E2E initialization completing without protection faults. NIC traffic routed through controller 1 should work with normal HBM/PCI access and without unexpected `RANGE_SEC_HIT_*` reports. Security tests should program AW/AR ranges and confirm hits are attributed to the controller-1 entries in the high-bandwidth route-range arrays. Register-map validation can check the `0x10000` stride from controller 0 and the identical normalized symbol set.
