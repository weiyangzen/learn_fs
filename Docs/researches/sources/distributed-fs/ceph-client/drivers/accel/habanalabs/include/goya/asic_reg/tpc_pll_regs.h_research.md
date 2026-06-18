## sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/tpc_pll_regs.h

Purpose: auto-generated TPC PLL register map. It defines 41 `mmTPC_PLL_*` offsets from `0xE01100` through `0xE01440` for configuring, resetting, gating, dividing, and monitoring the TPC clock PLL.

Important API surface: PLL numerator/denominator/output divider/config registers (`NR`, `NF`, `OD`, `NB`, `CFG`), lock/loss interrupt and bypass controls, data-change and reset registers, slip watchdog counter, four divider factor registers plus command/busy/select/enable sets, clock gater and clock relax registers, reference counter period and low/high thresholds, not-stable status, and frequency calculation enable.

Control flow and state: no functions. Clock-management code writes PLL/divider/reset/gate controls and reads lock/busy/stability/frequency status. State persists in clock hardware while powered.

Dependencies and integration: included early in `goya_regs.h`; `goyaP.h` defines default TPC PLL frequency-related values and `goya.c` exposes PLL/clock profile operations.

Risks and test signals: bad PLL offsets can destabilize every TPC, cause hangs, or report wrong telemetry. Test PLL profile changes, lock interrupt handling, frequency calculation, busy polling, clock gating, and recovery after reset.
