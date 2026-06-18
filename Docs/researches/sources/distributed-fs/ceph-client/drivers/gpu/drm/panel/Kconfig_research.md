# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/Kconfig

Purpose: Defines the DRM panel framework menu and per-panel Kconfig symbols, dependencies, selected helper libraries, and user-facing descriptions.

Important APIs/types/functions: Top-level `DRM_PANEL` bool depends on `DRM`; `menu "Display Panels"` gates entries on `DRM && DRM_PANEL`. Listed symbols include the work-item panels such as `DRM_PANEL_ABT_Y030XX067A`, `DRM_PANEL_ARM_VERSATILE`, `DRM_PANEL_ASUS_Z00T_TM5P5_NT35596`, `DRM_PANEL_AUO_A030JTN01`, `DRM_PANEL_BOE_BF060Y8M_AJ0`, `DRM_PANEL_BOE_HIMAX8279D`, `DRM_PANEL_BOE_TD4320`, `DRM_PANEL_BOE_TH101MB31UIG002_28A`, and `DRM_PANEL_BOE_TV101WUM_LL2`, plus many other panel drivers.

Control flow: Kernel configuration selects panel drivers based on bus and support dependencies. SPI/regmap panels select `REGMAP_SPI` or `DRM_MIPI_DBI`; MIPI DSI panels depend on or select `DRM_MIPI_DSI`; many require `OF` and `BACKLIGHT_CLASS_DEVICE`; DSC/eDP panels select display helper libraries.

State and persistence: Kconfig symbols persist into `.config`, controlling object inclusion in the panel Makefile and module availability.

Dependencies and integration: Directly paired with `drivers/gpu/drm/panel/Makefile`. Symbol names must match `obj-$(CONFIG_...)` entries and source drivers.

Risks: Dependency mistakes surface as build failures or runtime probe gaps on platforms missing GPIO, regulator, backlight, DSI, SPI, syscon, or helper APIs. Help text contains some stale copy-paste descriptions, so it should not be used as a hardware authority without checking bindings/drivers.

Test signals: `make olddefconfig`, allmodconfig build coverage for panel drivers, dependency checks for each bus class, and symbol-to-Makefile consistency audits.
