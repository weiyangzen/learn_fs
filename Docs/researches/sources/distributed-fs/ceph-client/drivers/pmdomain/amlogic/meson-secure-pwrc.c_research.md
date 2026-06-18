# sources/distributed-fs/ceph-client/drivers/pmdomain/amlogic/meson-secure-pwrc.c

Purpose: secure-monitor backed generic PM-domain provider for newer Amlogic SoCs where power state is controlled through Meson secure firmware calls rather than direct MMIO.

Important APIs/types/functions: `meson_secure_pwrc_domain` wraps a genpd with firmware index and optional parent; `meson_secure_pwrc` owns the domain array, onecell data, and `meson_sm_firmware`; descriptor tables are built with `SEC_PD()` and `TOP_PD()` for A1, A4, A5, C3, S4, S6, S7, S7D, and T7. Runtime callbacks are `meson_secure_pwrc_on()`, `meson_secure_pwrc_off()`, `pwrc_secure_is_off()`, and `meson_secure_pwrc_probe()`.

Control flow: probe locates the global `amlogic,meson-gxbb-sm` secure-monitor node, gets firmware handle, allocates onecell/domain arrays, initializes every named descriptor as a genpd, powers on any always-on domain found off, initializes genpd with firmware-reported off/on state, wires parent-child relationships for descriptors with `parent != PWRC_NO_PARENT`, and registers the onecell provider. Power transitions call `meson_sm_call()` with `SM_A1_PWRC_SET`; status calls use `SM_A1_PWRC_GET`.

State and persistence: software state is the descriptor-derived domain index, flags, parent index, firmware handle, and genpd state. Actual persistence is in secure firmware and power controller hardware. Always-on domains are forced on during probe if firmware reports them off.

Dependencies/integration: depends on Meson secure monitor firmware (`MESON_SM`), ARM SMCCC availability, generic PM domains, DT binding IDs, and OF onecell provider registration. Parent-child genpd hierarchy models T7 subdomains such as DOS/GE2D/MALI/NNA under NIC/MIPI/NNA top domains.

Risks: all hardware control is opaque firmware ABI; failures are collapsed to `-EINVAL` after logging. The driver assumes the secure-monitor node compatible and `SM_A1_PWRC_*` commands work across all listed SoCs. Parent indices must be valid and initialized; incorrect descriptor tables can create broken genpd hierarchies. Always-on annotations protect UART, DMC, SRAM, NIC, ETH wake, DDR, and similar critical blocks.

Test signals: firmware GET/SET calls should succeed for every non-empty descriptor, always-on domains should be on after probe, DT power-domain cells should resolve to correct names, parent subdomains should appear in genpd hierarchy, and consumer drivers should survive suspend/resume and runtime PM cycles.
