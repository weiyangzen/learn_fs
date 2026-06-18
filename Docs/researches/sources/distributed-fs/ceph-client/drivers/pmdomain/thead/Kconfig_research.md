<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/thead/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/thead/Kconfig

Purpose: Build configuration for T-HEAD TH1520 power-domain support.

Important APIs/types/functions: `TH1520_PM_DOMAINS` is a tristate gated by `TH1520_AON_PROTOCOL`; it selects `REGMAP_MMIO` and `AUXILIARY_BUS`.

Control flow: no runtime logic.

State/persistence: build-time only.

Dependencies/integration: reflects that the driver talks to the TH1520 AON firmware protocol and spawns auxiliary devices for GPU power sequencing/reboot behavior.

Risks: if selected without compatible AON protocol support the driver cannot probe.

Test signals: enabling this symbol should build `th1520-pm-domains.o` and pull auxiliary bus support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/thead/Kconfig -->
