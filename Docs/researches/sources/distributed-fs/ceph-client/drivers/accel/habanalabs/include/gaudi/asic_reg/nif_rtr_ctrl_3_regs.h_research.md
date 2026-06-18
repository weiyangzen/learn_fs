# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_3_regs.h

## Purpose
`nif_rtr_ctrl_3_regs.h` is the generated Gaudi register map for `NIF_RTR_CTRL_3`, a Network Interface router-control instance of the `RTR_CTRL` prototype. It defines 437 `mmNIF_RTR_CTRL_3_*` symbols in the address range `0x3B6108..0x3B6CBC`. The register layout is identical to the other NIF router-control instances after normalizing the controller id and base address.

The header supplies the symbolic register contract for controller-3 routing policy, HBM/SRAM hash polynomial setup, SRAM/HBM scrambler enablement, rate limiting, E2E credits and counters, non-linear steering, secure/privileged route ranges, RGL controls, and HBM performance counter selection.

## Important APIs, types, and functions
No functions or C types are declared. The relevant interface is the macro namespace:

- `mmNIF_RTR_CTRL_3_PERM_SEL` for block permission selection.
- `mmNIF_RTR_CTRL_3_HBM_POLY_H3_0..27` and `mmNIF_RTR_CTRL_3_SRAM_POLY_H3_0..14` for HBM/SRAM polynomial routing configuration.
- `mmNIF_RTR_CTRL_3_SCRAM_SRAM_EN` and `mmNIF_RTR_CTRL_3_SCRAM_HBM_EN` for scrambler control.
- `mmNIF_RTR_CTRL_3_RL_HBM_*`, `RL_PCI_*`, and `RL_SRAM_*` for rate-limit control.
- `mmNIF_RTR_CTRL_3_E2E_*` for HBM/PCI E2E enable, size, counter set, counter wrap, and counter count registers.
- `mmNIF_RTR_CTRL_3_NL_*` for non-linear SRAM/HBM steering and performance-counter selection.
- `mmNIF_RTR_CTRL_3_RANGE_SEC_*` and `mmNIF_RTR_CTRL_3_RANGE_PRIV_*` for secure and privileged range checks on AW and AR channels.
- `mmNIF_RTR_CTRL_3_RGL_*` for RGL configuration, latency expectation, token, bank-id, and watchdog registers.

## Control flow
The generated file itself does not execute logic. `gaudi_init_scrambler_sram()` and `gaudi_init_scrambler_hbm()` use the scrambler enable symbols as part of a broader sequence that programs all NIF/SIF/DMA router paths when firmware security is disabled and firmware boot status indicates scrambling is not already active.

`gaudi_init_e2e()` writes controller-3 E2E size registers with HBM write/read sizes `176 >> 3` and `32 >> 3`, PCI write size `19`, and PCI read size `32`, then enables HBM and PCI E2E. The security code uses controller-3 `RANGE_SEC_*` symbols in indexed arrays for secure AW/AR hit detection and base/mask programming across the high-bandwidth route range fabric.

## State and persistence
The symbols reference persistent hardware register state, not software objects. Values written to scrambler, E2E, route-range, rate-limit, non-linear steering, and RGL registers remain until reset or reconfiguration. Counter and hit-status registers are volatile hardware state and may change as traffic flows. No value is cached or persisted by this header.

Software persistence is through external driver structures and firmware status: capability bits prevent duplicate scrambler programming, while security-mode flags determine whether Linux or firmware owns the programming.

## Dependencies and integration points
`gaudi_regs.h` includes this file, making its constants available to Gaudi source files. Main consumers are the initialization code in `gaudi.c` and secure range code in `gaudi_security.c`. The header also relies on generated mask/shift definitions for correctly forming register values and on the common register accessors used by the HabanaLabs driver.

## Risks and edge cases
- Since the file contains only constants, compile success does not validate that the addresses are correct for the attached silicon.
- Controller 3 and controller 4 share the same E2E size programming, but differ from other NIF controllers. Maintenance should keep those relationships deliberate.
- Route-range programming has a high chance of copy/paste or index errors because every range has low/high base and low/high mask registers for AW and AR.
- Hardware counters and hit bits can be read-clear or timing-sensitive depending on the underlying register semantics; consumers should avoid assuming persistence.
- Manual edits should be avoided because the header is generated.

## Test signals
Test probe and reset flows with firmware-owned and driver-owned scrambler/E2E setup. Exercise traffic paths expected to cross controller 3 and validate no unexpected protection hits or E2E credit stalls occur. Security tests should intentionally hit secure AW/AR ranges and confirm the controller-3 hit registers are surfaced. Static validation should confirm the `0x3B6xxx` address window and identical normalized macro list.
