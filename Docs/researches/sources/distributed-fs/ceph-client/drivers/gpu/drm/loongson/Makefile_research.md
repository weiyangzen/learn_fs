# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/Makefile

Purpose: defines object composition for the Loongson DRM module.

Important APIs/types/functions: `loongson-y` includes benchmark, CRTC, debugfs, core PCI DRM, GEM, GFX PLL, I2C, IRQ, LS7A1000/LS7A2000 outputs, planes, pixel PLL, probe, TTM, device descriptors, and module entry. `obj-$(CONFIG_DRM_LOONGSON)` links `loongson.o`.

Control flow: build-system only.

State and persistence: determines the module's linked symbol set.

Dependencies and integration points: all files in the list cooperate through `lsdc_drv.h` and chip-specific function tables.

Risks and test signals: excluding `lsdc_ttm.o` or a chip output file would break core references. Test module link and allmodconfig builds.
