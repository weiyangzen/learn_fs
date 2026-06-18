# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/Makefile

## Purpose
This Makefile maps the `rtlwifi` Kconfig symbols to built objects and subdirectories. It builds the shared `rtlwifi.o` core, PCI and USB transport modules, chip-family common directories, per-device directories, and the optional Bluetooth coexistence library.

## Important APIs, Types, And Functions
The main object aggregate is `rtlwifi-objs`, made from `base.o`, `cam.o`, `core.o`, `debug.o`, `efuse.o`, `ps.o`, `rc.o`, `regd.o`, and `stats.o`. Transport aggregates are `rtl_pci-objs := pci.o` and `rtl_usb-objs := usb.o`. The Makefile then attaches subdirectories to symbols such as `RTL8192C_COMMON`, `RTL8192CE`, `RTL8192CU`, `RTL8192SE`, `RTL8192D_COMMON`, `RTL8192DE`, `RTL8192DU`, `RTL8723AE`, `RTL8723BE`, `RTL8188EE`, `RTLBTCOEXIST`, `RTL8723_COMMON`, `RTL8821AE`, and `RTL8192EE`.

## Control Flow
Build flow is declarative. When `CONFIG_RTLWIFI` is enabled, kbuild links the shared core object. Transport symbols pull in transport modules. Device and common-family symbols recurse into their subdirectories. Bluetooth coexistence is included only when `CONFIG_RTLBTCOEXIST` is enabled.

## State And Persistence
The Makefile persists no runtime state. It determines the module/object graph emitted by kbuild and therefore the boundaries of loadable modules and built-in code. The core module exports many helpers from `base.c` and adjacent files for transport and per-chip modules.

## Dependencies And Integration Points
It depends on the Kconfig file for `CONFIG_*` symbol validity and on each listed source file/subdirectory existing with matching object names. It integrates the shared core with transport and chip modules, including `btcoexist/Makefile` for coexistence code.

## Risks
Incorrect object membership can create unresolved symbols or duplicated definitions. Missing subdirectory wiring can silently omit a device driver even when Kconfig exposes it. The empty `rtl8192c_common-objs +=` line is harmless but notable because actual 8192C common code is built through the subdirectory entry, not this aggregate.

## Test Signals
Signals are successful kbuild for modular and built-in combinations, expected `.ko` names (`rtlwifi`, `rtl_pci`, `rtl_usb`, per-chip modules, and `btcoexist`), `modpost` without unresolved symbols, and probe tests proving per-chip modules can use shared core exports.
