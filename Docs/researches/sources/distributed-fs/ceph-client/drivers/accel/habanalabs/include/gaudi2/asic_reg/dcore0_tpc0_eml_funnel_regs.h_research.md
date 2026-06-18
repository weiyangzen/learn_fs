# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_funnel_regs.h

Purpose: generated register map for the TPC0 EML trace funnel. It exports 26 `mmDCORE0_TPC0_EML_FUNNEL_*` constants from `0x6000` to `0x6FFC`.

Important APIs/types/functions: macro-only API for funnel control, priority control, integration ATB registers, ITCTRL, claim set/clear, lock access/status, auth status, device architecture/type, peripheral IDs, and component IDs.

Control flow: none. External trace setup code selects and prioritizes trace streams before they flow to downstream trace buffering or collection.

State and persistence behavior: funnel selection and priority registers are hardware routing state. They persist during a trace session and determine which EML sources are forwarded.

Dependencies and integration points: works with `dcore0_tpc0_eml_etf_regs.h`, `dcore0_tpc0_eml_spmu_regs.h`, `dcore0_tpc0_eml_stm_regs.h`, and bus monitor headers. Included via generated register aggregation for diagnostics/debug paths.

Risks: incorrect routing can drop trace streams or combine unexpected sources. Lock/auth fields must be respected to avoid exposing debug trace controls where prohibited.

Test signals: trace-path tests confirming selected sources appear downstream, priority behavior under multiple active sources, component ID readback, and security-mode access tests for lock/auth registers.
