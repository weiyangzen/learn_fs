<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/tegra/powergate-bpmp.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/tegra/powergate-bpmp.c

Purpose: Dynamically discovers Tegra powergate IDs from BPMP firmware and exposes each named powergate as a generic PM domain.

Important APIs/types/functions: `struct tegra_powergate_info` is temporary discovery data; `struct tegra_powergate` wraps `generic_pm_domain`, BPMP handle, and firmware ID. Firmware MRQ helpers include `tegra_bpmp_powergate_set_state()`, `get_state()`, `get_max_id()`, and `get_name()`. `tegra_powergate_add/remove()`, `tegra_bpmp_probe_powergates()`, `tegra_bpmp_add_powergates()`, and `tegra_powergate_xlate()` provide genpd integration. Public entry points are `tegra_bpmp_init_powergates()` and `tegra_bpmp_remove_powergates()`.

Control flow: init asks firmware for the maximum ID, loops over IDs to fetch names, skips unnamed holes, creates one genpd per discovered gate, installs a custom xlate that matches DT phandle arg to firmware ID, and registers the BPMP device node as a onecell provider. Power callbacks send `CMD_PG_SET_STATE` with `PG_STATE_ON/OFF`. Removal unregisters each genpd and frees names.

State/persistence: firmware remains source of truth for power state and available gates. Software state is the BPMP-owned `genpd_onecell_data` array and per-domain IDs/names. Discovery names are duplicated during probing and freed after genpd names are independently duplicated.

Dependencies/integration: depends on `soc/tegra/bpmp.h`, BPMP ABI `MRQ_PG`, genpd core, DT `power-domains`, and Tegra BPMP initialization order.

Risks: `tegra_bpmp_powergate_get_state()` returns `PG_STATE_OFF` on transfer errors but `-EINVAL` on firmware negative return; treating all non-off as powered can hide errors. Sparse IDs require custom xlate; consumers using provider array index semantics would be wrong. Provider add failure must remove initialized gates to avoid dangling genpds.

Test signals: BPMP firmware with holes in IDs, DT consumers referencing firmware IDs, power-cycle each gate, failure injection for MRQ transfer/rx errors, and teardown tests when provider registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/tegra/powergate-bpmp.c -->
