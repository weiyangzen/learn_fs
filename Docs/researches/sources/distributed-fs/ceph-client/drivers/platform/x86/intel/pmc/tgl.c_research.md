# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/tgl.c

Purpose: supplies Tiger Lake PMC platform maps for LP and H variants and fetches LPM requirement registers through an ACPI `_DSM` interface.

Important APIs/types/functions: `tgl_lpm_maps` combines clocksource, power gating, D3, VNN, misc, and signal status maps. `tgl_reg_map` and `tgl_h_reg_map` share most offsets, with H adding PSON residency support. `pmc_core_get_tgl_lpm_reqs()` evaluates ACPI DSM UUID `57a6512e-3979-4e9d-9708-ff13b2508972` function 1 and stores returned requirement registers in the primary PMC. `tgl_core_init()` calls generic init then DSM requirement fetching. `tgl_l_pmc_dev` and `tgl_pmc_dev` publish LP/H descriptors.

Control flow: CPU matching selects LP or H descriptor. Init maps the legacy primary PMC, computes LPM modes, then reads ACPI-provided LPM requirements. Debugfs creates substate files when LPM offsets exist and creates `pson_residency_usec` on H when ACPI property enables PSON switching.

State and persistence: static maps only. DSM output is copied into a devm-allocated `pmc->lpm_req_regs` buffer that lives with the platform device.

Dependencies and integration points: depends on CNP maps/offsets, ACPI companion and DSM, CNL suspend/resume hooks, and core debugfs paths. `tgl_signal_status_map` is exported for other platform maps.

Risks: `pmc_core_get_tgl_lpm_reqs()` allocates with `lpm_size` as the element count even though it is already bytes, which overallocates rather than underallocates; still, future edits must preserve correct copy size. If ACPI DSM returns unexpected size or is absent, requirements are silently unavailable while other debugfs remains. LP/H map selection affects PSON visibility.

Test signals: Tiger Lake debugfs should show LPM status/residency and, when DSM succeeds, `substate_requirements`. ACPI debug logs indicate DSM size mismatches. Suspend/resume should use CNL quirks.
