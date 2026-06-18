# Research: subset-b-000971

Grouped research for Gaudi NIF router control register maps under `sources/distributed-fs/ceph-client`. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_0_regs.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_0_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_1_regs.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_1_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_2_regs.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_2_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_3_regs.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_3_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_4_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_4_regs.h

## Purpose
`nif_rtr_ctrl_4_regs.h` is the generated register-address map for Gaudi `NIF_RTR_CTRL_4`, a fourth Network Interface router-control instance using the `RTR_CTRL` prototype. It defines 437 `mmNIF_RTR_CTRL_4_*` constants in `0x3C6108..0x3C6CBC`. Its symbol families and relative offsets match the other NIF router-control headers.

The header is the symbolic interface to controller-4 router permissions, HBM/SRAM distribution polynomials, SRAM/HBM scrambling, HBM/PCI/SRAM rate limiting, HBM/PCI E2E credits and counters, non-linear HBM/SRAM mapping, security/privilege route ranges, RGL controls, and HBM performance-counter selectors.

## Important APIs, types, and functions
The file exports macros only:

- `mmNIF_RTR_CTRL_4_PERM_SEL` for permission selection.
- `mmNIF_RTR_CTRL_4_HBM_POLY_H3_0..27` and `mmNIF_RTR_CTRL_4_SRAM_POLY_H3_0..14` for distribution/hash polynomial programming.
- `mmNIF_RTR_CTRL_4_SCRAM_SRAM_EN` and `mmNIF_RTR_CTRL_4_SCRAM_HBM_EN` for scrambler enablement.
- `mmNIF_RTR_CTRL_4_RL_HBM_*`, `mmNIF_RTR_CTRL_4_RL_PCI_*`, and `mmNIF_RTR_CTRL_4_RL_SRAM_*` for rate limits.
- `mmNIF_RTR_CTRL_4_E2E_*` for E2E credit enablement, credit sizes, and counter controls.
- `mmNIF_RTR_CTRL_4_NL_*` for non-linear memory steering and performance selector state.
- `mmNIF_RTR_CTRL_4_RANGE_SEC_*` and `mmNIF_RTR_CTRL_4_RANGE_PRIV_*` for secure/privileged AW and AR range checking.
- `mmNIF_RTR_CTRL_4_RGL_*` for RGL expected-latency, token, bank-id, watchdog, and configuration registers.

## Control flow
Runtime code reaches these macros through common Gaudi initialization and security paths. The scrambler setup functions in `gaudi.c` conditionally program controller-4 SRAM/HBM scrambler enable registers when firmware did not already do so. The E2E setup function programs controller-4 HBM write/read sizes as `176 >> 3` and `32 >> 3`, PCI write size `19`, and PCI read size `32`, then writes the HBM and PCI enable registers.

`gaudi_security.c` uses controller-4 secure range symbols in arrays that cover DMA, SIF, and NIF router blocks. Those arrays let common loops program base/mask registers and inspect AW/AR hit status without controller-specific branches.

## State and persistence
The header defines names for hardware state only. Register writes to scrambler, E2E, range, rate-limit, non-linear, and RGL controls persist in hardware until reset or reprogramming. E2E count/wrap registers and secure/privileged hit registers are volatile status. No software state is created by the header, and no values survive except as source constants in the generated file.

External software state includes driver hardware-capability bits for scrambler initialization and firmware boot/security flags that suppress direct Linux programming when firmware owns the block setup.

## Dependencies and integration points
This file is part of the generated register include chain rooted at `gaudi_regs.h`. It integrates with `gaudi.c` initialization, `gaudi_security.c` protection setup/reporting, generated field mask headers, and the hardware register accessor layer. It also participates in the larger route-range model that includes DMA interface and SIF router-control blocks.

## Risks and edge cases
- Address-map errors are high impact because these symbols configure routing, security, and credit behavior.
- Controller 4 mirrors controller 3 E2E values; future tuning should preserve intentional per-controller differences.
- Common security arrays rely on the symbol names and relative range-register layout being present and consistent.
- Reads from status/counter registers may race with hardware traffic and should be interpreted as snapshots.
- The generated-file warning means local hand changes are not maintainable.

## Test signals
Validate successful driver probe, reset, and direct scrambler/E2E setup on non-secure firmware paths. Run NIC traffic that exercises controller 4 and confirm no E2E stalls or unexpected security hits. Protection tests should verify AW/AR range hits through controller-4 entries. Static checks can verify the `0x3C6xxx` address range, 437 macros, and normalized equality with the other NIF router-control maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_4_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_5_regs.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_5_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_6_regs.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nif_rtr_ctrl_6_regs.h -->
