# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic1_qm1_regs.h

## Purpose

`nic1_qm1_regs.h` defines the auto-generated MMIO register offsets for the Gaudi `NIC1_QM1` QMAN block. The register layout mirrors `NIC1_QM0`, but the address window starts at `mmNIC1_QM1_GLBL_CFG0` offset `0xD22000` and ends at `mmNIC1_QM1_GLBL_MEM_INIT_BUSY` offset `0xD22D00`. `gaudi_blocks.h` defines the full block base as `mmNIC1_QM1_BASE 0x7FFCD22000ull`, with section size `0x2000` and max offset `0xD040`.

## Important APIs, Types, and Macros

This file provides 406 `#define` constants and no functions or data types. It covers global QMAN configuration and protection, secure/non-secure property programming, four PQ rings with base/size/PI/CI/config/status, five CQ rings with config/pointer/transfer-size/control/status, five CP register groups for message bases/LDMA/fences/current instruction/barriers/debug/AXI attributes, arbitration WRR/credit/routing/error registers, CGM status, CSMR strict-priority config, HBW/LBW rate-limit knobs, local range, global AXCACHE, indirect APB gateway, global error capture, and memory-init busy status.

## Control Flow and Integration

There is no executable flow in the header. Driver code uses the constants as MMIO offsets. `gaudi.c` writes `mmNIC1_QM1_GLBL_CFG1` during QMAN stop/stall handling when `HW_CAP_NIC3` is initialized. Queue submission maps `GAUDI_QUEUE_ID_NIC_3_0...GAUDI_QUEUE_ID_NIC_3_3` to doorbell writes beginning at `mmNIC1_QM1_PQ_PI_0`. IRQ handling maps `GAUDI_EVENT_NIC1_QM1` to `mmNIC1_QM1_BASE` and the `NIC1_QM1` description before invoking QMAN error handling. `gaudi_security.c` references `GLBL_CFG1`, `GLBL_NON_SECURE_PROPS_*`, and `PQ_PI_0` to build protection masks.

## State and Persistence Behavior

The header is stateless, but the registers name persistent hardware state. Queue and CP progress are tracked by PQ/CQ indexes and pointers, CP current instruction registers, fence counters, and FIFO counters. Scheduling state is visible through arbitration credit/status registers. Error cause, error drop, global error address, write-data, and memory-init busy registers expose fault and initialization state. Writes persist in the live device until reset or reconfiguration.

## Dependencies

`gaudi_regs.h` includes this header for normal Gaudi builds. `gaudi_blocks.h` supplies the full base address and section metadata. Runtime users depend on Gaudi queue IDs, `HW_CAP_NIC3`, async event `GAUDI_EVENT_NIC1_QM1`, shared NIC QMAN masks, and MMIO helper macros.

## Risks

The major risks are generated-register drift and instance misbinding. A bad offset can corrupt a neighboring NIC/QMAN block or silently ring the wrong queue doorbell. Security-sensitive registers include `GLBL_PROT`, secure/non-secure property registers, AR/AWUSER fields, and the indirect APB gateway. The generated `CHOISE` spelling must remain unchanged because call sites must use the generated names.

## Test Signals

Build coverage should verify inclusion through `gaudi_regs.h`. Runtime signals include NIC3 queue submissions updating the expected `PQ_PI` register, clean QMAN stop through `GLBL_CFG1`, correct IRQ decoding for `GAUDI_EVENT_NIC1_QM1`, security masks containing this instance's non-secure property and doorbell registers, and absence of CP fence/arbitration errors during NIC3 traffic.
