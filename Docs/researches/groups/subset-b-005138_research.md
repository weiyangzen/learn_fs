# subset-b-005138 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/arl.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/arl.c

Purpose: adds Arrow Lake PMC platform descriptions to the shared Intel PMC core driver. The file is almost entirely data-driven: it describes ARL SoC-S and PCH-S LTR, PPFEAR, LPM status, D3, VNN, signal, residency, and telemetry layouts, then publishes `arl_pmc_dev` and `arl_h_pmc_dev` for CPU matching in `core.c`.

Important APIs/types/functions: `struct pmc_bit_map` arrays encode register bit names and optional blocker strides; `struct pmc_reg_map` instances `arl_socs_reg_map` and `arl_pchs_reg_map` bind those arrays to offsets and telemetry GUIDs; `struct pmc_info arl_pmc_info_list[]` maps SSRAM device IDs to regmaps. `arl_d3_fixup()` and `arl_h_d3_fixup()` call `pmc_core_set_device_d3()` for NPU/GNA PCI IDs lacking drivers. `arl_core_init()`, `arl_h_core_init()`, `arl_resume()`, and `arl_h_resume()` wrap the generic PMC init/resume path with those D3 fixups. Public integration is through `arl_pmc_dev` and `arl_h_pmc_dev`.

Control flow: `core.c` selects `arl_pmc_dev` for `INTEL_ARROWLAKE` and `arl_h_pmc_dev` for Arrow Lake H/U. Their init callbacks run the platform-specific D3 fixup, then delegate to `generic_core_init()`. Because `regmap_list` is set, generic init attempts SSRAM enumeration, maps each discovered PMC by device ID through `arl_pmc_info_list`, reads enabled LPM modes, registers PUNIT DMU telemetry using `ARL_PMT_DMU_GUIDS` or `ARL_H_PMT_DMU_GUIDS`, and reads LPM requirement data through `pmc_core_pmt_get_lpm_req()`. Resume repeats D3 fixups before `cnl_resume()`.

State and persistence: this file owns no dynamic state beyond static const maps and static GUID arrays. Runtime state is stored by `core.c` in `struct pmc_dev` and `struct pmc`, including per-PMC MMIO mappings, LPM mode ordering, telemetry endpoint pointers, and suspend counters. The D3 fixups intentionally mutate PCI power state for selected unbound devices at init/resume.

Dependencies and integration points: depends on `core.h` constants, shared MTL maps (`mtl_socm_*`, `mtl_ioep_reg_map`), CNP offsets, TGL/MTL LPM offsets, and PMT telemetry functions consumed through `core.c`. The regmap list covers `PMC_DEVID_ARL_IOEP`, `PMC_DEVID_ARL_SOCS`, `PMC_DEVID_ARL_PCHS`, and `PMC_DEVID_ARL_SOCM`; this must stay consistent with `ssram_telemetry.c` device discovery. Debugfs files created by `core.c` consume the arrays here.

Risks: bit-map drift against silicon documentation can make debugfs blocker attribution wrong without compile failures. Shared MTL regmaps in the ARL list are a cross-file coupling. The D3 fixup touches PCI power state only if devices are present and unbound; if device IDs are wrong or a driver probes later, power-management symptoms may be hard to trace. `arl_pchs_reg_map.pfear_sts` reuses `ext_arl_socs_pfear_map`, so PCH-S PPFEAR labeling depends on that being intentional.

Test signals: boot on Arrow Lake/Arrow Lake-H with `intel_pmc_core` should create `pmc_core` debugfs entries; `pch_ip_power_gating_status`, `ltr_show`, `substate_status_registers`, `substate_requirements`, and suspend/resume warning paths should show ARL labels. SSRAM path can be validated by seeing PMCs indexed beyond main when available. Power-state fixup behavior is visible through PCI power state and package C/S0ix residency changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/arl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/cnp.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/cnp.c

Purpose: supplies Cannon Lake Point PMC platform data and suspend/resume quirks used by Cannon Lake, Comet Lake, and later platform maps that reuse CNP offsets and LTR names.

Important APIs/types/functions: exports `cnp_pfear_map`, `cnp_slps0_dbg_maps`, `cnp_ltr_show_map`, and `cnp_reg_map` for reuse by ICL/TGL/MTL-family files. Defines `cnl_suspend()` and `cnl_resume()`, which are used by many later `pmc_dev_info` records. The per-CPU `pkg_cst_config` stores MSR_PKG_CST_CONFIG_CONTROL values while C1 auto-demotion is disabled.

Control flow: platform init in `core.c` uses `cnp_pmc_dev` to select `cnp_reg_map`. During suspend, `cnl_suspend()` runs `s2idle_cpu_quirk(disable_c1_auto_demote)` unless firmware suspend is used, then ignores GBE LTR index 3 to avoid PC10 blocking with a cable attached. Resume restores the MSR on all CPUs, restores GBE LTR ignore, and calls `pmc_core_resume_common()` for S0ix/PKGC diagnostics.

State and persistence: static per-CPU MSR snapshots persist across suspend/resume only. The PM register map and bit names are static. `cnl_suspend()` also writes the PMC LTR ignore register through `pmc_core_send_ltr_ignore()`, but resume reverses it.

Dependencies and integration points: depends on SMP, suspend mode checks, MSR helpers, and the shared PMC core. `cnp_ltr_show_map` intentionally includes ICL/TGL offsets (`ICL_PMC_LTR_WIGIG`, `TGL_PMC_LTR_THC0/1`) because it is reused by multiple platforms. Debugfs consumers in `core.c` read this map for `ltr_show`, `ltr_ignore`, `slp_s0_debug_status`, and PPFEAR.

Risks: `on_each_cpu()` assumes online CPUs are stable during suspend/resume after userspace freeze. LTR index 3 is positional, so changing `cnp_ltr_show_map` ordering could silently break the GBE quirk. MSR writes affect all online CPUs and should remain limited to s2idle. Shared map extension across generations increases the chance of stale labels.

Test signals: suspend-to-idle tests on CNP-class hardware should show restored MSR values, no persistent GBE LTR ignore after resume, and useful `slp_s0_debug_status` output when `warn_on_s0ix_failures=1`. Compile coverage comes from x86 platform builds using `CONFIG_INTEL_PMC_CORE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/cnp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/core.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/core.c

Purpose: implements the Intel PMC Core platform driver. It discovers the platform-specific PMC map, maps PWRM MMIO, creates debugfs/sysfs interfaces for S0ix, LTR, PPFEAR, LPM, blocker, package C-state, and telemetry views, and participates in suspend/resume diagnostics.

Important APIs/types/functions: low-level helpers `pmc_core_reg_read()`, `pmc_core_reg_write()`, and `pmc_core_adjust_slp_s0_step()` abstract MMIO and counter units. Sysfs `etr3` exposes CF9 global reset control when not locked. Debugfs show/write handlers include `pmc_core_ppfear_show()`, `pmc_core_ltr_show()`, `pmc_core_ltr_ignore_write()`, `pmc_core_ltr_restore_write()`, `pmc_core_slps0_dbg_show()`, `pmc_core_substate_*`, `pmc_core_s0ix_blocker_show()`, `pmc_core_pkgc_show()`, `pmc_core_lpm_latch_mode_*()`, and `pmc_core_die_c6_us_show()`. Exported/internal integration functions include `pmc_core_send_ltr_ignore()`, `pmc_core_resume_common()`, `get_primary_reg_base()`, `pmc_core_punit_pmt_init()`, `pmc_core_set_device_d3()`, `generic_core_init()`, `pmc_core_pmt_get_lpm_req()`, and `pmc_core_pmt_get_blk_sub_req()`.

Control flow: `pmc_core_probe()` allocates `struct pmc_dev`, matches the CPU against `intel_pmc_core_ids`, allocates the primary `struct pmc`, initializes package C-state snapshots and the mutex, then calls a platform-specific init callback or `generic_core_init()`. Generic init sets suspend/resume hooks, tries SSRAM multi-PMC discovery when a `regmap_list` exists, falls back to LPIT/default-base primary mapping if SSRAM fails except `-EAGAIN`, computes enabled LPM mode order, registers PUNIT telemetry if configured, and fetches LPM/substate requirements from PMT telemetry for SSRAM platforms. Probe then checks the PMC read-disable bit, applies DMI quirks, registers debugfs, and reports max hardware sleep.

State and persistence: `struct pmc_dev` holds per-platform lifetime state: `pmcs[]`, debugfs root, platform device, crystal frequency, read-lock flag, mutex, suspend/resume hooks, S0ix and package C-state snapshots, PUNIT telemetry endpoint, and regmap list. Each `struct pmc` tracks base address, ioremapped registers, regmap, LPM requirement buffers, saved LTR ignore value, and enabled LPM modes. Module params `warn_on_s0ix_failures` and `ltr_ignore_all_suspend` affect suspend/resume behavior. Static `device_initialized` permits one instance, and static `slps0_dbg_latch` controls debug latch behavior.

Dependencies and integration points: depends on ACPI `INT33A1`, x86 CPU model matching, LPIT, DMI, PCI, PM suspend core, MSRs, debugfs/sysfs, PMT telemetry, and the SSRAM telemetry driver. Platform files provide `struct pmc_dev_info` objects and regmaps. PMT telemetry endpoints are registered through `pmt_telem_find_and_register_endpoint()` and read with `pmt_telem_read32()`/`pmt_telem_read()`.

Risks: hardware-facing writes (`etr3`, LTR ignore/restore, latch mode, D3 fixups from platform files) need correct locking and validation; user-facing debugfs writes can affect power behavior. SSRAM init can partially discover PMCs; secondary PMC add failures are ignored, so diagnostics may be incomplete rather than fatal. Requirement-fetch failure after SSRAM mapping unwinds mappings and telemetry endpoints, so lifetime bugs would show as probe failures. `pmc_core_resume_common()` uses primary PMC offsets for LPM display in a loop, which relies on compatible offsets/maps. `get_primary_reg_base()` fallback to `PMC_BASE_ADDR_DEFAULT` must avoid RAM mappings via `page_is_ram()`.

Test signals: probe success logs `initialized` and creates `/sys/kernel/debug/pmc_core`. Read debugfs files to validate mappings and counters. Suspend/resume with `warn_on_s0ix_failures=1` should report PKGC vs S0ix blockers. PMT-dependent files (`substate_requirements`, `die_c6_us_show`) validate endpoint discovery. Error paths can be exercised by missing SSRAM telemetry (`-EPROBE_DEFER`), absent LPIT, invalid LTR index writes, invalid `lpm_latch_mode` strings, and locked ETR3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/core.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/core.h

Purpose: central header for the Intel PMC Core driver. It defines register offsets, device IDs, shared constants, core data structures, platform hooks, exported platform data, and debugfs helper macros used by all PMC platform files.

Important APIs/types/functions: `struct pmc_bit_map` names bits and optionally supplies blocker stride metadata. `struct pmc_reg_map` is the central platform contract for register offsets, bit maps, LPM layout, S0ix blocker layout, telemetry GUIDs, and counter units. `struct pmc_info` maps SSRAM device IDs to regmaps. `struct pmc` stores one controller's MMIO base, regmap, LPM requirements, saved LTR ignore state, and enabled modes. `struct pmc_dev` stores the driver instance and up to `MAX_NUM_PMC` controllers. `struct pmc_dev_info` is the CPU/platform descriptor with init/suspend/resume/sub-requirement callbacks. `pmc_for_each_mode()` iterates enabled LPM modes, and `DEFINE_PMC_CORE_ATTR_WRITE()` builds writable debugfs file operations.

Control flow: platform `.c` files fill `pmc_dev_info`, `pmc_reg_map`, and `pmc_info` data declared here; `core.c` consumes those at probe and runtime. Legacy platforms rely on a single `.map`, while SSRAM platforms set `.regmap_list` and telemetry callbacks. The header's offsets and device IDs determine which MMIO regions are mapped and which LTR/LPM/debugfs controls are exposed.

State and persistence: the header itself has no state, but defines all persistent in-memory state held for module lifetime. Register macros encode hardware ABI and must remain stable for the matching silicon generation.

Dependencies and integration points: includes ACPI bits and platform-device types and forward-declares `struct telem_endpoint` from PMT telemetry. Externs tie together SPT/CNP/ICL/TGL/ADL/MTL/ARL/LNL/PTL/WCL platform descriptors, and function declarations tie platform files back to `core.c`.

Risks: a wrong offset, counter step, `ltr_ignore_max`, device ID, or map count silently corrupts debug output or hardware control. `pmc_bit_map.blk` has meaning only for blocker-style paths; maps used in both bit display and blocker paths must keep that field consistent. Cross-file externs require link-time consistency as newer files reuse MTL/PTL maps.

Test signals: build/link coverage catches missing extern definitions, but not incorrect values. Runtime signals are correct debugfs file presence, sane LTR and LPM output on each supported CPU, successful SSRAM matching by device ID, and absence of invalid memory accesses when optional maps are NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/icl.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/icl.c

Purpose: defines the Ice Lake PMC regmap by extending Cannon Lake PPFEAR with Ice Lake-specific entries and adjusting counter units and limits.

Important APIs/types/functions: `icl_pfear_map` adds RES/TAM/GBETSN/TBTLSX bits beyond the CNP map. `ext_icl_pfear_map` chains `cnp_pfear_map` plus Ice Lake additions. `icl_reg_map` reuses CNP offsets, SLP_S0 debug maps, LTR map, and ETR3 while setting `ICL_PMC_SLP_S0_RES_COUNTER_STEP`, `ICL_PPFEAR_NUM_ENTRIES`, and `ICL_NUM_IP_IGN_ALLOWED`. `icl_pmc_dev` publishes the map.

Control flow: CPU matching in `core.c` selects `icl_pmc_dev`; no custom init means `generic_core_init()` maps the primary PMC through the legacy LPIT/default base path and debugfs uses the ICL regmap.

State and persistence: no dynamic state. Static maps live for module lifetime; runtime state is in `core.c`.

Dependencies and integration points: depends on CNP exported maps and core constants. Debugfs consumers include `pch_ip_power_gating_status`, `ltr_show`, `slp_s0_debug_status`, and package C-state output.

Risks: because this is mostly inherited CNP behavior, the main risk is over-reuse of CNP LTR/SLP_S0 names on ICL variants. PPFEAR bucket count must match the appended Ice Lake map.

Test signals: on Ice Lake, debugfs PPFEAR should include Ice Lake-specific tail entries and SLP_S0 residency should use the Ice Lake counter step. Basic compile/link verifies `cnp_*` extern usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/icl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/lnl.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/lnl.c

Purpose: provides Lunar Lake PMC platform data for an SSRAM-discovered SoC-M controller, including LPM status maps, blocker maps, PPFEAR maps, LTR maps, and D3 fixups for unbound IPU/NPU devices.

Important APIs/types/functions: `LNL_LPM_REG_INDEX` maps PMT LPM table registers into debugfs requirement columns. `lnl_ltr_show_map`, `lnl_lpm_maps`, `lnl_blk_maps`, and `ext_lnl_pfear_map` feed `lnl_socm_reg_map`. Many `pmc_bit_map` entries populate the `blk` field, which `pmc_core_s0ix_blocker_show()` and `pmc_core_pmt_get_blk_sub_req()` use for blocker counters and requirement offsets. `lnl_d3_fixup()`, `lnl_core_init()`, and `lnl_resume()` wrap generic init/resume. `lnl_pmc_dev` is the exported platform descriptor.

Control flow: `core.c` matches `INTEL_LUNARLAKE_M` to `lnl_pmc_dev`. Init sets IPU/NPU to D3 if unbound, then `generic_core_init()` uses SSRAM telemetry to discover `PMC_DEVID_LNL_SOCM`, maps the controller, reads enabled LPM modes, and reads PMT LPM requirements with `pmc_core_pmt_get_lpm_req()`. Resume repeats the D3 fixup then uses `cnl_resume()`.

State and persistence: all maps are static. D3 fixup mutates PCI power state. Requirement buffers and LPM mode state are allocated/managed by `core.c` during probe.

Dependencies and integration points: depends on SSRAM telemetry, PMT telemetry GUID `SOCM_LPM_REQ_GUID`, CNP/ADL/TGL/MTL offsets, and `cnl_suspend`/`cnl_resume`. The `s0ix_blocker_maps` path integrates with the `s0ix_blocker` debugfs file and with blocker-style requirements only if the regmap supplies blocker metadata.

Risks: the `blk` metadata is easy to misalign with hardware counter spacing, producing wrong blocker counts even when bit displays look correct. The LNL PPFEAR map includes repeated or reserved labels, so consumers should treat it as hardware diagnostic labeling rather than a stable userspace ABI. D3 fixups depend on device IDs and driver binding status.

Test signals: Lunar Lake boot should expose `s0ix_blocker`, `substate_requirements`, `substate_status_registers`, and `ltr_show` with LNL labels. PMT endpoint discovery failures should defer or fail probe through `generic_core_init()`. Suspend/resume should maintain IPU/NPU D3 when unbound and restore LTR/MSR state through CNL hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/lnl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/mtl.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/mtl.c

Purpose: supplies Meteor Lake PMC data for SSRAM-discovered SOC-M and IOE variants. It defines reusable maps later consumed by ARL and exports `mtl_pmc_dev` for Meteor Lake CPU matching.

Important APIs/types/functions: exports `mtl_socm_pfear_map`, several SOC-M D3/VNN/signal maps, `mtl_socm_reg_map`, and `mtl_ioep_reg_map`. Defines private IOE-P/IOE-M PFET, LTR, LPM, D3, VNN, and misc maps plus `mtl_ioem_reg_map`. `mtl_pmc_info_list[]` maps `PMC_DEVID_MTL_SOCM`, `PMC_DEVID_MTL_IOEP`, and `PMC_DEVID_MTL_IOEM` to regmaps. `mtl_d3_fixup()` sets unbound GNA/IPU/VPU devices to D3. `mtl_core_init()` and `mtl_resume()` wrap generic init/resume. `MTL_PMT_DMU_GUIDS` supports die C6 telemetry.

Control flow: `core.c` matches Meteor Lake-L to `mtl_pmc_dev`. Init performs D3 fixups, SSRAM discovery maps available SOC/IOE PMCs, reads enabled LPM modes, registers PUNIT DMU telemetry, and fetches LPM requirement registers using `pmc_core_pmt_get_lpm_req()`. Debugfs then iterates all available PMCs for PPFEAR, LTR, substate, and requirement views. Resume repeats D3 fixups then runs the CNL resume path.

State and persistence: maps are static and exported where later platform files reuse them. Runtime state is in `core.c`; `punit_ep` persists until driver removal and is used by `die_c6_us_show`.

Dependencies and integration points: depends on CNP offsets, ADL/TGL/MTL core constants, SSRAM telemetry device IDs, PMT telemetry GUIDs (`SOCP_LPM_REQ_GUID`, `IOEM_LPM_REQ_GUID`, `IOEP_LPM_REQ_GUID`, `MTL_PMT_DMU_GUID`), and the CNL suspend/resume quirk. ARL depends on several non-static maps from this file.

Risks: exported map reuse means MTL changes can affect ARL. Multi-PMC discovery must match silicon device IDs and GUIDs or requirement debugfs will be absent/fail. D3 fixups can change power state for devices without drivers and should remain targeted. IOE-M and IOE-P maps are similar but not identical; accidental consolidation would lose labels.

Test signals: Meteor Lake systems should show multiple PMC sections in `ltr_show`/PPFEAR when IOE is present, `die_c6_us_show` when DMU telemetry registers, and valid `substate_requirements`. Suspend/resume should show CNL quirk behavior plus MTL device D3 fixups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/mtl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/pltdrv.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/pltdrv.c

Purpose: creates a fallback `intel_pmc_core` platform device on older supported Intel systems that lack the preferred ACPI `INT33A1` device.

Important APIs/types/functions: `intel_pmc_core_platform_ids[]` lists legacy CPU models where fallback enumeration is allowed. `pmc_core_platform_init()` checks ACPI, virtualization, CPU match, allocates a `platform_device`, and registers it. `pmc_core_platform_exit()` unregisters it. `intel_pmc_core_release()` frees the manually allocated device.

Control flow: module init exits with `-ENODEV` if ACPI already exposes `INT33A1`, if running under a hypervisor outside Xen dom0, or if the CPU is not in the fallback list. Otherwise it creates a platform device named `intel_pmc_core`, which binds to the core platform driver in `core.c`.

State and persistence: global `pmc_core_device` stores the created platform device until module exit. No hardware state is touched directly here.

Dependencies and integration points: depends on ACPI enumeration, x86 CPU matching, Xen dom0 detection, and the `intel_pmc_core` platform driver name. The file explicitly should not grow for new platforms because ACPI enumeration is preferred.

Risks: overly broad fallback enumeration could attach the PMC driver in unsupported VMs or systems without safe MMIO access; the hypervisor/Xen checks mitigate this. If ACPI detection misses an existing device, duplicate registration could occur, though ACPI presence is checked first.

Test signals: on listed older hardware without ACPI `INT33A1`, `platform_device_register()` should cause `core.c` probe. On newer platforms, VMs, and systems with ACPI device, module init should return `-ENODEV` without side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/pltdrv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/ptl.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/ptl.c

Purpose: adds Panther Lake PMC support for PCD-H/PCD-P dies using SSRAM discovery and blocker-style PMT substate requirements.

Important APIs/types/functions: `ptl_pcdp_pfear_map`, `ptl_pcdp_ltr_show_map`, `ptl_pcdp_lpm_maps`, and `ptl_pcdp_blk_maps` describe Panther Lake power/debug status. Exports `ptl_pcdp_clocksource_status_map`, `ptl_pcdp_vnn_req_status_3_map`, and `ptl_pcdp_signal_status_map` for WCL reuse. `ptl_pcdp_reg_map` sets `s0ix_blocker_maps`, `num_s0ix_blocker`, `blocker_req_offset`, and `lpm_req_guid`. `ptl_pmc_info_list[]` maps `PMC_DEVID_PTL_PCDH` and `PMC_DEVID_PTL_PCDP`. `ptl_d3_fixup()`, `ptl_core_init()`, and `ptl_resume()` handle unbound IPU/NPU D3.

Control flow: CPU match selects `ptl_pmc_dev`; init runs D3 fixup and generic SSRAM init. Requirement fetching uses `pmc_core_pmt_get_blk_sub_req()` rather than the register-index LPM table function, and debugfs uses `pmc_core_substate_blk_req_fops` for `substate_requirements`.

State and persistence: static platform maps only. Runtime controller mappings, blocker requirement arrays, and enabled modes are owned by `core.c`. D3 fixup alters unbound PCI device power state.

Dependencies and integration points: depends on CNP/TGL/MTL/LNL constants and CNL suspend/resume hooks. WCL reuses exported PTL clocksource, VNN3, and signal maps, so symbol visibility is intentional. SSRAM telemetry must discover one of the PTL device IDs; PMT telemetry must provide `PCDP_LPM_REQ_GUID`.

Risks: blocker requirement path depends on `num_s0ix_blocker`, `blocker_req_offset`, and every map entry's `blk` field; mismatch can shift all rows. Reused maps in WCL mean PTL changes can alter WCL output. As a 2025 platform file, silicon table churn is plausible.

Test signals: Panther Lake systems should expose `s0ix_blocker` and blocker-style `substate_requirements` with PTL labels. PMT reads beginning at `PTL_BLK_REQ_OFFSET` should succeed. Suspend/resume should run NPU/IPU D3 fixups and CNL LTR/MSR handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/ptl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/spt.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/spt.c

Purpose: provides Sunrise Point PMC data for Skylake/Kaby Lake-era platforms and a special init path to redirect Coffee Lake-like systems to Cannon Lake PCH mapping when the SPT PMC PCI ID is absent.

Important APIs/types/functions: `spt_pll_map`, `spt_mphy_map`, `spt_pfear_map`, `ext_spt_pfear_map`, and `spt_ltr_show_map` feed `spt_reg_map`. `spt_core_init()` checks for `SPT_PMC_PCI_DEVICE_ID` with `pci_dev_present()` and chooses either SPT generic init or CNP generic init. `spt_pmc_dev` exports the platform descriptor.

Control flow: CPU match in `core.c` selects `spt_pmc_dev`; custom init detects whether actual PCH is SPT. If not, it calls `generic_core_init()` with `cnp_pmc_dev` to handle Coffee Lake cases where CPU ID resembles Kaby Lake but PCH registers are CNP-compatible.

State and persistence: all maps and PCI ID table are static. Runtime MMIO state is managed by `core.c`. SPT exposes MPHY/PLL paths that use PMC XRAM message registers in `core.c`.

Dependencies and integration points: depends on `core.h`, PCI device matching, and `cnp_pmc_dev`. Debugfs consumers include PPFEAR, LTR, MPHY power gating, PLL status, and package C-state.

Risks: fallback detection hinges on presence of one PCI ID; unusual firmware hiding could select the wrong regmap. MPHY/PLL debugfs reads depend on `PMC_READ_DISABLE` being clear; otherwise users get access-denied output. SPT LTR ordering affects manual `ltr_ignore` indices.

Test signals: on SPT hardware, `pll_status` and `mphy_core_lanes_power_gating_status` should exist if read is allowed. Coffee Lake-like systems should select CNP behavior. Build/link ensures `cnp_pmc_dev` reference resolves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/spt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/ssram_telemetry.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/ssram_telemetry.c

Purpose: PCI driver that discovers PMC SSRAM telemetry headers, records PMC device IDs and PWRM bases for the PMC core driver, and registers PMT telemetry DVSEC regions with Intel VSEC.

Important APIs/types/functions: `pmc_ssram_telemetry_add_pmt()` reads a DVSEC header from SSRAM and calls `intel_vsec_register()` with telemetry capability. `get_base()` reads aligned 64-bit base fields and masks low attribute bits. `pmc_ssram_telemetry_get_pmc()` maps SSRAM headers for main/IOE/PCH PMCs, extracts PWRM base and device ID, stores them in `pmc_ssram_telems`, and registers PMT telemetry. Exported `pmc_ssram_telemetry_get_pmc_info()` returns cached info to `core.c`.

Control flow: PCI probe allocates the telemetry array, enables the device, discovers the main PMC, then best-effort discovers IOE and PCH PMCs from offsets in the main SSRAM header. At probe finish it publishes `device_probed=true` with a write barrier. Consumers calling before probe finishes receive `-EAGAIN`, which `generic_core_init()` converts to probe defer.

State and persistence: static `pmc_ssram_telems` points to devm-managed per-PMC info and static `device_probed` gates reads. The array persists for the PCI device lifetime. Registered VSEC telemetry devices become integration points for PMT telemetry consumers.

Dependencies and integration points: depends on PCI, `linux/intel_vsec.h`, SSRAM offsets, PMC device IDs from `core.h`, and `INTEL_VSEC` namespace. `core.c` consumes this through `pmc_ssram_telemetry_get_pmc_info()` for multi-PMC mapping.

Risks: `device_probed` is global and there is no remove callback resetting it, so this assumes one relevant device lifetime. Secondary PMC discovery errors are ignored by probe, so missing IOE/PCH may be silent. DVSEC parsing from firmware/hardware-provided SSRAM must be correct or PMT telemetry registration will be wrong. Memory barriers protect publication but not broader multi-device scenarios.

Test signals: on supported MTL/ARL/LNL/PTL/WCL PCI IDs, probe should enable the device, expose PMT telemetry through VSEC, and allow `intel_pmc_core` SSRAM init without `-EPROBE_DEFER`. Missing secondary PMCs should not fail probe. Invalid early consumer ordering should result in deferred PMC core probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/ssram_telemetry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/ssram_telemetry.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/ssram_telemetry.h

Purpose: declares the minimal SSRAM telemetry data contract between the SSRAM PCI driver and the PMC core driver.

Important APIs/types/functions: `struct pmc_ssram_telemetry` carries a PMC device ID and PWRM base address. `pmc_ssram_telemetry_get_pmc_info()` retrieves one indexed PMC's cached information.

Control flow: `core.c` calls the declared function from `pmc_core_pmc_add()` during SSRAM-backed generic init. The implementation may return success, `-EAGAIN`, `-EINVAL`, or `-ENODEV`.

State and persistence: no header state. The structure is a copy-out container for implementation-owned state in `ssram_telemetry.c`.

Dependencies and integration points: included by `core.c` and `ssram_telemetry.c`; depends on core definitions for `MAX_NUM_PMC` and indexes indirectly through callers.

Risks: the API only exposes `devid` and `base_addr`, so any future need for per-PMC metadata requires extending this interface. Callers must understand `-EAGAIN` as probe ordering, not permanent absence.

Test signals: compile coverage for both implementation and consumer; runtime SSRAM init should correctly map returned `devid` through the platform `pmc_info` list.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/ssram_telemetry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/tgl.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/tgl.c

Purpose: supplies Tiger Lake PMC platform maps for LP and H variants and fetches LPM requirement registers through an ACPI `_DSM` interface.

Important APIs/types/functions: `tgl_lpm_maps` combines clocksource, power gating, D3, VNN, misc, and signal status maps. `tgl_reg_map` and `tgl_h_reg_map` share most offsets, with H adding PSON residency support. `pmc_core_get_tgl_lpm_reqs()` evaluates ACPI DSM UUID `57a6512e-3979-4e9d-9708-ff13b2508972` function 1 and stores returned requirement registers in the primary PMC. `tgl_core_init()` calls generic init then DSM requirement fetching. `tgl_l_pmc_dev` and `tgl_pmc_dev` publish LP/H descriptors.

Control flow: CPU matching selects LP or H descriptor. Init maps the legacy primary PMC, computes LPM modes, then reads ACPI-provided LPM requirements. Debugfs creates substate files when LPM offsets exist and creates `pson_residency_usec` on H when ACPI property enables PSON switching.

State and persistence: static maps only. DSM output is copied into a devm-allocated `pmc->lpm_req_regs` buffer that lives with the platform device.

Dependencies and integration points: depends on CNP maps/offsets, ACPI companion and DSM, CNL suspend/resume hooks, and core debugfs paths. `tgl_signal_status_map` is exported for other platform maps.

Risks: `pmc_core_get_tgl_lpm_reqs()` allocates with `lpm_size` as the element count even though it is already bytes, which overallocates rather than underallocates; still, future edits must preserve correct copy size. If ACPI DSM returns unexpected size or is absent, requirements are silently unavailable while other debugfs remains. LP/H map selection affects PSON visibility.

Test signals: Tiger Lake debugfs should show LPM status/residency and, when DSM succeeds, `substate_requirements`. ACPI debug logs indicate DSM size mismatches. Suspend/resume should use CNL quirks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/tgl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/wcl.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/wcl.c

Purpose: adds Wildcat Lake PMC support for PCD-N using SSRAM discovery and blocker-style PMT substate requirements.

Important APIs/types/functions: `wcl_pcdn_pfear_map`, `wcl_pcdn_ltr_show_map`, `wcl_pcdn_lpm_maps`, and `wcl_pcdn_blk_maps` define the WCL diagnostic layout. `wcl_pcdn_reg_map` sets WCL MMIO length, blocker count/offset, LPM status offsets, and `PCDN_LPM_REQ_GUID`. `wcl_pmc_info_list[]` maps `PMC_DEVID_WCL_PCDN`. `wcl_d3_fixup()`, `wcl_core_init()`, and `wcl_resume()` handle unbound NPU D3.

Control flow: `core.c` matches Wildcat Lake-L to `wcl_pmc_dev`. Init runs NPU D3 fixup then generic SSRAM init. Requirement fetching uses `pmc_core_pmt_get_blk_sub_req()`, and debugfs uses `pmc_core_substate_blk_req_fops`.

State and persistence: static maps plus runtime PMC state in `core.c`. WCL reuses exported PTL maps for clocksource, VNN3, and signal status, so those symbols must remain available.

Dependencies and integration points: depends on PTL exported maps, CNP/TGL/MTL/LNL offsets, SSRAM telemetry, PMT telemetry GUID `PCDN_LPM_REQ_GUID`, and CNL suspend/resume. Debugfs consumers include PPFEAR, LTR, S0ix blocker, LPM status, and blocker requirements.

Risks: blocker count and offset are platform-specific; any mismatch with the PMT telemetry table shifts requirements. PTL map reuse is a cross-platform dependency. As with other D3 fixups, behavior depends on whether the NPU has a bound driver.

Test signals: Wildcat Lake systems should expose WCL labels in `ltr_show`, `s0ix_blocker`, and `substate_requirements`. PMT reads at `WCL_BLK_REQ_OFFSET` should succeed. NPU D3 state and suspend/resume S0ix residency are practical integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/wcl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/Kconfig

Purpose: defines build-time configuration options for Intel Platform Monitoring Technology drivers.

Important APIs/types/functions: `INTEL_PMT_CLASS` is an internal tristate selected by feature drivers. `INTEL_PMT_TELEMETRY` depends on `INTEL_VSEC` and selects discovery and class support. `INTEL_PMT_CRASHLOG` depends on `INTEL_VSEC` and selects class support. `INTEL_PMT_DISCOVERY` depends on `INTEL_VSEC` and selects class support. `INTEL_PMT_KUNIT_TEST` depends on discovery, KUnit, and a telemetry-compatible expression so tests can build with telemetry enabled or disabled.

Control flow: Kconfig selections determine which objects in the PMT Makefile are built. Telemetry selecting discovery means telemetry users also get feature discovery interfaces. Crashlog remains independent of telemetry but shares the class layer.

State and persistence: no runtime state. Kconfig state persists in the kernel build configuration and affects module availability/names.

Dependencies and integration points: integrates with `INTEL_VSEC`, PMT class, telemetry, crashlog, discovery, and KUnit infrastructure. Help text points to the sysfs ABI documentation for the class interface.

Risks: typo in help text says "Monitory" for telemetry, not functional. Selection dependencies can increase build footprint: enabling telemetry also enables discovery and class. KUnit dependency expression is intentionally broad and should be checked if telemetry APIs used by tests change.

Test signals: `allyesconfig`/`allmodconfig` should build all PMT modules. Minimal configs enabling telemetry/crashlog/discovery should pull in `intel_pmt_class`. KUnit config should produce `pmt-discovery-kunit`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/Makefile

Purpose: maps PMT Kconfig symbols to module/object composition.

Important APIs/types/functions: builds `pmt_class.o` from `class.o`, `pmt_telemetry.o` from `telemetry.o`, `pmt_crashlog.o` from `crashlog.o`, `pmt_discovery.o` from `discovery.o features.o`, and `pmt-discovery-kunit.o` from `discovery-kunit.o`.

Control flow: kernel build includes each object according to its `CONFIG_INTEL_PMT_*` symbol. The object names align with module names described in Kconfig help.

State and persistence: no runtime state. Build output composition persists in generated kernel modules or built-in objects.

Dependencies and integration points: depends on Kconfig to select symbols and on source files in the same directory. Discovery links `features.o`, which supplies feature names/layouts referenced by discovery and KUnit code.

Risks: changing module object names can break module aliases or expected help text. Forgetting to include `features.o` with discovery would break symbols used by discovery and tests.

Test signals: build with each `CONFIG_INTEL_PMT_*=m/y` and verify expected module/object names. KUnit build should include only `discovery-kunit.o` for the test module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/class.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/class.c

Purpose: implements the common PMT class layer. It creates `/sys/class/intel_pmt` devices, maps PMT data buffers, exposes common attributes/bin files, and provides shared helper functions for telemetry, discovery, and crashlog drivers.

Important APIs/types/functions: `intel_pmt_is_early_client_hw()` checks VSEC early hardware quirks. `pmt_telem_read_mmio()` reads telemetry either through platform callbacks or direct MMIO, with special aligned 64-bit handling for SPR PUNIT GUID. `intel_pmt_read()` and `intel_pmt_mmap()` back binary sysfs access. `intel_pmt_populate_entry()` resolves PMT base addresses for `ACCESS_LOCAL` and `ACCESS_BARID`. `intel_pmt_dev_register()`, `intel_pmt_dev_create()`, and `intel_pmt_dev_destroy()` manage class devices, xarray IDs, sysfs groups, ioremap, bin attributes, and optional endpoint registration. `intel_pmt_class` is exported.

Control flow: feature drivers provide an `intel_pmt_namespace` with a header decoder and optional endpoint callback, then call `intel_pmt_dev_create()` for each VSEC resource. The class maps the discovery table, decodes the feature header, computes the data base address, creates the class device and sysfs files, maps the data resource if non-empty, and registers feature-specific endpoints. Destroy removes bin files/groups, unregisters the device, and erases the xarray entry.

State and persistence: xarray IDs are namespace-owned and allocated from 1 to INT_MAX. Each `intel_pmt_entry` stores mapped discovery/data addresses, kobject, header, device ID, GUID, feature flags, callback pointer, and optional telemetry endpoint. The class itself is registered at module init and unregistered at exit.

Dependencies and integration points: depends on Intel VSEC auxiliary devices, PCI BAR resources, sysfs, xarray, MMIO helpers, and `class.h`. Telemetry and crashlog drivers reuse this layer. `intel_pmt_attr_visible()` suppresses common attributes for discovery-capability devices.

Risks: address calculation differs for early client hardware, so wrong quirks can map the wrong BAR/offset. `mmap` forbids writable mappings and bounds by page-rounded physical size, but incorrect `entry->size` from header decoding can still expose wrong ranges. `pmt_memcpy64_fromio()` requires 8-byte alignment for SPR PUNIT reads. Error paths must remove partially created sysfs and xarray entries in the correct order.

Test signals: sysfs should show `guid`, `size`, `offset`, and a read-only bin attribute for non-discovery PMT entries. `mmap` with write flags should fail `-EROFS`; oversized mmap should fail `-EINVAL`. VSEC telemetry/crashlog probes exercise create/destroy unwinds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/class.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/class.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/class.h

Purpose: defines the PMT class-layer data structures and APIs shared by telemetry, discovery, crashlog, and PMC integration code.

Important APIs/types/functions: access-type macros `ACCESS_BARID` and `ACCESS_LOCAL` plus `GET_BIR()`/`GET_ADDRESS()` decode PMT base-offset fields. `struct telem_endpoint` represents a telemetry endpoint with device, header, callbacks, MMIO base, presence flag, and kref. `struct intel_pmt_header` is the decoded discovery header. `struct intel_pmt_entry` stores one class device/resource. `struct intel_pmt_namespace` supplies namespace name, xarray, header decoder, and optional endpoint registration hook. Declared APIs include `pmt_telem_read_mmio()`, `intel_pmt_is_early_client_hw()`, `intel_pmt_dev_create()`, `intel_pmt_dev_destroy()`, and optionally `intel_pmt_get_features()`.

Control flow: feature drivers include this header, fill an entry/namespace, and delegate common device creation/destruction to `class.c`. Telemetry endpoint users rely on `struct telem_endpoint` from this header through `telemetry.h`.

State and persistence: no header state. It defines the per-entry and per-endpoint state layout used for module lifetime by PMT drivers.

Dependencies and integration points: depends on `linux/intel_vsec.h`, xarray, IO helpers, and `telemetry.h`. It bridges class code with telemetry feature discovery and crashlog.

Risks: `struct intel_pmt_entry` has many ownership-sensitive fields; feature drivers must not destroy class-managed objects out of order. Conditional `intel_pmt_get_features()` stub means discovery-disabled builds silently omit feature enrichment.

Test signals: compile matrix with discovery enabled/disabled validates the conditional stub. PMT telemetry/crashlog probes validate namespace and entry layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/class.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/crashlog.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/crashlog.c

Purpose: implements the Intel PMT crashlog auxiliary driver. It decodes crashlog discovery headers, creates PMT class devices, exposes crashlog control/status sysfs attributes, and allows users to read crashlog buffers through the PMT class bin file.

Important APIs/types/functions: `struct crashlog_status`, `struct crashlog_control`, and `struct crashlog_info` describe version-specific status/control bits. `struct crashlog_entry` embeds `intel_pmt_entry` first and adds a control mutex and selected info. `pmt_crashlog_rmw()` masks trigger bits and writes control, while `pmt_crashlog_rc()` reads status. Sysfs handlers implement `clear`, `consumed`, `enable`, `error`, `rearm`, and `trigger`. `pmt_crashlog_header_decode()` validates type/version, decodes access/GUID/base/size, and attaches the correct attribute group. Probe/remove manage entries for each VSEC resource.

Control flow: auxiliary probe allocates a flexible private structure sized for all VSEC resources and calls `intel_pmt_dev_create()` for each. The namespace decoder skips unsupported crashlog headers by returning positive `1`; hard errors abort and unwind. For supported type 1 version 0 or 2, class creation exposes version-appropriate controls and the binary crashlog region. Remove destroys all created entries and mutexes.

State and persistence: per-entry mutex protects control register writes. Hardware status/control bits persist in the device discovery/control registers. The `crashlog_array` xarray persists namespace IDs until module exit, where it is destroyed.

Dependencies and integration points: depends on auxiliary bus, Intel VSEC, PMT class, PCI/MMIO, sysfs, mutex, and overflow-safe allocation. Imports `INTEL_PMT`. PMT class handles common mapping and bin read/mmap.

Risks: sysfs writes directly alter crashlog hardware state; guards prevent clearing false, consuming incomplete logs, triggering while disabled, and triggering when a log is already complete. Version 0 has combined status/control register while version 2 separates them, so bit masks must be exact. Returning positive `1` for unsupported devices is a convention with `pmt_crashlog_probe()` and class create callers.

Test signals: supported crashlog VSEC resources should create `crashlogN` devices with v0 or v2 attribute sets. Invalid writes should return `-EINVAL`, disabled trigger/consume should return `-EBUSY`, and duplicate trigger should return `-EEXIST`. Remove/reprobe should clean sysfs and xarray entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/crashlog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/discovery-kunit.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/discovery-kunit.c

Purpose: KUnit test module that exercises PMT feature discovery by querying available telemetry regions for every valid PMT feature ID.

Important APIs/types/functions: `validate_pmt_regions()` logs each region and asserts nonnegative platform metadata, nonzero GUID, and non-null/non-error mapped address. `test_intel_pmt_get_regions_by_feature()` iterates feature IDs from 1 through `FEATURE_MAX`, checks `pmt_feature_id_is_valid()`, calls `intel_pmt_get_regions_by_feature()`, validates available groups, and releases them with `intel_pmt_put_feature_group()`. `intel_pmt_discovery_test_suite` registers the single test case.

Control flow: when the KUnit module runs, it loops all known feature IDs. `-ENOENT` and other errors are warnings rather than hard failures, so the test is tolerant of hardware without a given feature. Available feature groups are validated structurally.

State and persistence: no persistent driver state. The test temporarily obtains feature groups whose references must be put after validation.

Dependencies and integration points: depends on KUnit, `linux/intel_pmt_features.h`, Intel VSEC, PMT discovery namespace, and exported discovery/telemetry feature group APIs. Imports `INTEL_PMT_DISCOVERY`.

Risks: many assertions are weak because fields are unsigned and `>= 0` is tautological; the strongest checks are GUID nonzero and address validity. The test warns rather than fails when no feature groups are available, making it more of a smoke/integration test than a strict unit test. It depends on real registered PMT regions unless a test harness supplies them.

Test signals: KUnit output should list available features and regions. A regression in feature group lookup, GUID population, or address mapping should show errors or assertion failures. Systems without PMT regions produce warnings but not necessarily failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmt/discovery-kunit.c -->
