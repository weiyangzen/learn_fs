# sources/distributed-fs/ceph-client/drivers/clk/hisilicon/clk-hi3660.c

Purpose: registers Hi3660 clock providers across CRGCTRL, PCTRL, PMUCTRL, SCTRL, and IOMCU domains using shared HiSilicon clock helpers.

Important APIs/types/functions: descriptor arrays cover fixed rates, CRG fixed factors, separated gates, hiword gates, muxes, dividers, PMU/PCTRL gates, SCTRL gates/muxes/dividers, and IOMCU gates. `clk_crgctrl_data` is initialized early by `hi3660_clk_crgctrl_early_init()`. Domain init functions include `hi3660_clk_crgctrl_init()`, `hi3660_clk_pctrl_init()`, `hi3660_clk_pmuctrl_init()`, `hi3660_clk_sctrl_init()`, and `hi3660_clk_iomcu_init()`.

Control flow: CRGCTRL has an early `CLK_OF_DECLARE_DRIVER` path that registers fixed roots and fills all clock slots with `-EPROBE_DEFER`, allowing early consumers to defer until the platform driver registers the rest. Platform probe dispatches to the init function stored in the OF match table. Each domain maps/registers its own onecell provider via `hisi_clk_init()` and the relevant descriptor arrays.

State and persistence: each hardware block keeps register state in its own MMIO region. Software state is in `hisi_clock_data` objects and the global CRGCTRL pointer.

Dependencies and integration points: uses `dt-bindings/clock/hi3660-clock.h`, shared `clk.h`, OF early declaration, platform driver `core_initcall()`, and common-clock hiword mask semantics.

Risks: descriptor-only errors are hard to detect until consumers request clocks. Some gate entries use `CLK_DIVIDER_HIWORD_MASK` where gate flags might be expected, which deserves review against helper semantics. CRGCTRL global state is singleton and assumes one controller. Unregistered `-EPROBE_DEFER` slots are logged only after full registration.

Test signals: boot with early serial/storage consumers, verify deferral resolves after platform probe, inspect clock summary across all domains, test UFS critical clock suspend/resume, and check all binding IDs map to non-error clocks where hardware supports them.
