# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/Makefile

## Purpose

This Makefile maps ath9k Kconfig symbols to kernel objects. It builds the main `ath9k` softmac module, the shared `ath9k_hw` hardware library, `ath9k_common`, the USB `ath9k_htc` module, and the optional PCI EEPROM-less loader.

## Important build targets

- `ath9k-y` contains core runtime objects such as beacon, GPIO, init, main, receive, transmit, link, antenna, and channel support.
- Conditional `ath9k-*` entries add MCI bluetooth coexistence, PCI, AHB, DFS debug/certified files, TX99, WOW, HWRNG, debugfs, and station statistics.
- `ath9k_hw-y` builds hardware support: AR9002/AR9003 hardware, PHY/MAC, calibration, EEPROM formats, ANI, PAPRD, and optional WOW/BT coexistence/PCOEM/dynamic ACK components.
- `ath9k_common-y` builds shared helper code for common init/beacon/debug/spectral functionality.
- `ath9k_htc-y` builds the USB HTC stack with host transport, HIF USB, WMI, TX/RX, main/beacon/init/GPIO, and optional debug.

## Control flow and integration

The file consumes symbols from `Kconfig` and decides object composition at build time. The generated modules are linked by Kbuild according to `obj-$(CONFIG_...)` lines. Runtime entry points in `init.c`, bus-specific files, and HTC files depend on these object lists being consistent with selected capabilities.

## State and persistence behavior

No runtime state exists. The Makefile persists build topology: changing it alters which code is present in modules and which symbols can resolve. Conditional object inclusion is the build-time equivalent of feature state.

## Dependencies and risks

The main risk is mismatch between Kconfig dependencies and object references. For example, enabling AHB requires `ahb.o` plus OF support, and BT coexistence pulls both high-level and hardware MCI/AIC pieces. Missing optional objects can produce unresolved symbols; extra objects can expose unsupported features or increase module size.

## Test signals

Build-test representative configs: `ATH9K=m` with PCI, with AHB, with both, `ATH9K_HTC=m`, debugfs/spectral combinations, WOW, BT coexistence, DYNACK, HWRNG, TX99, DFS, and `ATH9K_PCI_NO_EEPROM`. Inspect linked module contents or `modinfo` to verify expected objects are included.
