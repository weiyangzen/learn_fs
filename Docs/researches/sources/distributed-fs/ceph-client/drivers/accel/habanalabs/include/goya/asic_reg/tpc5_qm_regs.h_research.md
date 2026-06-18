## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc5_qm_regs.h

Purpose: auto-generated TPC5 QMAN register map with 78 `mmTPC5_QM_*` offsets from `0xF48000` to `0xF4830C`.

Important API surface: QMAN global registers, PQ configuration/base/size/indices/push/status/rate-limiting, CQ configuration/pointers/control/status/rate-limiting, CP message and LDMA offsets, fence/counter/current-instruction/barrier/debug registers, and queue buffer readback windows.

Control flow and state: this file only names registers. TPC queue initialization and execution code writes PQ/CQ/CP values and polls or handles status/fence progress. Hardware retains these values until reset/reprogramming.

Dependencies and integration: included by `goya_regs.h`, paired with `mmTPC5_QM_BASE` and `TPC5_QM_SECTION` in `goya_blocks.h`, and linked to async event ID `GOYA_ASYNC_EVENT_ID_TPC5_QM`.

Risks and test signals: single-TPC address skew can send writes into adjacent blocks. Test TPC5-specific QMAN bring-up, queue stress, MMU/security attribute programming, fence counters, and generated map parity with TPC3/4/6/7 normalized layouts.
