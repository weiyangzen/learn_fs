# sources/distributed-fs/ceph-client/arch/mips/sibyte/common/Makefile

Purpose: common SiByte support build rules.

Important APIs and control flow: always builds CFE firmware support. It conditionally adds SWIOTLB DMA setup, bus watcher, CFE console, and ZBbus profiling objects based on config symbols.

State, persistence, and integration: no runtime state; it controls inclusion of common boot, DMA, diagnostics, and console support. Dependencies include Kconfig selections such as `CONFIG_SWIOTLB`, `CONFIG_SIBYTE_BUS_WATCHER`, and `CONFIG_SIBYTE_CFE_CONSOLE`. Risks include omitting diagnostics or DMA bounce setup when required by board memory/device constraints. Test signals are object inclusion and boot logs for CFE and optional diagnostics.
