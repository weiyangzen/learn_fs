# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/Makefile

Purpose: this Makefile maps MT76x0 Kconfig symbols to kernel module objects. It is the build glue between `MT76x0_COMMON`, USB, and PCIe support.

Important targets: `mt76x0-common-y` contains `init.o`, `main.o`, `eeprom.o`, and `phy.o`. `mt76x0u-y` contains `usb.o` and `usb_mcu.o` outside this subset. `mt76x0e-y` contains `pci.o` and `pci_mcu.o`. The top-level `obj-$(CONFIG_...)` lines produce `mt76x0-common.o`, `mt76x0u.o`, and `mt76x0e.o` as selected.

Control flow and integration: the file ensures both bus modules link against the shared common module. `pci.c` and `pci_mcu.c` are built only for the PCIe variant; USB transport files are separate and not researched here.

State and persistence behavior: no runtime state. The persistent effect is object composition and module names in the kernel build output.

Dependencies: symbol names must match `Kconfig`, and object names must match source files. The commented `ccflags-y := -DDEBUG` is a local debug knob, left disabled.

Risks: adding common APIs without updating object membership causes unresolved symbols. Moving code between common and bus modules can change module dependencies and autoload behavior.

Test signals: kernel/module build with USB-only, PCI-only, and both variants should emit the expected objects and no unresolved exports from common code.
