# sources/distributed-fs/ceph-client/drivers/reset/tegra/Makefile

Purpose: Kbuild mapping for Tegra BPMP reset support.

Important APIs/types/functions: builds `reset-bpmp.o` when `CONFIG_RESET_TEGRA_BPMP` is enabled.

Control flow: build-time only.

State and persistence: no runtime state.

Dependencies and integration: object provides `tegra_bpmp_init_resets()` for the BPMP core.

Risks and test signals: missing object breaks BPMP reset registration. Compile with BPMP enabled and disabled.
