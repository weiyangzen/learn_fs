# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_2_regs.h

## Purpose
`nif_rtr_ctrl_2_regs.h` is the generated register-address map for Gaudi `NIF_RTR_CTRL_2`, another instance of the `RTR_CTRL` Network Interface router-control prototype. It defines 437 `mmNIF_RTR_CTRL_2_*` symbols covering `0x3A6108..0x3A6CBC`. Its normalized contents match the other NIF router-control headers in this subset, with only the controller id and address base changed.

The file gives driver code symbolic names for controller-2 router policy, HBM/SRAM hashing polynomials, scrambler enables, rate-limit controls, E2E credit/counter registers, non-linear memory steering, route-range access-control registers, RGL scheduling/latency controls, and HBM performance-counter selectors.

## Important APIs, types, and functions
There are no callable APIs or data structures. The important symbols are:

- `mmNIF_RTR_CTRL_2_PERM_SEL` for permission/policy selection.
- `mmNIF_RTR_CTRL_2_HBM_POLY_H3_0..27` and `mmNIF_RTR_CTRL_2_SRAM_POLY_H3_0..14` for HBM/SRAM distribution configuration.
- `mmNIF_RTR_CTRL_2_SCRAM_SRAM_EN` and `mmNIF_RTR_CTRL_2_SCRAM_HBM_EN` for driver-controlled scrambler enablement.
- `mmNIF_RTR_CTRL_2_RL_HBM_*`, `mmNIF_RTR_CTRL_2_RL_PCI_*`, and `mmNIF_RTR_CTRL_2_RL_SRAM_*` for rate limiting.
- `mmNIF_RTR_CTRL_2_E2E_*` for HBM/PCI E2E enablement, transaction-size credits, and read/write counter state.
- `mmNIF_RTR_CTRL_2_NL_*` for non-linear steering and HBM performance counter selection.
- `mmNIF_RTR_CTRL_2_RANGE_SEC_*` and `mmNIF_RTR_CTRL_2_RANGE_PRIV_*` for secure/privileged AW and AR range base/mask tables plus hit status.
- `mmNIF_RTR_CTRL_2_RGL_*` for RGL configuration, expected latency, token, bank-id, and watchdog controls.

## Control flow
The include guard is the only control flow in this generated header. Runtime flow is in consumers. `gaudi_init_scrambler_sram()` and `gaudi_init_scrambler_hbm()` conditionally write controller-2 scrambler enable registers when firmware has not already handled the feature and the driver is allowed to program it directly.

In `gaudi_init_e2e()`, controller 2 is programmed with minimal E2E sizes: HBM write size `1`, HBM read size `1`, PCI write size `1`, and PCI read size `32`. The function then enables E2E for HBM and PCI on this controller. `gaudi_security.c` includes controller-2 secure AW/AR registers in its high-bandwidth route-range arrays, so common security setup loops can program the 16 secure ranges and later identify secure hit status.

## State and persistence
Register state is owned by hardware. Scrambler enable bits, E2E credit sizes/enables, route-range base/mask tables, rate-limit controls, non-linear steering values, and RGL settings persist until reset or reprogramming. E2E counters, wrap indicators, and route-range hit registers are volatile observation state. The header creates no software storage and has no persistence independent of generated source content.

External driver state tracks whether setup has been performed and whether security firmware owns the programming sequence. In secure firmware mode the driver avoids direct scrambler and E2E initialization, so the symbols remain present but may not be written by Linux.

## Dependencies and integration points
The header is pulled in by `gaudi_regs.h` and used by `gaudi.c` and `gaudi_security.c`. It depends on the surrounding generated register ecosystem for field masks and on common Gaudi register-access macros such as `WREG32()` in consumers. It integrates with firmware boot-status bits that determine whether Linux should write scrambler/E2E registers and with the high-bandwidth route-range protection path.

## Risks and edge cases
- Controller 2 has intentionally small E2E sizes compared with controllers 0, 1, 3, 4, and 6. Tuning changes should be reviewed against hardware expectations, not copied from neighboring blocks.
- The many range-register sequences must preserve AW versus AR and base versus mask ordering. A swapped symbol can weaken security or cause false protection faults.
- Generated address constants provide no type safety; any macro can be passed to any register accessor.
- Security firmware mode changes who programs these registers, so tests must cover both firmware-owned and driver-owned setup paths.
- Manual modification risks divergence from the ASIC database.

## Test signals
Strong signals include successful probe with direct scrambler/E2E setup when firmware leaves it to the driver, working NIC traffic through controller 2, and no unexpected secure range hits during normal workloads. Protection tests should verify that programmed secure AW/AR ranges generate hits through the controller-2 entries. Register-generation checks should confirm the normalized symbol set and `0x3A6xxx` address window.
