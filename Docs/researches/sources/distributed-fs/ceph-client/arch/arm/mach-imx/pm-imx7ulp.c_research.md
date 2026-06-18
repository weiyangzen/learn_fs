# sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx7ulp.c

Purpose: i.MX7ULP System Mode Controller low-power mode setup.

Important APIs/types/functions: Defines `imx7ulp_set_lpm()` and `imx7ulp_pm_init()`, plus SMC PMCTRL field constants for RUN/WAIT/STOP post-stop options.

Control flow: Init maps the `fsl,imx7ulp-smc1` node and programs RUN mode. `imx7ulp_set_lpm()` clears RUNM/STOPM/PSTOPO fields, selects PSTOP3 for run, PSTOP2 for wait, or PSTOP1 for stop, and writes SMC_PMCTRL.

State and persistence: Global state is `smc1_base`; hardware state is SMC PMCTRL low-power mode selection.

Dependencies and integration points: Depends on DT SMC node, i.MX ULP power-mode enum from common headers, and callers in cpuidle/PM paths.

Risks: `smc1_base` is only warning-checked; callers before successful init would dereference NULL. The helper does not serialize access or validate wake-source policy.

Test signals: Boot i.MX7ULP, verify init maps SMC, exercise cpuidle/low-power transitions for RUN/WAIT/STOP, and validate resume clocks.
