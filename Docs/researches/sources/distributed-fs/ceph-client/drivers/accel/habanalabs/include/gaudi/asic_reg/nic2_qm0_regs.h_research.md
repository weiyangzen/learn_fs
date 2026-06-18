# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic2_qm0_regs.h

## Purpose

`nic2_qm0_regs.h` defines the generated register offsets for Gaudi `NIC2_QM0`, one of the NIC queue-manager instances. Its local window starts at `mmNIC2_QM0_GLBL_CFG0` offset `0xD60000` and ends at `mmNIC2_QM0_GLBL_MEM_INIT_BUSY` offset `0xD60D00`. `gaudi_blocks.h` gives the full base as `mmNIC2_QM0_BASE 0x7FFCD60000ull`, section size `0x2000`, and max offset `0xD040`.

## Important APIs, Types, and Macros

The file has 406 macro definitions and no functions, types, or storage. The exported names cover global QMAN configuration and protection, secure/non-secure property programming, four producer queues, five completion queues, five command processors, arbitration/scheduling and credit accounting, CGM status, strict priority and bandwidth rate-limiter controls, local range, AXCACHE, indirect APB gateway, global error capture, and memory initialization status.

## Control Flow and Integration

The header contributes constants consumed by the Gaudi driver. In `gaudi.c`, `mmNIC2_QM0_GLBL_CFG1` is written with the shared QMAN stop masks when `HW_CAP_NIC4` is active. Queue submission maps `GAUDI_QUEUE_ID_NIC_4_0...GAUDI_QUEUE_ID_NIC_4_3` to `mmNIC2_QM0_PQ_PI_0 + q_off`, where `q_off` is the selected queue lane times four bytes. Async error handling maps `GAUDI_EVENT_NIC2_QM0` to `mmNIC2_QM0_BASE` and dispatches through the common QMAN error path. Security setup references this header's global config, non-secure property, and producer-index registers.

## State and Persistence Behavior

The macros name hardware state rather than C state. Persistent device state includes queue base/size configuration, producer and consumer indexes, completion queue pointers, command-processor message base and fence registers, arbitration credits, error causes, and memory initialization status. These registers are volatile from the CPU perspective but persist in the hardware block until reset or explicit reprogramming.

## Dependencies

The aggregate `gaudi_regs.h` includes the header. Full address metadata is in `gaudi_blocks.h`; common bit masks are shared with the NIC0 QMAN mask header. Runtime integration depends on Gaudi hardware capability `HW_CAP_NIC4`, queue ID definitions, `GAUDI_EVENT_NIC2_QM0`, and low-level MMIO read/write helpers.

## Risks

Offset correctness is critical because this file sits in a distinct NIC2 address window. Misusing `NIC2_QM0` constants for another QMAN instance can stop or ring the wrong queues. Security and isolation risks center on `GLBL_PROT`, secure/non-secure property registers, AR/AWUSER attributes, and the indirect APB gateway. Manual edits would also risk diverging from the hardware register generator.

## Test Signals

Expected signals include successful compilation, NIC4 queue doorbells resolving from `mmNIC2_QM0_PQ_PI_0`, QMAN stop/stall writes to `GLBL_CFG1`, `GAUDI_EVENT_NIC2_QM0` interrupts producing the expected block description, correct security-mask bits for the `0xD60000` window, and hardware runs without unexpected arbitration credit, CP fence, or global error reports.
