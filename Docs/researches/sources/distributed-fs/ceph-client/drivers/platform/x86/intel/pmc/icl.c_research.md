# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/icl.c

Purpose: defines the Ice Lake PMC regmap by extending Cannon Lake PPFEAR with Ice Lake-specific entries and adjusting counter units and limits.

Important APIs/types/functions: `icl_pfear_map` adds RES/TAM/GBETSN/TBTLSX bits beyond the CNP map. `ext_icl_pfear_map` chains `cnp_pfear_map` plus Ice Lake additions. `icl_reg_map` reuses CNP offsets, SLP_S0 debug maps, LTR map, and ETR3 while setting `ICL_PMC_SLP_S0_RES_COUNTER_STEP`, `ICL_PPFEAR_NUM_ENTRIES`, and `ICL_NUM_IP_IGN_ALLOWED`. `icl_pmc_dev` publishes the map.

Control flow: CPU matching in `core.c` selects `icl_pmc_dev`; no custom init means `generic_core_init()` maps the primary PMC through the legacy LPIT/default base path and debugfs uses the ICL regmap.

State and persistence: no dynamic state. Static maps live for module lifetime; runtime state is in `core.c`.

Dependencies and integration points: depends on CNP exported maps and core constants. Debugfs consumers include `pch_ip_power_gating_status`, `ltr_show`, `slp_s0_debug_status`, and package C-state output.

Risks: because this is mostly inherited CNP behavior, the main risk is over-reuse of CNP LTR/SLP_S0 names on ICL variants. PPFEAR bucket count must match the appended Ice Lake map.

Test signals: on Ice Lake, debugfs PPFEAR should include Ice Lake-specific tail entries and SLP_S0 residency should use the Ice Lake counter step. Basic compile/link verifies `cnp_*` extern usage.
