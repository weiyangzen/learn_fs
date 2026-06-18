# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic3_qm1_regs.h

## Purpose

`nic3_qm1_regs.h` is the generated register-offset map for the Gaudi `NIC3_QM1` QMAN block. It mirrors the other NIC QMAN maps with instance-specific names and address constants. The first local offset is `mmNIC3_QM1_GLBL_CFG0 0xDA2000`, the last is `mmNIC3_QM1_GLBL_MEM_INIT_BUSY 0xDA2D00`, and the full block base in `gaudi_blocks.h` is `mmNIC3_QM1_BASE 0x7FFCDA2000ull`.

## Important APIs, Types, and Macros

Only macros are defined. The 406 constants cover global control and status, protection and security property registers, producer queue setup/doorbell/status for four PQs, completion queue setup/status/pointer/control for five CQs, five command-processor register groups for message bases/LDMA/fences/current instruction/barriers/debug/AXI attributes, arbitration scheduler and credit state, CGM, strict priority, bandwidth rate limits, local range, AXCACHE, indirect APB access, global error capture, and memory initialization status.

## Control Flow and Integration

The file has no branches or functions. `gaudi.c` uses `mmNIC3_QM1_GLBL_CFG1` for QMAN stop handling under `HW_CAP_NIC7`; it computes queue doorbells for `GAUDI_QUEUE_ID_NIC_7_0...GAUDI_QUEUE_ID_NIC_7_3` from `mmNIC3_QM1_PQ_PI_0`; and it maps `GAUDI_EVENT_NIC3_QM1` to `mmNIC3_QM1_BASE` for common QMAN error reporting and recovery. `gaudi_security.c` uses selected offsets from the same header for protection-bit masks.

## State and Persistence Behavior

There is no C-level persistence, but the referenced hardware registers hold persistent device configuration and live queue state. Queue ring addresses/sizes, producer indexes, completion pointers, command-processor fences and current instructions, arbitration credits, and error registers remain meaningful across driver operations until reset or reconfiguration. Some status registers are hardware-updated as work progresses.

## Dependencies

The header participates in the aggregate register namespace via `gaudi_regs.h`. Full base and section metadata come from `gaudi_blocks.h`; shared masks and bit fields come from NIC0 QMAN masks due to layout reuse. Runtime call sites depend on Gaudi queue IDs, async event IDs, `HW_CAP_NIC7`, and MMIO helpers.

## Risks

The register window is adjacent to `NIC3_QM0`, so prefix mistakes can be hard to spot but severe. Wrong constants in queue PI, queue base, CQ pointer, or CP fence registers can hang queue processing or corrupt command submission. Security-sensitive properties and the indirect APB gateway require careful mask coverage. The generated names, including misspellings such as `CHOISE`, should be treated as fixed generated interface.

## Test Signals

Signals include successful compile, NIC7 queue submissions writing the expected producer-index offsets, clean stop/stall transitions via `GLBL_CFG1`, `GAUDI_EVENT_NIC3_QM1` handled as `NIC3_QM1`, security masks including this instance's non-secure properties and doorbells, and stable hardware runs with no unexpected CP fence or arbitration errors.
