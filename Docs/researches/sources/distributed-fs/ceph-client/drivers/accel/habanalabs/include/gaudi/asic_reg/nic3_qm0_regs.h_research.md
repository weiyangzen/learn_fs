# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic3_qm0_regs.h

## Purpose

`nic3_qm0_regs.h` defines the generated register names and offsets for the Gaudi `NIC3_QM0` queue manager. The local address range starts at `mmNIC3_QM0_GLBL_CFG0 0xDA0000` and extends through `mmNIC3_QM0_GLBL_MEM_INIT_BUSY 0xDA0D00`. `gaudi_blocks.h` pairs this with `mmNIC3_QM0_BASE 0x7FFCDA0000ull`, section `0x2000`, max offset `0xD040`.

## Important APIs, Types, and Macros

The header exports only 406 `#define` constants. Register groups include global configuration/protection/status and message-enable controls; secure and non-secure global properties; producer queue base/size/PI/CI/config/ARUSER/status registers for four PQs; completion queue config/status/pointer/transfer/control/IFIFO registers for five CQs; command processor message-base, LDMA, fence, current-instruction, barrier, debug, ARUSER, and AWUSER registers for five CPs; arbitration WRR, credits, choice offsets, routing, state, error, and credit status registers; plus clock-gating, priority, bandwidth limit, local range, AXCACHE, APB indirect gateway, and global error/mem-init registers.

## Control Flow and Integration

No executable code is present. In the Gaudi runtime, `mmNIC3_QM0_GLBL_CFG1` is used in QMAN stop handling for `HW_CAP_NIC6`. Queue doorbells for `GAUDI_QUEUE_ID_NIC_6_0...GAUDI_QUEUE_ID_NIC_6_3` are computed from `mmNIC3_QM0_PQ_PI_0`. QMAN error handling maps `GAUDI_EVENT_NIC3_QM0` to `mmNIC3_QM0_BASE`, labels the block `NIC3_QM0`, and routes through the common QMAN error printer/handler. Security code derives protection masks from `GLBL_CFG1`, `GLBL_NON_SECURE_PROPS_*`, and `PQ_PI_0`.

## State and Persistence Behavior

The register definitions expose hardware state. Queue, completion, CP, arbitration, and error-status registers reflect live device state and are updated by both driver writes and hardware progress. Configuration writes persist until the NIC QMAN block is reset or reprogrammed. The `GLBL_MEM_INIT_BUSY` and global error registers are important for initialization and fault diagnosis.

## Dependencies

The file is included by `gaudi_regs.h`, while base address metadata comes from `gaudi_blocks.h`. Consumers rely on shared NIC QMAN masks, Gaudi queue/event IDs, `HW_CAP_NIC6`, and MMIO access helpers. There are no local include dependencies beyond the include guard.

## Risks

Incorrect offsets can affect the wrong QMAN instance or corrupt live queue state. Doorbell and queue base registers are high-risk because small arithmetic mistakes can submit work to the wrong producer queue. Security risks involve global protection, non-secure property, AR/AWUSER, and indirect-gateway registers. Since the file is generated, manual edits may be overwritten or may desynchronize from hardware documentation.

## Test Signals

Useful checks are build coverage through `gaudi_regs.h`, NIC6 queue traffic causing expected `PQ_PI` writes, correct `GLBL_CFG1` stop behavior, correct `GAUDI_EVENT_NIC3_QM0` diagnostics, protected-register masks matching the `0xDA0000` register window, and no unexpected QMAN error causes or arbitration credit exhaustion during NIC3/QM0 workloads.
