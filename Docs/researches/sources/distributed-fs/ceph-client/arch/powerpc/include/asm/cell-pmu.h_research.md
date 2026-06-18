# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/cell-pmu.h

Purpose: defines Cell Broadband Engine PMU counter counts, selected control/status bits, and PMU register names.

Important APIs/types/functions: `NR_PHYS_CTRS` is 4, `NR_CTRS` is 8 logical 16-bit counters, `CBE_PM_16BIT_CTR(ctr)` selects 16-bit counter mode bits in `pm_control`, `CBE_PM_TRACE_BUF_EMPTY` marks trace-buffer empty status, and `enum pm_reg_name` names `group_control`, `debug_bus_control`, `trace_address`, `ext_tr_timer`, `pm_status`, `pm_control`, `pm_interval`, and `pm_start_stop`.

Control flow: declarative only. Cell PMU implementation code uses the enum and macros when reading or programming PMU registers.

State and persistence: PMU state lives in Cell hardware registers and perf event state, not in this header.

Dependencies and integration points: integrates Cell platform PMU code with the PowerPC perf subsystem and Cell register definitions.

Risks: counter-count assumptions are Cell-specific. Incorrect `CBE_PM_16BIT_CTR()` use can configure the wrong physical counter half.

Test signals: build Cell perf configs, run `perf stat`/`perf record` on Cell hardware or simulator, and verify 32-bit versus 16-bit counter mode behavior.
