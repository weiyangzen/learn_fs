# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/Makefile

## Purpose
This Makefile maps the Kconfig symbols in the `rtw88` directory to kernel modules and object composition. It defines the common `rtw88_core.o`, per-chip modules, per-adapter bus glue modules, and transport modules for PCI, SDIO, and USB.

## Important build products
`rtw88_core-y` contains the shared implementation: `main.o`, `mac80211.o`, `util.o`, `debug.o`, `tx.o`, `rx.o`, `mac.o`, `phy.o`, `coex.o`, `efuse.o`, `fw.o`, `ps.o`, `sec.o`, `bf.o`, `sar.o`, and `regd.o`. Optional core pieces are `wow.o` under `CONFIG_PM` and `led.o` under `CONFIG_RTW88_LEDS`.

Chip-family modules include `rtw88_8822b.o`, `rtw88_8822c.o`, `rtw88_8723x.o`, `rtw88_8703b.o`, `rtw88_8723d.o`, `rtw88_8821c.o`, `rtw88_88xxa.o`, `rtw88_8821a.o`, `rtw88_8812a.o`, and `rtw88_8814a.o`, usually pairing logic files with generated or static table files. Concrete bus modules include names such as `rtw88_8822be.o`, `rtw88_8822bs.o`, `rtw88_8822bu.o`, `rtw88_8821au.o`, and `rtw88_8814ae.o`. Transport modules are `rtw88_pci.o`, `rtw88_sdio.o`, and `rtw88_usb.o`.

## Control flow and integration
The kernel build system expands `obj-$(CONFIG_...)` and `*-objs` lists. Kconfig selects decide which modules are built; this file decides which compilation units are linked into each module. The common core always includes coexistence and beamforming support (`coex.o`, `bf.o`), while chip modules provide operation tables consumed by the core.

## State and persistence behavior
The Makefile has no runtime state. Build output state is determined by `.config` and by module/built-in linkage decisions. Optional PM and LED source objects are compiled only when their associated configs are active.

## Dependencies and integration points
This file must stay synchronized with `Kconfig`, source filenames, module aliases/device tables in adapter files, and exported symbols between core, chip, and transport modules. It also relies on kernel kbuild conventions for composite object names and conditional object lists.

## Risks and test signals
Risks are mostly build graph breakage: missing an object in a composite module, stale source names, adding a Kconfig symbol without an object rule, or linking an adapter module without its chip/transport dependency. Test signals include targeted `M=drivers/net/wireless/realtek/rtw88` builds for each enabled adapter, modpost symbol checks, module load ordering, and runtime probe on PCI/SDIO/USB variants.
