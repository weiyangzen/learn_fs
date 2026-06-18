# sources/distributed-fs/ceph-client/drivers/net/ethernet/engleder/Kconfig

Purpose: this Kconfig file exposes the Engleder Ethernet vendor menu and the TSN endpoint driver options.

Important APIs, types, and functions: it defines `NET_VENDOR_ENGLEDER` as a boolean vendor gate, `TSNEP` as a tristate "TSN endpoint support" driver option, and `TSNEP_SELFTESTS` as an optional boolean for driver self tests.

Control flow and state: Kconfig selection controls build-time inclusion only. If `NET_VENDOR_ENGLEDER` is disabled, the TSNEP questions are hidden. Selecting `TSNEP` requires `HAS_IOMEM`, `HAS_DMA`, and `PTP_1588_CLOCK_OPTIONAL`, and selects `PHYLIB` plus `PAGE_POOL`. `TSNEP_SELFTESTS` depends on `TSNEP` and gates the optional self-test object in the Makefile.

Dependencies and integration points: the symbol names are consumed by the local Makefile and the wider Ethernet Kbuild tree. The selected dependencies match the driver code: MMIO register access, DMA descriptor rings, PHYLIB link management, optional PTP hardware timestamping, and page_pool-backed RX.

Risks: missing dependencies would surface as compile failures in less common configurations, especially PTP/page-pool/XDP paths. Because `PTP_1588_CLOCK_OPTIONAL` is a dependency rather than a select, configurations without optional PTP support will not expose the driver. `NET_VENDOR_ENGLEDER` defaulting to `y` only controls menu visibility; it does not build TSNEP by itself.

Test signals: run `make olddefconfig` or menuconfig with and without `NET_VENDOR_ENGLEDER`, build `CONFIG_TSNEP=m` and `=y`, build with `CONFIG_TSNEP_SELFTESTS=y`, and compile-test on non-target architectures that satisfy `HAS_IOMEM` and `HAS_DMA`.
