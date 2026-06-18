# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/nic0_qm0_regs.h

## Purpose

`nic0_qm0_regs.h` is the auto-generated register address map for the Gaudi NIC0 QM0 QMAN instance. It exports 406 `mmNIC0_QM0_*` constants from `mmNIC0_QM0_GLBL_CFG0` at `0xCE0000` through `mmNIC0_QM0_GLBL_MEM_INIT_BUSY` at `0xCE0D00`. It gives the driver the base instance used to initialize NIC QMANs and to derive offsets for additional NIC QMAN blocks.

## Important APIs, types, and functions

There are no functions or types. The address macros follow the shared QMAN layout:

- `GLBL_*`: global config, protection, error config/capture, secure/non-secure properties, status, message enables, AXCACHE, and memory-init busy.
- `PQ_*`: four producer queues with base, size, PI, CI, config, AXI user, and status registers.
- `CQ_*`: five completion queue config/status/pointer/transfer/control and IFIFO registers.
- `CP_*`: command processor message base registers, LDMA offsets, fences, status, current instruction, barrier, debug, and AXI user registers.
- `ARB_*`: arbiter config, WRR, master/slave credits, message properties, base, state, error, and credit status.
- `CGM_*`, `LOCAL_RANGE_*`, `CSMR_STRICT_PRIO_CFG`, rate-limiter, and indirect APB gateway registers.

## Control flow

The header itself has no runtime control flow. `gaudi_init_nic_qman()` uses `mmNIC0_QM0_*` addresses plus a `nic_offset` and per-stream `q_off` to program PQ DMA base/size/indices, CP LDMA offsets, CP message bases, global error config and error message target, arbiter error message enable, watchdog timeout, global config/protection, and final QMAN enable. `gaudi_init_nic_qmans()` computes offsets using `mmNIC0_QM1_GLBL_CFG0 - mmNIC0_QM0_GLBL_CFG0` and `mmNIC1_QM0_GLBL_CFG0 - mmNIC0_QM0_GLBL_CFG0`, making this header the anchor for NIC QMAN address arithmetic.

## State and persistence behavior

The defines are compile-time constants. The hardware registers hold queue-manager state such as PQ base DMA addresses, PI/CI values, CP message base addresses for sync manager objects, LDMA offsets, error handler addresses/data, arbiter watchdog/configuration, protection trust, and enable bits. These values persist in the NIC QMAN until reset, port disablement, or reinitialization. Runtime doorbells write producer indices to `PQ_PI_*` registers derived from this map.

## Dependencies and integration points

`gaudi_regs.h` includes this file, and `nic0_qm0_masks.h` supplies bitfield definitions for its registers. `gaudiP.h` defines NIC QMAN macro and engine offsets from base constants. `gaudi.c` integrates this map with NIC port mask handling, queue initialization, queue doorbell selection, power/idle checks, MMU non-secure property programming, RAZWI/error IRQ routing, and debug engine dumps. It also cooperates with sync-manager register maps because CP message bases point to monitor and SOB objects.

## Risks

Because offset arithmetic for multiple NIC ports is anchored on NIC0 QM0, a wrong base or register ordering error can propagate to many NIC instances. Per-stream arithmetic assumes each queue's related registers are spaced regularly by four bytes in the generated order. Misaddressed PQ/CP registers can corrupt DMA queue pointers or sync-manager message bases, while wrong global error registers can suppress or misroute RAZWI/error interrupts. This header must be kept consistent with `nic0_qm0_masks.h`.

## Test signals

Signals include successful Gaudi build, NIC QMAN initialization for enabled ports, queue submissions on NIC0 streams, producer-index doorbells, sync-stream collective message-base behavior, NIC QMAN RAZWI/error interrupt handling, stop/disable paths, idle checks using `GLBL_STS0` and `CGM_STS`, and MMU ASID property programming. Static tests should verify that normalized QMAN register names match `nic0_qm1_regs.h` and `mme2_qm_regs.h` where the layout is shared.
