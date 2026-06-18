# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/sleep34xx.S

## Purpose
Provides OMAP34xx/36xx low-level suspend and restore code for retention/off modes, including secure RAM context save, cache handling, SDRC self-refresh/DLL recovery, ROM-code restore entry points, and SDRC errata workarounds.

## APIs, Flow, And State
Exports `enable_omap3630_toggle_l2_on_restore`, `save_secure_ram_context`, `omap34xx_cpu_suspend`, `omap3_do_wfi`, `omap3_do_wfi_sz`, `omap3_restore_es3`, `omap3_restore_3630`, `omap3_restore`, `es3_sdrc_fix`, and `es3_sdrc_fix_sz`. Suspend flow selects SRAM WFI when no context is lost, otherwise flushes caches, disables the C bit, invalidates cache, and enters WFI code. WFI flow sets SDRC self-refresh-on-idle, executes WFI, waits for DPLL3 and SDRC readiness, clears self-refresh, waits/kicks DLL if needed, re-enables cache, and returns for non-off modes. OFF-mode restore is entered by ROM, handles ES3 SDRC erratum i443, OMAP3630 RTA disable, L2 invalidate/secure service calls, scratchpad state, optional L2 aux restore, and branches to `cpu_resume`.

## Dependencies And Integration
Uses OMAP34xx PRM/CM/SDRC/control/SRAM physical addresses, secure monitor calls, scratchpad memory, and generic ARM resume. It is copied partly to internal SRAM by PM setup code.

## Risks And Test Signals
This is highly silicon-revision-specific and runs with MMU/cache constraints. Bad scratchpad, secure monitor, or SDRC sequencing causes resume failure or memory corruption. Test signals are OMAP3430 ES3 off-mode, OMAP3630 L2 restore toggling, secure device suspend, SDRC DLL relock, and resume through `cpu_resume`.
