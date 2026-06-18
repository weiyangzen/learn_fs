# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/Makefile

## Purpose
This Makefile maps ath11k Kconfig symbols to kernel objects. It builds the common ath11k module from core WLAN, firmware, control, datapath, hardware, QMI, and PCI-common components, then conditionally adds optional diagnostics, PM, thermal, coredump, spectral, testmode, and CFR objects. It also builds separate AHB and PCI bus modules.

## Important Build Rules
- `obj-$(CONFIG_ATH11K) += ath11k.o` creates the main ath11k module/built-in object.
- `ath11k-y` lists the mandatory common objects: `core.o`, `hal.o`, `hal_tx.o`, `hal_rx.o`, `wmi.o`, `mac.o`, `reg.o`, `htc.o`, `qmi.o`, datapath files, `debug.o`, copy-engine support, peer management, data-buffer-ring support, hardware tables, PCI-common code, firmware support, and P2P support.
- `ath11k-$(CONFIG_ATH11K_DEBUGFS)` adds `debugfs.o`, `debugfs_htt_stats.o`, and `debugfs_sta.o`.
- `ath11k-$(CONFIG_NL80211_TESTMODE)` adds `testmode.o`.
- `ath11k-$(CONFIG_ATH11K_TRACING)` adds `trace.o`.
- `ath11k-$(CONFIG_THERMAL)` adds `thermal.o`.
- `ath11k-$(CONFIG_ATH11K_SPECTRAL)` adds `spectral.o`.
- `ath11k-$(CONFIG_PM)` adds `wow.o`, tying WoW support to the kernel PM option.
- `ath11k-$(CONFIG_DEV_COREDUMP)` adds `coredump.o`.
- `ath11k-$(CONFIG_ATH11K_CFR)` adds `cfr.o`.
- `obj-$(CONFIG_ATH11K_AHB) += ath11k_ahb.o` with `ath11k_ahb-y += ahb.o` builds the AHB bus module.
- `obj-$(CONFIG_ATH11K_PCI) += ath11k_pci.o` with `ath11k_pci-y += mhi.o pci.o` builds the PCI bus module.
- `CFLAGS_trace.o := -I$(src)` ensures the tracing framework can find local `trace.h`.

## Control Flow
Kernel kbuild expands `obj-*` and `ath11k-*` variables based on resolved Kconfig symbols. The common module always receives the mandatory `ath11k-y` object list when `CONFIG_ATH11K` is enabled. Optional objects are linked into the same common module when their symbols are enabled. Bus-specific objects are built as separate modules or built-ins according to `ATH11K_AHB` and `ATH11K_PCI`, allowing one common driver core to be paired with different host interfaces.

## State and Persistence Behavior
The file has no runtime state. It persistently defines build composition. Runtime availability of features such as WoW, debugfs, spectral scan, tracing, thermal support, coredump, CFR, AHB, and PCI is determined by whether their object files are linked.

## Dependencies and Integration Points
The Makefile integrates with the Kconfig symbols in the sibling `Kconfig`, Linux kbuild module aggregation rules, and local source files in the ath11k directory. It also uses the broader kernel symbols `CONFIG_NL80211_TESTMODE`, `CONFIG_THERMAL`, `CONFIG_PM`, and `CONFIG_DEV_COREDUMP`. The local include flag for `trace.o` is an integration point with Linux trace event generation.

## Risks and Edge Cases
- Missing an object in `ath11k-y` can produce link failures or runtime feature holes even when Kconfig dependencies are correct.
- Optional source files must remain guarded by matching Kconfig symbols. For example, `wow.o` is linked solely under `CONFIG_PM`; code that references WoW symbols outside PM guards would fail.
- Bus modules depend on common-module symbols and initialization ordering. AHB/PCI object split must keep bus-specific code out of the common object list unless shared intentionally.
- Trace builds often require local header include paths; removing `CFLAGS_trace.o` can break generated trace compilation.

## Test Signals
Build tests should cover common-only, PCI, AHB, PM-enabled, debugfs-enabled, tracing-enabled, spectral/CFR-enabled, and coredump-enabled configurations. Expected artifacts are `ath11k.o`, optional objects folded into it, plus `ath11k_ahb.o` and/or `ath11k_pci.o` when bus support is enabled. A tracing build should compile `trace.o` without missing `trace.h`.
