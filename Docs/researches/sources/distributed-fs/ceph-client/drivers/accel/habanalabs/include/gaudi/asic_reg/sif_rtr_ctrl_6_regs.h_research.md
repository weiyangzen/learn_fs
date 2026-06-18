# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/sif_rtr_ctrl_6_regs.h

## Purpose

`sif_rtr_ctrl_6_regs.h` is the generated register-address map for Gaudi SIF router controller instance 6. It defines `mmSIF_RTR_CTRL_6_*` MMIO offsets in the `0x366...` range for an `RTR_CTRL` hardware prototype. This header is a pure compile-time address catalog used by low-level driver code; it does not declare C data structures, functions, callbacks, or software state.

The file’s role is to let driver code refer to named hardware functions without embedding numeric offsets throughout the implementation. It covers router hashing, scrambler enables, rate limiting, E2E traffic protection, non-linear mapping, security/privilege range tables, range-hit status, and RGL controls for this one SIF router instance.

## Important APIs and Register Groups

The public API consists of preprocessor macros. Key groups are:

- `PERM_SEL` for permission/route selection.
- `HBM_POLY_H3_0..27` and `SRAM_POLY_H3_0..14` for HBM and SRAM hash-polynomial configuration.
- `SCRAM_SRAM_EN` and `SCRAM_HBM_EN` for enabling router-side SRAM/HBM scrambling.
- HBM/PCI/SRAM rate-limit controls: enable, saturation, reset, timeout, and SRAM reduction registers.
- E2E control: HBM/PCI enable bits, HBM/PCI read/write size registers, AR/AW PCI/HBM counter set/wrap/count registers, and per-HBM-channel counter wrap/count exports.
- Non-linear memory selection and offset tables: `NL_HBM_SEL_*`, `NON_LIN_EN`, `NL_SRAM_BANK_*`, `NL_SRAM_OFFSET_*`, `NL_HBM_OFFSET_*`, and `NL_HBM_PC_SEL_*`.
- Secure and privileged range programming tables for write (`AW`) and read (`AR`) paths, each with 16 slots of low/high base and low/high mask registers.
- Range hit status registers for secure and privileged AW/AR paths.
- RGL latency/token/bank/watchdog controls.

## Control Flow and State Behavior

There is no internal control flow. The header’s constants are used by runtime code that performs ordered register writes. The resulting state is device state, not software state, and follows the hardware reset and firmware/driver ownership model.

In `gaudi.c`, SIF router 6 is part of the host-side scrambler initialization flow. The driver writes `SCRAM_SRAM_EN` and `SCRAM_HBM_EN` under the same guards used for other routers: firmware security disabled, boot-status bits not already enabling the feature, and the driver capability bit not already initialized. In E2E setup, instance 6 is programmed with HBM write size `275 >> 3`, HBM read size `614 >> 3`, PCI write size `1`, and PCI read size `39`, then E2E is enabled for HBM and PCI paths.

In `gaudi_security.c`, instance 6 range registers appear in high-bandwidth router arrays between instances 5 and 7. Generic security code can therefore address all routers consistently when programming secure base/mask ranges or reading hit registers.

## Dependencies and Integration Points

The header depends on generated register-map consistency and on being included in the Gaudi ASIC register namespace. Runtime use depends on the HabanaLabs MMIO accessor layer and on separate field-definition headers for shifts and masks. It integrates with:

- Gaudi boot/init code for scrambler and E2E feature setup.
- Gaudi security range programming through ordered arrays of router registers.
- Hardware debug and diagnostics that may inspect E2E counters, range-hit state, or RGL controls.

The instance-to-instance layout symmetry is an integration contract. Instance 6 must remain aligned with the same offsets as router 4, 5, and 7, with only the base page changed to `0x366...`.

## Risks and Test Signals

The highest-risk changes are generated-address changes, prefix mistakes, or any manual edit that breaks the sibling layout. Because security and E2E consumers often operate in arrays, an incorrect instance 6 base/mask macro may be hard to isolate: symptoms can appear as protected-range misses, unexpected range-hit status, boot instability, or data integrity failures on particular traffic paths.

Testing should cover full Gaudi probe/init, MMIO write/read sanity for scrambler and E2E setup, security range programming across all high-bandwidth routers, and stress traffic that exercises the SIF router 6 path. Static validation should compare this header against the hardware database and confirm the `0x10000` address stride from instance 5 and to instance 7.
