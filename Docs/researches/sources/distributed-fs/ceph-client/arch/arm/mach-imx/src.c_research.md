# sources/distributed-fs/ceph-client/arch/arm/mach-imx/src.c

Purpose: i.MX System Reset Controller support for reset-controller consumers and secondary CPU boot/resume registers.

Important APIs/types/functions: Defines `imx_src_init()`, `imx7_src_init()`, `imx_enable_cpu()`, `imx_set_cpu_jump()`, `imx_get_cpu_arg()`, `imx_set_cpu_arg()`, `imx_gpcv2_set_core1_pdn_pup_by_software()`, `imx_src_reset_module()`, and the `imx-src` platform driver.

Control flow: Early init maps SRC for i.MX51 or i.MX7D and clears warm-reset behavior where applicable. Reset-controller probe exposes five software reset lines for GPU/VPU/IPU/OpenVG/IPU2 by setting SCR bits and polling for auto-clear. SMP helpers write boot jump/argument GPRs and enable or reset cores; i.MX7D powers core1 through GPCv2 before toggling A7RCR1.

State and persistence: Global state includes `src_base`, `gpc_base`, `gpr_v2`, and `scr_lock`. Hardware state includes SRC SCR/A7RCR1/GPR boot slots, GPC CPU PGC software power-up/down requests, and reset bits.

Dependencies and integration points: Depends on reset-controller framework, DT compatible nodes, SMP CPU logical mapping, i.MX GPCv2, and `platsmp.c` callers.

Risks: Spinlock covers SRC writes but `imx_gpcv2_set_core1_pdn_pup_by_software()` is called under it and polls atomically, so timing matters. Missing SRC/GPC silently disables some paths. Reset timeout is fixed at 1s. The `fsl,imx51-src` match table is broad for later SoCs using compatible inheritance.

Test signals: Test reset-controller consumers, secondary CPU boot/hotplug on i.MX6/i.MX7, and timeout behavior with invalid reset ids.
