# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic1_qm0_regs.h

## Purpose

`nic1_qm0_regs.h` defines the memory-mapped register offsets for the Gaudi `NIC1_QM0` QMAN block. It is included through `gaudi_regs.h` and gives driver code stable names for queue-manager control, doorbell, status, command-processor, arbitration, rate-limit, indirect-gateway, and error registers. The local register window starts at `mmNIC1_QM0_GLBL_CFG0` offset `0xD20000` and runs through `mmNIC1_QM0_GLBL_MEM_INIT_BUSY` offset `0xD20D00`; `gaudi_blocks.h` maps the block base as `mmNIC1_QM0_BASE 0x7FFCD20000ull`, with section size `0x2000` and max offset `0xD040`.

## Important APIs, Types, and Macros

This header exports macros only. Important families are `GLBL_*` global configuration/protection/status and message registers, `PQ_*` producer queue base/size/PI/CI/config/status registers for four queues, `CQ_*` completion queue config/status/pointer/control registers for five queues, `CP_*` command-processor message/LDMA/fence/current-instruction/barrier/debug/AXI-user registers, `ARB_*` scheduling and credit registers, plus `CGM_*`, `CSMR_STRICT_PRIO_CFG`, rate-limit, local-range, AXCACHE, indirect APB gateway, global error, and memory-init status registers.

## Control Flow and Integration

The header has no executable control flow. Runtime behavior comes from code that uses these constants with MMIO helpers such as `WREG32`. In `gaudi.c`, `mmNIC1_QM0_GLBL_CFG1` is written during NIC QMAN stop/stall handling when `HW_CAP_NIC2` is initialized; the driver reuses `NIC0_QM0_GLBL_CFG1_*_STOP_MASK` bit definitions because the QMAN layout is shared. Queue submission maps `GAUDI_QUEUE_ID_NIC_2_0...GAUDI_QUEUE_ID_NIC_2_3` to doorbells by adding a 4-byte queue offset to `mmNIC1_QM0_PQ_PI_0`. Interrupt handling maps `GAUDI_EVENT_NIC1_QM0` to `mmNIC1_QM0_BASE` and common QMAN error handling. `gaudi_security.c` uses selected offsets to build protection masks.

## State and Persistence Behavior

The header itself stores no software state. The named registers describe volatile device state that persists in hardware until reset, firmware reinitialization, or explicit driver writes. State-bearing groups include PQ producer/consumer indexes, CQ pointers and latched pointer status, CP current instruction/fence counters, arbitration credits, error cause/drop/status registers, and memory-init busy. Writes to configuration, queue base, queue size, security property, AR/AWUSER, rate-limit, and arbitration registers change live device behavior.

## Dependencies

The file depends only on the C preprocessor and include guards. It is pulled into the Gaudi driver via `include/gaudi/asic_reg/gaudi_regs.h`. Full block base and section metadata live in `gaudi_blocks.h`; bit masks for the shared QMAN layout are mostly represented by `nic0_qm0_masks.h`. Consumers depend on queue IDs, hardware capability bits, async event IDs, and MMIO helpers in the Gaudi driver.

## Risks

The file is auto-generated and should not be edited by hand. Any wrong offset can redirect MMIO reads/writes into another hardware block, especially queue doorbells, security property registers, and error registers. The spelling `CHOISE` appears in generated macro names and is part of the generated interface. Because this instance is tied to `HW_CAP_NIC2` and queue IDs for NIC 2 traffic, mismatched NIC numbering in call sites is a realistic integration risk.

## Test Signals

Useful signals are successful kernel build including `gaudi_regs.h`, successful NIC2 queue submission with producer-index writes landing at `mmNIC1_QM0_PQ_PI_0 + n * 4`, clean QMAN stop/stall behavior via `GLBL_CFG1`, correct `GAUDI_EVENT_NIC1_QM0` IRQ diagnostics, security mask generation that includes `GLBL_CFG1`, `GLBL_NON_SECURE_PROPS_*`, and `PQ_PI_0`, and hardware/firmware tests showing no unexpected QMAN arbitration or CP fence errors.
