## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc4_qm_regs.h

Purpose: auto-generated TPC4 queue-manager register map. It defines 78 `mmTPC4_QM_*` offsets from `0xF08000` to `0xF0830C`, corresponding to `mmTPC4_QM_BASE`.

Important API surface: global configuration/protection/error/status, PQ base/size/PI/CI/config/ARUSER/push/status/rate-limiter registers, CQ config/pointer/size/control/status/read-rate-limit registers, CQ FIFO count, CP message bases, CP LDMA offsets, fence data/counters, current instruction, barrier/debug, and PQ/CQ buffer readback registers.

Control flow and state: the header is declarative. Queue setup code writes PQ/CQ descriptors and pushes producer indices; hardware advances consumer indices and fence counters. Register contents are transient device state and are not persisted by software.

Dependencies and integration: included by `goya_regs.h`; TPC QMAN SRAM placement in `goyaP.h` depends on the shared QMAN model, and async events map TPC4 QM faults to `GOYA_ASYNC_EVENT_ID_TPC4_QM`.

Risks and test signals: offset drift breaks queue submission, MMU attributes, queue-status polling, or protection-bit setup. Test with TPC4 QMAN queue tests, command submission under load, fence wait/timeout paths, MMIO security checks, and generated register-map comparisons.
