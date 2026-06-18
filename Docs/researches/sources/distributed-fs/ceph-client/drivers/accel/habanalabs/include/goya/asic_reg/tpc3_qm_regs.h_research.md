## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc3_qm_regs.h

Purpose: auto-generated Goya TPC3 queue-manager MMIO register map. It exports 78 `mmTPC3_QM_*` address macros from `0xEC8000` through `0xEC830C`, matching `mmTPC3_QM_BASE` in `goya_blocks.h` and included transitively by `goya_regs.h`.

Important API surface: global QMAN configuration/status/protection registers, producer queue registers (`PQ_BASE_*`, `PQ_SIZE`, `PQ_PI`, `PQ_CI`, `PQ_PUSH*`, rate-limit controls), completion queue registers (`CQ_*`, status mirrors, read rate limits, `CQ_IFIFO_CNT`), command processor message base registers, LDMA offsets, fence counters/read data, current instruction, barrier/debug, and queue buffer readback windows.

Control flow and state: this header has no executable flow. Runtime state lives in hardware queues, queue indices, CP fence counters, status registers, and buffer windows accessed by driver `RREG32`/`WREG32` paths. Persistence is only hardware-visible register state; the file itself is generated constants.

Dependencies and integration: consumers rely on exact offsets relative to Goya CFG space. `goya_security.c` uses TPC3 QM addresses to configure protection bits, and QMAN setup/test paths depend on compatible PQ/CQ layout and `QMAN_PQ_ENTRY_SIZE`.

Risks and test signals: wrong offsets can break queue submission, interrupt completion, security windows, or fence waits. Test via queue bring-up, TPC QMAN self-tests, MMIO access fault checks, security protection-bit validation, and compile checks after regenerating bitfield headers.
