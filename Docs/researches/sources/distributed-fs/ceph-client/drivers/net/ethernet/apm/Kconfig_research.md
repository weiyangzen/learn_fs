## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/Kconfig

Purpose: this top-level APM Ethernet Kconfig file delegates configuration to the two APM X-Gene Ethernet driver generations.

Important APIs, types, and functions: it has no C APIs; its only behavior is sourcing `drivers/net/ethernet/apm/xgene/Kconfig` and `drivers/net/ethernet/apm/xgene-v2/Kconfig`.

Control flow, state, and dependencies: Kconfig evaluation includes the legacy X-Gene and v2 driver menus in this directory. No persistent runtime state exists; build-time state is the selected symbols exported by the sourced files.

Integration points: used by the parent Ethernet Kconfig to expose APM vendor drivers. It must stay in sync with the subdirectory names and Makefile object gates.

Risks: a stale source path hides all APM driver options from configuration. Because it contains only includes, test coverage is mainly configuration discovery.

Test signals: run kernel config menu or `make olddefconfig` with `ARCH_XGENE`/`COMPILE_TEST`; verify `NET_XGENE` and `NET_XGENE_V2` remain visible and selectable.
