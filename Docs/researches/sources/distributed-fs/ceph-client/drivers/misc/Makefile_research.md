## sources/distributed-fs/ceph-client/drivers/misc/Makefile

Purpose: this Makefile maps misc-driver Kconfig symbols to built-in objects, loadable modules, and subdirectory descents. It is the build-side counterpart to `drivers/misc/Kconfig`.

Important APIs, types, and functions: it uses kernel kbuild variables such as `obj-$(CONFIG_SYMBOL) += object.o` and composite object declarations for `lan966x-pci-objs`. Entries include AD525X common/I2C/SPI objects, IBM/POWER management drivers, sensor drivers, enclosure, SGI subdirectories, Qualcomm FastRPC, SRAM, endpoint test, security/virt helpers, TPS6594 children, CN10K DPI, and always-descended subdirectories such as `eeprom/`, `cb710/`, `lis3lv02d/`, `cardreader/`, `keba/`, and `amd-sbi/`.

Control flow: during kernel build, kbuild expands each `obj-*` line according to the configured symbol. `obj-y` entries are always entered for this directory build, though child contents still depend on their own Kconfig/Makefile choices. The LAN966x PCI driver is composed from `lan966x_pci.o` and a DT overlay object before being attached to `CONFIG_MCHP_LAN966X_PCI`.

State and persistence: build outputs are determined by `.config` and source timestamps. The Makefile itself carries no runtime state; it persists build topology and module naming conventions.

Dependencies and integration points: integrates with `drivers/misc/Kconfig`, per-driver source files, subdirectory Makefiles, kbuild composite object rules, and module autoload naming. The AD525X entries connect the common core object to transport-specific wrappers researched in this subset.

Risks and test signals: drift between Kconfig symbols and object names yields missing modules or dead options. Whitespace is mostly harmless but inconsistent entries can obscure review. Test signals are `make M=drivers/misc`, allmodconfig/randconfig link checks, and verifying module names match Kconfig help.
