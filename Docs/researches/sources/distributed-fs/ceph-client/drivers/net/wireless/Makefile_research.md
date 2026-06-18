# sources/distributed-fs/ceph-client/drivers/net/wireless/Makefile

Purpose: Selects wireless vendor subdirectories for compilation based on Kconfig symbols.

Important APIs and definitions: Adds vendor directories to `obj-y`/`obj-m` through `obj-$(CONFIG_WLAN_VENDOR_*) += <vendor>/`, including `admtek/`, `ath/`, `broadcom/`, `intel/`, and others. Adds `virtual/` when `CONFIG_WLAN` is enabled.

Control flow: Kbuild descends into each enabled vendor directory and into virtual wireless drivers when WLAN is enabled.

State and persistence: Build-time only; no runtime state.

Dependencies and integration points: Mirrors the top-level wireless Kconfig vendor list and relies on each subdirectory Makefile to map concrete driver symbols to objects.

Risks: Kconfig/Makefile drift can expose a config option that never builds, or build a directory with no visible config. Vendor ordering can affect link order for built-in objects.

Test signals: Build with representative vendor symbols enabled/disabled, `make drivers/net/wireless/`, and consistency check against Kconfig sources.
