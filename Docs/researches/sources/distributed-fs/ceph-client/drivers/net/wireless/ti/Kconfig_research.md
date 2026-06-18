# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/Kconfig

Purpose: Adds the top-level Texas Instruments wireless vendor menu for kernel configuration and includes all TI wireless subdriver Kconfig files.

Important APIs, types, and functions: Defines `config WLAN_VENDOR_TI` as a boolean, default `y`, and conditionally sources `wl1251`, `wl12xx`, `wl18xx`, and finally `wlcore` Kconfigs.

Control flow: Kconfig visibility is gated by `if WLAN_VENDOR_TI`; selecting `N` hides vendor-specific TI driver prompts without directly changing built objects.

State and persistence: Kconfig selections persist in the kernel `.config`, not in driver runtime state.

Dependencies and integration points: Integrates with Linux wireless Kconfig hierarchy and the Makefile's `CONFIG_*` object selection.

Risks: Because `wlcore` is sourced last for automatic dependencies, reordering can affect dependency resolution. Typo in help text says "Texas Instrument" rather than "Texas Instruments" but is nonfunctional.

Test signals: `oldconfig/menuconfig` visibility for TI drivers and build matrix with `WLAN_VENDOR_TI=n/y`.
