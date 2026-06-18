# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/sif_rtr_ctrl_7_regs.h

## Purpose

`sif_rtr_ctrl_7_regs.h` is the generated Gaudi register-address header for SIF router controller instance 7, an `RTR_CTRL` prototype instance mapped into the `0x376...` MMIO range. It is a hardware address declaration file: every meaningful line is a `#define` for an `mmSIF_RTR_CTRL_7_*` register offset.

The file provides symbolic names for driver code that configures the last SIF router-control instance in this family. It is not an implementation unit and has no runtime behavior by itself. Its correctness is nevertheless critical because it is the only source of the numeric offsets used by host code for this router instance.

## Important APIs and Register Groups

The macro API is broad and follows the same layout as sibling SIF router-control instances:

- Selection and hashing: `PERM_SEL`, `HBM_POLY_H3_0..27`, and `SRAM_POLY_H3_0..14`.
- Scrambling: `SCRAM_SRAM_EN` and `SCRAM_HBM_EN`.
- Rate limiting: HBM, PCI, and SRAM enable/saturation/reset/timeout registers, plus `RL_SRAM_RED`.
- E2E protection: HBM/PCI enables, HBM/PCI read/write sizes, AR/AW PCI/HBM counter set/wrap/count registers, and per-HBM-channel AR/AW wrap/count registers.
- Non-linear routing: HBM selectors, `NON_LIN_EN`, SRAM bank entries, SRAM/HBM offset entries, and HBM PC selectors.
- Security and privilege range tables for write and read channels: secure and privileged low/high base and mask arrays, 16 entries per table.
- Hit/status: `RANGE_SEC_HIT_AW`, `RANGE_SEC_HIT_AR`, `RANGE_PRIV_HIT_AW`, and `RANGE_PRIV_HIT_AR`.
- RGL controls: configuration, shift, expected latencies, token values, bank IDs, and watchdog.

## Control Flow and State Behavior

The header has no branches or data mutation. Runtime control flow is supplied by Gaudi initialization and security code that writes or reads these MMIO offsets. Hardware owns persistence of the register state across normal driver operations until reset, firmware reprogramming, or another driver write.

`gaudi.c` consumes instance 7 in the same guarded scrambler flows as the other routers. It writes `SCRAM_SRAM_EN` and `SCRAM_HBM_EN` only when firmware security/status does not indicate the firmware already owns the feature. For E2E setup, instance 7 receives HBM write size `297 >> 3`, HBM read size `908 >> 3`, PCI write size `19`, and PCI read size `19`, then the driver enables both HBM and PCI E2E paths.

`gaudi_security.c` places the instance 7 secure hit, secure base, and secure mask registers at the end of the SIF portion of the high-bandwidth router arrays. The array ordering is important because generic code assumes a fixed traversal over DMA, SIF, and NIF router blocks.

## Dependencies and Integration Points

This header is tied to the generated Gaudi ASIC register map and the common HabanaLabs MMIO accessor layer. It also depends on companion bitfield headers for value construction; this file only provides offsets. Integration points include:

- Host-side Gaudi boot/init for scrambler and E2E programming.
- Security setup and diagnostics for high-bandwidth router protected ranges.
- Potential debug use of E2E counters, RGL counters, non-linear mapping, and hit registers.

As the final SIF router-control instance in the observed 4..7 group, this file helps complete symmetric arrays and repeated initialization sequences. Any missing or shifted macro can break array-based programming assumptions.

## Risks and Test Signals

The main risk is silent hardware misprogramming caused by a wrong generated offset. This risk is amplified for instance 7 because it can be confused with neighboring instance 6 except for the `0x376...` base. The security range tables and range-hit registers are particularly sensitive; wrong addresses can cause protected windows to be programmed on the wrong router or prevent violations from being reported.

Testing should include driver initialization paths where firmware has not pre-enabled scrambling/E2E, security range programming across all high-bandwidth routers, and traffic that exercises SIF router 7. Static validation should ensure every macro remains in the `0x376...` page with the expected offsets from the `RTR_CTRL` prototype and a `0x10000` stride from instance 6.
