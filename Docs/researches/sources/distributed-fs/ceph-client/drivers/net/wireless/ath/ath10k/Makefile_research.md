# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/Makefile

Purpose: Kbuild file for ath10k core and bus-specific modules.

Important APIs/types/functions: `ath10k_core-y` lists core mac80211, HTC/HTT, WMI, BMI, hardware, P2P, swap, TX/RX, and debug objects. Conditional additions include spectral, testmode, trace, thermal, LEDs, station debugfs, WoW, coredump, and CE. Bus modules are `ath10k_pci.o`, `ath10k_sdio.o`, `ath10k_usb.o`, and `ath10k_snoc.o`; `ahb.o` is conditionally linked into `ath10k_pci` when `ATH10K_AHB` is enabled.

Control flow: Kbuild creates a core module for `CONFIG_ATH10K`, then adds bus modules according to their symbols. The AHB source is linked with PCI support, reflecting its reuse of PCI CE, interrupt, resource, and HIF helpers.

State/persistence: Build outputs only.

Dependencies/integration: Mirrors Kconfig feature choices and wires source files into the module graph. `CFLAGS_trace.o := -I$(src)` supports local trace header discovery.

Risks: Because many features are optional, missing conditional objects create unresolved references only in specific configs. AHB's placement under `ath10k_pci` can surprise maintainers splitting bus code.

Test signals: Compile tests for combinations of PCI/AHB/SDIO/USB/SNOC and optional debugfs/tracing/spectral/thermal/PM/devcoredump options are the primary validation.
