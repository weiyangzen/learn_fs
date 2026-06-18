# sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx27.c

Purpose: i.MX27 suspend support that disables main/system PLL bits before WFI.

Important APIs/types/functions: Defines `mx27_suspend_enter()`, `mx27_suspend_ops`, and `imx27_pm_init()`.

Control flow: On suspend-to-mem, it finds and maps `fsl,imx27-ccm`, clears MPEN/SPEN in the CCM CSCR register, then executes `cpu_do_idle()`. Init installs suspend ops accepting only memory suspend.

State and persistence: Persists a modified CCM register value across idle/resume according to hardware behavior; no software state is cached. The mapped CCM address is not explicitly unmapped.

Dependencies and integration points: Depends on DT CCM node, i.MX relaxed accessors, Linux suspend core, and ARM idle path.

Risks: `BUG_ON(!ccm_base)` makes missing CCM fatal. `of_find_compatible_node()` result is not `of_node_put()` released and the mapping is not unmapped. Clearing PLL bits is board-sensitive and assumes wake/reset sequencing restores clocks correctly.

Test signals: Suspend/resume on i.MX27 hardware, verify clocks after resume, and check DT node presence.
