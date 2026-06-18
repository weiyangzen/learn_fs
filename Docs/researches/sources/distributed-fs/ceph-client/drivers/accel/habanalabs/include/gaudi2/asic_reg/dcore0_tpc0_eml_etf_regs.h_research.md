# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_etf_regs.h

Purpose: generated register map for the TPC0 EML embedded trace FIFO. It exports 45 `mmDCORE0_TPC0_EML_ETF_*` constants from `0x2004` to `0x2FFC`.

Important APIs/types/functions: macro-only API for ETF RAM size/status/read/write pointers, trigger/control/mode registers, buffer levels/watermarks, formatter flush/status controls, integration test registers, claim/lock/auth registers, and component ID registers.

Control flow: none. Trace control code uses these constants to enable buffering, flush captured trace data, and inspect FIFO state.

State and persistence behavior: names trace buffer state and configuration. Captured trace data and pointers persist until drained, reset, flushed, or overwritten according to hardware mode.

Dependencies and integration points: part of the EML trace fabric with SPMU event source, STM stimulus, funnel routing, and bus monitor sources. Included through the Gaudi2 register aggregation path if EML headers are referenced by driver diagnostics.

Risks: trace FIFO control is sensitive to ordering: enabling, flushing, and pointer reads must follow hardware rules. Wrong base interpretation can access unrelated trace registers. Trace capture can expose workload behavior.

Test signals: trace capture/flush tests, buffer watermark behavior under generated events, component ID readback, and generated map comparison to CoreSight/EML specifications.
