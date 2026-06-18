# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_busmon_0_regs.h

Purpose: generated register map for TPC0 EML bus monitor 0. It exports 70 `mmDCORE0_TPC0_EML_BUSMON_0_*` address constants from `0x7000` to `0x7FFC`.

Important APIs/types/functions: macro-only API for bus-monitor control/reset/interrupt clear, trigger threshold, start/end address windows for monitored regions, event and interrupt registers, counters, match filters, debug/auth/lock registers, and CoreSight-style peripheral/component ID registers.

Control flow: none. External diagnostics or tracing code configures monitor windows and reads counters/status to observe bus activity.

State and persistence behavior: represents trace/monitor hardware configuration and captured counters. State can persist across a running diagnostic session until reset/clear, and lock/auth registers can affect accessibility.

Dependencies and integration points: included by the aggregate register include when EML/trace support needs symbolic addresses. It is conceptually paired with the ETF, funnel, SPMU, and STM EML headers for a trace fabric around TPC0.

Risks: relative-looking addresses in this EML map may be offsets within an EML aperture rather than the absolute DCORE0 TPC CFG range used by other files. Callers must combine them with the correct base. Misconfigured monitor ranges can miss events or leak sensitive address activity through debug interfaces.

Test signals: trace/bus-monitor enable tests, counter increment validation under known TPC traffic, lock/auth access tests, and generated peripheral ID readback checks.
