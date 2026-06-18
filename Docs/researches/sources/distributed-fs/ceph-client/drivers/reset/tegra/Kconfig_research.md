# sources/distributed-fs/ceph-client/drivers/reset/tegra/Kconfig

Purpose: Kconfig option for NVIDIA Tegra BPMP reset support.

Important APIs/types/functions: `RESET_TEGRA_BPMP` is a bool visible under COMPILE_TEST and defaults to `TEGRA_BPMP`.

Control flow: build-time selection only; runtime initialization is called by the BPMP driver.

State and persistence: kernel config controls inclusion.

Dependencies and integration: relies on Tegra BPMP support to provide reset IDs and message transport.

Risks and test signals: if defaulting diverges from BPMP availability, reset support may be compiled without usable firmware. Test COMPILE_TEST and Tegra BPMP enabled builds.
