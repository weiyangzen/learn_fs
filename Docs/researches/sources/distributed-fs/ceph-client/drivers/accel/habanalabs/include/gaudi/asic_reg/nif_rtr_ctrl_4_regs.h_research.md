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
