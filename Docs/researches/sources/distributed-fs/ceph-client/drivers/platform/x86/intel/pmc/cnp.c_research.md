# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/cnp.c

Purpose: supplies Cannon Lake Point PMC platform data and suspend/resume quirks used by Cannon Lake, Comet Lake, and later platform maps that reuse CNP offsets and LTR names.

Important APIs/types/functions: exports `cnp_pfear_map`, `cnp_slps0_dbg_maps`, `cnp_ltr_show_map`, and `cnp_reg_map` for reuse by ICL/TGL/MTL-family files. Defines `cnl_suspend()` and `cnl_resume()`, which are used by many later `pmc_dev_info` records. The per-CPU `pkg_cst_config` stores MSR_PKG_CST_CONFIG_CONTROL values while C1 auto-demotion is disabled.

Control flow: platform init in `core.c` uses `cnp_pmc_dev` to select `cnp_reg_map`. During suspend, `cnl_suspend()` runs `s2idle_cpu_quirk(disable_c1_auto_demote)` unless firmware suspend is used, then ignores GBE LTR index 3 to avoid PC10 blocking with a cable attached. Resume restores the MSR on all CPUs, restores GBE LTR ignore, and calls `pmc_core_resume_common()` for S0ix/PKGC diagnostics.

State and persistence: static per-CPU MSR snapshots persist across suspend/resume only. The PM register map and bit names are static. `cnl_suspend()` also writes the PMC LTR ignore register through `pmc_core_send_ltr_ignore()`, but resume reverses it.

Dependencies and integration points: depends on SMP, suspend mode checks, MSR helpers, and the shared PMC core. `cnp_ltr_show_map` intentionally includes ICL/TGL offsets (`ICL_PMC_LTR_WIGIG`, `TGL_PMC_LTR_THC0/1`) because it is reused by multiple platforms. Debugfs consumers in `core.c` read this map for `ltr_show`, `ltr_ignore`, `slp_s0_debug_status`, and PPFEAR.

Risks: `on_each_cpu()` assumes online CPUs are stable during suspend/resume after userspace freeze. LTR index 3 is positional, so changing `cnp_ltr_show_map` ordering could silently break the GBE quirk. MSR writes affect all online CPUs and should remain limited to s2idle. Shared map extension across generations increases the chance of stale labels.

Test signals: suspend-to-idle tests on CNP-class hardware should show restored MSR values, no persistent GBE LTR ignore after resume, and useful `slp_s0_debug_status` output when `warn_on_s0ix_failures=1`. Compile coverage comes from x86 platform builds using `CONFIG_INTEL_PMC_CORE`.
