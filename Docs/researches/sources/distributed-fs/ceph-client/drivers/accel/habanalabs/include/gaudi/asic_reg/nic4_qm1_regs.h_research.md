# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic4_qm1_regs.h

## Purpose

`nic4_qm1_regs.h` defines the generated MMIO offsets for the Gaudi `NIC4_QM1` QMAN block, the QM1 queue manager for the last NIC instance covered by this group. Its local range starts at `mmNIC4_QM1_GLBL_CFG0 0xDE2000` and ends at `mmNIC4_QM1_GLBL_MEM_INIT_BUSY 0xDE2D00`. `gaudi_blocks.h` maps the full base as `mmNIC4_QM1_BASE 0x7FFCDE2000ull`, with section size `0x2000` and max offset `0xD040`.

## Important APIs, Types, and Macros

The file exports only register-offset macros. The 406 definitions follow the shared QMAN structure: global config, protection, properties, statuses, and message enables; PQ base/size/PI/CI/config/ARUSER/status for four producer queues; CQ config/status/pointer/transfer/control and IFIFO counters for five completion queues; CP message-base, LDMA, fence, current-instruction, barrier, debug, ARUSER, and AWUSER registers for five command processors; arbitration WRR, credit, choice, routing, message, status, error, and credit-status registers; and CGM, strict priority, rate limiting, local range, AXCACHE, indirect APB, global error, and memory-init registers.

## Control Flow and Integration

There is no executable code in the header. In the driver, `mmNIC4_QM1_GLBL_CFG1` is used to stop/stall the QMAN when `HW_CAP_NIC9` is present. Queue submission for `GAUDI_QUEUE_ID_NIC_9_0...GAUDI_QUEUE_ID_NIC_9_3` writes doorbells starting at `mmNIC4_QM1_PQ_PI_0`. Async error handling maps `GAUDI_EVENT_NIC4_QM1` to `mmNIC4_QM1_BASE`, labels the block `NIC4_QM1`, and calls common QMAN error handling. Security setup uses this instance's global and non-secure property offsets when computing protection masks.

## State and Persistence Behavior

The file does not persist C state. It names live MMIO registers whose values persist in the device across queue operations until reset or reprogramming. Important mutable state includes queue indexes and base/size registers, completion queue pointers and controls, command-processor fences and current instruction addresses, arbitration credits and routing, global error capture, and memory-init busy state.

## Dependencies

The header is part of the aggregate Gaudi register set through `gaudi_regs.h`. It relies on `gaudi_blocks.h` for the full physical/MMIO block base. Consumers use shared QMAN masks, Gaudi queue IDs, `HW_CAP_NIC9`, async event `GAUDI_EVENT_NIC4_QM1`, and low-level MMIO helpers.

## Risks

This instance is the final NIC QMAN in the Gaudi NIC set, so off-by-one NIC capability, queue ID, or event mappings can leave it uninitialized or can direct traffic into the wrong block. Security/property and indirect-gateway registers are sensitive. Doorbell offsets must remain exactly aligned at four-byte intervals from `PQ_PI_0`. Manual edits to generated names or offsets would carry high hardware risk.

## Test Signals

Signals include compile coverage, NIC9 queue doorbells landing at `mmNIC4_QM1_PQ_PI_0 + lane * 4`, QMAN stop writes through `GLBL_CFG1`, `GAUDI_EVENT_NIC4_QM1` reported and recovered as this block, security masks for `GLBL_NON_SECURE_PROPS_*` and `PQ_PI_0`, and stress or hardware validation runs without CP, arbitration, or global QMAN error causes.
