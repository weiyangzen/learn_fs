# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic2_qm1_regs.h

## Purpose

`nic2_qm1_regs.h` provides the auto-generated MMIO offsets for the Gaudi `NIC2_QM1` QMAN block. It is the QM1 companion to `NIC2_QM0`, with the same register layout shifted to the `0xD62000` local window. The first exported register is `mmNIC2_QM1_GLBL_CFG0 0xD62000`, the last is `mmNIC2_QM1_GLBL_MEM_INIT_BUSY 0xD62D00`, and `gaudi_blocks.h` defines `mmNIC2_QM1_BASE 0x7FFCD62000ull`, section `0x2000`, max offset `0xD040`.

## Important APIs, Types, and Macros

There are no C APIs beyond preprocessor constants. The register map includes global config/protection/status, secure and non-secure global properties, PQ ring setup and doorbells for four producer queues, CQ setup/status for five completion queues, CP message and synchronization registers for five command processors, arbitration WRR/credit/routing/error registers, CGM status, CSMR strict-priority config, HBW/LBW rate-limit knobs, local range, global AXCACHE, indirect APB gateway, global error capture, and memory-init busy status.

## Control Flow and Integration

The file is consumed through `gaudi_regs.h`. `gaudi.c` writes `mmNIC2_QM1_GLBL_CFG1` during QMAN stop when `HW_CAP_NIC5` is initialized. Doorbell selection for `GAUDI_QUEUE_ID_NIC_5_0...GAUDI_QUEUE_ID_NIC_5_3` starts at `mmNIC2_QM1_PQ_PI_0`. Error handling maps `GAUDI_EVENT_NIC2_QM1` to `mmNIC2_QM1_BASE` and the `NIC2_QM1` label, then uses common QMAN diagnostics. `gaudi_security.c` uses selected offsets from this header to define non-secure access/protection masks.

## State and Persistence Behavior

The file stores no state, but it exposes device state registers. Queue progress is held in PQ/CQ producer, consumer, pointer, size, and control registers. Command processing state is represented by message base registers, LDMA offsets, fences, current instruction addresses, barrier configuration, and debug registers. Arbitration credits and error registers reflect scheduler state. Settings remain programmed in the hardware block until reset or a later driver/firmware write.

## Dependencies

Dependencies are the aggregate register include, block-base definitions in `gaudi_blocks.h`, common QMAN mask definitions, Gaudi queue and event enumerations, hardware capability flags, and the driver's MMIO helpers. The header itself needs only standard preprocessor support.

## Risks

The main risk is address-window mismatch: `NIC2_QM1` offsets are close to but distinct from `NIC2_QM0`, and using the wrong prefix affects different queues. Security-sensitive fields are the global protection/property registers and AXI user attributes. Indirect gateway and error registers are low-level hardware controls and should be treated as register-generator output, not hand-maintained source.

## Test Signals

Tests should observe successful build, NIC5 queue submission doorbells at `mmNIC2_QM1_PQ_PI_0 + lane * 4`, correct stop/stall writes to `mmNIC2_QM1_GLBL_CFG1`, IRQ handling for `GAUDI_EVENT_NIC2_QM1`, protected-register mask coverage for non-secure props and PQ PI, and clean hardware execution without CP/arbitration/global errors.
