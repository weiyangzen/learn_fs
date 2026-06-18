# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/Makefile

Purpose: Maps DRM panel Kconfig symbols to built-in or modular object files.

Important APIs/types/functions: Contains one `obj-$(CONFIG_DRM_PANEL_...) += panel-... .o` entry per panel driver. Work-item entries map ABT, ARM Versatile, ASUS NT35596, AUO A030JTN01, BOE BF060, BOE Himax8279d, BOE TD4320, BOE TH101MB31IG002-28A, and BOE TV101WUM LL2 symbols to their objects.

Control flow: Kbuild includes an object when its Kconfig symbol is `y` or `m`, matching the driver registration macro used inside each source file.

State and persistence: No runtime state; build artifacts depend on `.config` and this mapping.

Dependencies and integration: Must stay in sync with `Kconfig`, source filenames, module names, and driver compatible tables.

Risks: A missing or mismatched object entry silently prevents a configured panel from building. Renames require synchronized Kconfig, Makefile, and source updates.

Test signals: allmodconfig/allyesconfig builds, script checks for every `DRM_PANEL_*` symbol having the expected object, and module load tests for selected panel drivers.
