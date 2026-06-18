# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic4_qm0_regs.h

## Purpose

`nic4_qm0_regs.h` defines the auto-generated register constants for the Gaudi `NIC4_QM0` QMAN block. It provides the driver's symbolic view of the QM0 queue manager attached to NIC4. The local offsets run from `mmNIC4_QM0_GLBL_CFG0 0xDE0000` through `mmNIC4_QM0_GLBL_MEM_INIT_BUSY 0xDE0D00`; `gaudi_blocks.h` defines `mmNIC4_QM0_BASE 0x7FFCDE0000ull`, section `0x2000`, and max offset `0xD040`.

## Important APIs, Types, and Macros

This is a macro-only register map. It defines global configuration/protection/security/status registers; four producer queue register sets for base, size, producer/consumer indexes, configuration, ARUSER, and status; five completion queue register sets for configuration, status, pointer, transfer size, control, latched state, and IFIFO count; five command-processor register sets for message bases, LDMA offsets, fences, current instruction, barriers, debug, and AXI user properties; arbitration configuration, WRR weights, credits, choice offsets, master/slave controls, message attributes, status, and errors; and miscellaneous CGM, CSMR, HBW/LBW rate-limit, local range, AXCACHE, indirect-gateway, global error, and memory-init registers.

## Control Flow and Integration

The header is passive. `gaudi.c` writes `mmNIC4_QM0_GLBL_CFG1` as part of stop/stall handling for initialized `HW_CAP_NIC8`. Doorbell routing for `GAUDI_QUEUE_ID_NIC_8_0...GAUDI_QUEUE_ID_NIC_8_3` uses `mmNIC4_QM0_PQ_PI_0` plus a lane offset. Error routing maps `GAUDI_EVENT_NIC4_QM0` to `mmNIC4_QM0_BASE` and sends the event to common QMAN diagnostics/recovery. Security code references the same offsets to build register access masks.

## State and Persistence Behavior

No software state is defined here. The hardware state represented by these offsets includes queue ring location/size/progress, completion ring pointers, command-processor state and fences, arbitration scheduler credits, status/error registers, and memory initialization. Configuration and property writes persist in the QMAN hardware until reset or later programming.

## Dependencies

`gaudi_regs.h` includes this header, and `gaudi_blocks.h` defines the full base address. Runtime users also rely on common QMAN bit masks, `HW_CAP_NIC8`, queue and async event definitions, and MMIO read/write helpers. The file itself has no include dependencies other than its guard.

## Risks

Because `NIC4_QM0` is near the end of the NIC QMAN address range, copy/paste mistakes can accidentally target `NIC3` or `NIC4_QM1`. Queue doorbells, CP controls, and security property registers are sensitive to exact offsets. Generated register names should not be normalized or renamed manually. Any protection-mask omission can accidentally expose QMAN control registers to non-secure access.

## Test Signals

Expected evidence includes build success, correct NIC8 queue doorbells from `mmNIC4_QM0_PQ_PI_0`, stop writes to `GLBL_CFG1`, correct `GAUDI_EVENT_NIC4_QM0` logging and recovery, protection masks for this window, and stress tests without QMAN global, CP, or arbitration errors.
