# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/sif_rtr_ctrl_5_regs.h

## Purpose

`sif_rtr_ctrl_5_regs.h` is an auto-generated Gaudi ASIC register-address header for SIF router controller instance 5. It exports the absolute MMIO offsets for the `SIF_RTR_CTRL_5` hardware block, another instantiation of the `RTR_CTRL` prototype. It contains only preprocessor constants and include guards; there are no functions, types, inline helpers, persistent software variables, or algorithms.

The instance 5 window uses the `0x356...` address range. It is structurally identical to the neighboring SIF router-control headers, with the macro prefix and address base changed for this specific hardware instance. Driver code uses these constants to program routing, scrambling, E2E, non-linear mapping, security, privilege, and performance/latency controls.

## Important APIs and Register Groups

The exported API is the `mmSIF_RTR_CTRL_5_*` macro family. The file includes:

- Core selection and hashing controls: `PERM_SEL`, `HBM_POLY_H3_0..27`, and `SRAM_POLY_H3_0..14`.
- Scrambler enables: `SCRAM_SRAM_EN` and `SCRAM_HBM_EN`.
- Rate-limiting registers for HBM, PCI, and SRAM paths: `RL_HBM_*`, `RL_PCI_*`, `RL_SRAM_*`, and `RL_SRAM_RED`.
- E2E configuration and counters: `E2E_HBM_EN`, `E2E_PCI_EN`, write/read size registers, PCI/HBM AW and AR counter setup registers, and per-HBM channel counter wrap/count registers.
- Non-linear address-routing controls: `NL_HBM_SEL_0..1`, `NON_LIN_EN`, SRAM bank and offset tables, HBM offset table entries 0 through 18, and `NL_HBM_PC_SEL_0..3`.
- Write-path and read-path security/privilege range tables: 16 low/high base and mask entries for secure AW, privileged AW, secure AR, and privileged AR ranges.
- Hit/status registers for secure and privileged range matches on AW and AR.
- RGL configuration: `RGL_CFG`, `RGL_SHIFT`, expected latency registers, token registers, bank IDs, and watchdog.

## Control Flow and State Behavior

The header does not implement control flow. Its constants become operands to driver MMIO operations. Hardware register values persist in the device until reset or until overwritten by firmware or driver code.

`gaudi.c` uses instance 5 during scrambler initialization and E2E initialization. For SRAM/HBM scrambling, the driver writes `SCRAM_SRAM_EN` and `SCRAM_HBM_EN` only if firmware security is disabled, firmware status does not report the feature already enabled, and the matching hardware capability bit is not already marked initialized. For E2E, instance 5 is programmed with small credit sizes: HBM write size `1`, HBM read size `1`, PCI write size `1`, and PCI read size `32`, followed by writes to `E2E_HBM_EN` and `E2E_PCI_EN`.

`gaudi_security.c` includes instance 5 in high-bandwidth router arrays for secure range hit, base, and mask registers. This lets generic security setup code iterate over all router instances and program or inspect the same logical range slots across SIF and NIF blocks.

## Dependencies and Integration Points

This file depends on the generated ASIC register-map pipeline and on consumers including it through Gaudi register headers. Its macro values are only meaningful when paired with the driver’s MMIO accessor layer and the bitfield definitions used to compose register values, such as `IF_RTR_CTRL_SCRAM_*` and `IF_RTR_CTRL_E2E_*` shift constants.

The instance is integrated with Gaudi memory routing and security setup. The repeated layout means code can treat SIF router 5 as one element in ordered router arrays, but the exact address base must remain correct because array order and macro prefix both encode hardware topology.

## Risks and Test Signals

The major risk is incorrect generated addresses. A bad constant can corrupt unrelated router state, misconfigure E2E protection, or make security range programming ineffective. Instance 5 is easy to confuse with siblings because the body is almost identical except for prefix and base address; review should verify all exported macros stay in the `0x356...` page and preserve the expected offsets within the `RTR_CTRL` prototype.

Test signals include successful Gaudi driver initialization, no MMIO access errors when host-side scrambler/E2E setup runs, and security tests that validate protected range programming across all SIF/NIF routers. Static comparison against sibling headers should show the same register layout with a `0x10000` stride from instance 4 and to instance 6.
