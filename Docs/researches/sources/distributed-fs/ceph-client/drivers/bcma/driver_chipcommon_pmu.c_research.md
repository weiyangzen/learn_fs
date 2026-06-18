# sources/distributed-fs/ceph-client/drivers/bcma/driver_chipcommon_pmu.c

Purpose: this file implements BCMA ChipCommon PMU support: indirect PLL/chip/reg control access, crystal measurement, PLL initialization, resource masks, chip workarounds, ALP/bus/CPU clock derivation, and spur-avoidance PLL programming.

Important APIs, types, and functions: exported helpers include `bcma_chipco_pll_read`, `bcma_chipco_pll_write`, `bcma_chipco_pll_maskset`, `bcma_chipco_chipctl_maskset`, `bcma_chipco_regctl_maskset`, `bcma_chipco_bcm4331_ext_pa_lines_ctl`, `bcma_pmu_early_init`, `bcma_pmu_init`, `bcma_pmu_get_alp_clock`, `bcma_pmu_get_bus_clock`, `bcma_pmu_get_cpu_clock`, and `bcma_pmu_spuravoid_pllupdate`. Internal helpers compute xtal frequency, initialize PMU2 PLL target frequency, configure min/max resource masks, apply chip-specific workarounds, and calculate PLL outputs.

Control flow: early init selects a separate PMU core when AOB PMU is present, otherwise uses ChipCommon, reads PMU capability revision, and logs it. Full init toggles `NOILPONW` according to PMU revision, initializes PLL for specific chips, sets resource masks, and applies workarounds. Clock getters switch on chip IDs to return fixed ALP clocks or calculated PLL clocks. Spur-avoidance updates choose chip-family-specific PLL control register values, then set `PLL_UPD` and sometimes preserve/add `NOILPONW`.

State and persistence: PMU state is held in `cc->pmu.core` and `cc->pmu.rev`; most lasting state is hardware register programming in PMU PLL, chip-control, resource-mask, and control registers.

Dependencies and integration points: it depends on ChipCommon register accessors, public BCMA chip IDs/constants, the core `bcma_wait_value` helper, PMU register macros, and chip-specific radio/SoC bring-up expectations. MIPS clock code and watchdog timing consume CPU/bus/ALP clock helpers.

Risks: this file is highly chip-specific; wrong constants can destabilize clocks, power resources, wireless PHY behavior, or external PA lines. Several unknown-chip paths fall back to default clocks and warnings, which may be insufficient for new hardware. `BUG_ON` guards in PLL calculations can panic if called with invalid PLL index/divider. Spur-avoidance array indexing assumes valid `spuravoid` values.

Test signals: board boot stability, clock rate correctness, wireless operation, watchdog timing, and absence of PMU warnings are key signals. Hardware matrix testing across listed chip IDs is more important than synthetic tests.
