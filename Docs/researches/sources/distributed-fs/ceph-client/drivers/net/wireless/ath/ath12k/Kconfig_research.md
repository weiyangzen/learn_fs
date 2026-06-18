# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/Kconfig

## Purpose
`ath12k/Kconfig` defines the build-time configuration surface for the Qualcomm Wi-Fi 7 ath12k driver. It controls the core module, optional AHB bus support, debug logging, debugfs, tracepoints, and coredump collection.

## Important Symbols
- `CONFIG_ATH12K` is a tristate core option for Wi-Fi 7 chipsets such as WCN7850 and QCN9274. It depends on `MAC80211`, `HAS_DMA`, and `PCI`, and selects QMI, MHI, QRTR, QRTR_MHI, and optional PCI power sequencing support.
- `CONFIG_ATH12K_AHB` enables AHB platform-bus chipsets, depends on `ATH12K` and `REMOTEPROC`, and selects Qualcomm MDT loader and SCM support.
- `CONFIG_ATH12K_DEBUG`, `CONFIG_ATH12K_DEBUGFS`, `CONFIG_ATH12K_TRACING`, and `CONFIG_ATH12K_COREDUMP` toggle optional observability and dump paths.

## Control Flow And State Behavior
Kconfig has no runtime control flow, but it shapes compiled objects and module capabilities. Enabling `ATH12K` produces `ath12k.o`; optional symbols control whether `ahb.o`, debugfs, trace, coredump, and other conditional objects are linked by the Makefile. `ATH12K_AHB` expands runtime support from PCI/MHI-attached hardware to remoteproc-backed platform devices.

## Dependencies And Integration Points
This file integrates ath12k into the Linux wireless Kconfig tree. It depends on mac80211 and DMA for the core datapath, PCI for the baseline driver, MHI/QMI/QRTR for firmware control, REMOTEPROC/SCM/MDT for AHB firmware boot, debugfs/event tracing for observability, and devcoredump for firmware crash capture.

## Risks And Edge Cases
- `ATH12K` depends on `PCI`, so even AHB-only builds still require PCI dependency satisfaction through the core symbol.
- Optional debug features can alter object coverage and exported interfaces; build combinations must cover disabled debugfs/tracing/coredump paths.
- AHB support selects remote firmware loading/authentication infrastructure and must track platform firmware availability.

## Test Signals
Validate allyesconfig/allmodconfig, minimal `ATH12K=m`, `ATH12K_AHB=y` with remoteproc dependencies, debugfs off/on builds, tracing off/on builds, coredump off/on builds, and module naming/load behavior for `ath12k`.
