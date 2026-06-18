# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_0_regs.h

## Purpose
`nif_rtr_ctrl_0_regs.h` is an auto-generated Gaudi ASIC register-address header for the first Network Interface router-control block, `NIF_RTR_CTRL_0`, whose prototype is `RTR_CTRL`. It contains only preprocessor constants mapping symbolic register names to MMIO/config-space addresses. The covered address window is `0x386108..0x386CBC`, and the file defines 437 `mmNIF_RTR_CTRL_0_*` symbols.

The register families describe routing and protection controls around network-interface traffic into HBM, SRAM, and PCI paths: HBM/SRAM hashing polynomial registers, SRAM/HBM scrambler enables, rate-limit controls, end-to-end credit/counter controls, non-linear HBM/SRAM steering controls, security and privilege range registers for AW/AR traffic, RGL latency/token/bank controls, and HBM performance-counter selector registers.

## Important APIs, types, and functions
This header exposes no functions, structs, or runtime APIs. Its important interface is the macro namespace:

- `mmNIF_RTR_CTRL_0_PERM_SEL` selects the permission/routing policy register for the block.
- `mmNIF_RTR_CTRL_0_HBM_POLY_H3_0..27` and `mmNIF_RTR_CTRL_0_SRAM_POLY_H3_0..14` name polynomial/hash configuration registers used by the router for HBM and SRAM distribution.
- `mmNIF_RTR_CTRL_0_SCRAM_SRAM_EN` and `mmNIF_RTR_CTRL_0_SCRAM_HBM_EN` are used by Gaudi initialization to enable SRAM/HBM scrambling when firmware has not already enabled it and security firmware is not active.
- `mmNIF_RTR_CTRL_0_RL_HBM_*`, `mmNIF_RTR_CTRL_0_RL_PCI_*`, and `mmNIF_RTR_CTRL_0_RL_SRAM_*` name rate-limit enable, saturation, reset, timeout, and reduction controls for memory/PCI targets.
- `mmNIF_RTR_CTRL_0_E2E_*` names end-to-end credit enable, size, counter set, wrap, and count registers for HBM and PCI read/write channels.
- `mmNIF_RTR_CTRL_0_NL_*` names non-linear HBM/SRAM selection, bank, offset, and HBM performance-counter selector registers.
- `mmNIF_RTR_CTRL_0_RANGE_SEC_*` and `mmNIF_RTR_CTRL_0_RANGE_PRIV_*` define 16-range base/mask tables plus hit-status registers for secure and privileged AW/AR access checks.
- `mmNIF_RTR_CTRL_0_RGL_*` names RGL configuration, expected latency, token, bank-id, and watchdog registers.

## Control flow
The file itself has no control flow beyond a normal include guard. At runtime, control flow appears in consumers. `gaudi_init_scrambler_sram()` writes `mmNIF_RTR_CTRL_0_SCRAM_SRAM_EN` if firmware security is disabled, firmware did not already enable SRAM scrambling, and the driver has not already marked `HW_CAP_SRAM_SCRAMBLER` initialized. `gaudi_init_scrambler_hbm()` follows the same pattern for `mmNIF_RTR_CTRL_0_SCRAM_HBM_EN` and `HW_CAP_HBM_SCRAMBLER`.

`gaudi_init_e2e()` writes controller-0 E2E size registers before enabling HBM and PCI E2E credits. For this controller the driver programs HBM write/read sizes as `318 >> 3` and `956 >> 3`, PCI write size `79`, and PCI read size `163`, then sets `mmNIF_RTR_CTRL_0_E2E_HBM_EN` and `mmNIF_RTR_CTRL_0_E2E_PCI_EN`. Security setup in `gaudi_security.c` places `NIF_RTR_CTRL_0` into arrays of high-bandwidth route-range registers so common loops can program secure AW/AR base/mask ranges and read secure hit status for all DMA, SIF, and NIF router blocks.

## State and persistence
All state named here is hardware state. The header does not allocate memory or persist software data. Writes to the scrambler, E2E, route-range, rate-limit, non-linear routing, and RGL symbols persist in the device register block until firmware, reset, power loss, or later driver programming changes them. The driver's persistent software indication is external: `gaudi->hw_cap_initialized` records whether the SRAM/HBM scrambler setup paths have completed.

Counter registers such as `E2E_*_CTR_CNT` and `E2E_*_CTR_WRAP` are hardware-observed state and should be treated as volatile. Route-range hit registers capture security/protection events and are consumed by the protection-bit/security reporting paths rather than stored by this header.

## Dependencies and integration points
The header is included through `include/gaudi/asic_reg/gaudi_regs.h`, which provides the generated Gaudi register map to Gaudi driver code. Main integration points are `gaudi.c` for scrambler and E2E initialization, `gaudi_security.c` for secure range programming and hit reporting, and `gaudiP.h` for the router-control block offset convention used by Gaudi-specific code.

The register values depend on the generated ASIC database matching the Gaudi hardware revision. The companion field/shift definitions, such as `IF_RTR_CTRL_SCRAM_SRAM_EN_VAL_SHIFT`, live in generated mask headers and are required to form values written to these addresses.

## Risks and edge cases
- Generated headers are address contracts. A wrong value silently redirects MMIO writes to the wrong hardware register and can break routing, security ranges, or credit accounting.
- Controller 0 has distinct E2E tuning values from controllers 1, 2, 3, 4, 5, and 6. Replacing explicit symbols with naive indexed arithmetic risks applying the wrong credit sizes.
- Secure and privileged range tables have many parallel AW/AR base/mask registers. Off-by-one range programming can leave memory exposed or falsely block valid transactions.
- These constants are absolute generated register addresses; consumers must use the right accessor convention for config-space offsets versus absolute addresses.
- The file is marked auto-generated, so manual edits are fragile and would likely be overwritten by the register-generation flow.

## Test signals
Useful signals include successful Gaudi probe with no scrambler/E2E initialization errors, absence of protection-bit interrupts during normal NIC traffic, working NIC DMA/collective traffic that reaches HBM/SRAM/PCI targets, and expected behavior when firmware security pre-enables scramblers or E2E credits. Security validation should exercise protected and unprotected AW/AR ranges and confirm that `RANGE_SEC_HIT_AW` and `RANGE_SEC_HIT_AR` status reporting identifies controller 0. Low-level register tests can compare the generated address stride and symbol set against the ASIC database.
