# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_stm_regs.h

Purpose: generated register map for the TPC0 EML system trace macrocell. It exports 54 `mmDCORE0_TPC0_EML_STM_*` constants from `0x3C04` to `0x3FFC`.

Important APIs/types/functions: macro-only API for STM DMA start/stop/status/control, hardware event enable/trigger/bank/mux registers, stimulus features, synchronization/access controls, integration test controls, claim/lock/auth, device architecture/type, peripheral IDs, and component IDs.

Control flow: none. External trace code configures STM stimulus/event generation and DMA behavior as part of hardware trace capture.

State and persistence behavior: STM configuration and DMA state live in hardware. Values persist for the trace session and can emit trace packets or DMA trace data depending on mode.

Dependencies and integration points: part of the EML CoreSight-like trace fabric with funnel and ETF. It may consume events from TPC logic and emit them to downstream trace buffers.

Risks: trace DMA and stimulus configuration are ordering-sensitive. Wrong addresses or base selection can corrupt trace setup. Debug trace output can expose sensitive workload timing.

Test signals: STM event generation tests, DMA start/stop behavior, downstream trace visibility through funnel/ETF, lock/auth access tests, and ID register readback.
