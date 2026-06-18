# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/Kconfig

Purpose: Kconfig definitions for the ath10k 802.11ac driver family and its bus/debug feature variants.

Important APIs/types/functions: `ATH10K` is the main tristate requiring `MAC80211` and `HAS_DMA`; it selects `ATH_COMMON`, `CRC32`, `WANT_DEV_COREDUMP`, and `ATH10K_CE`. Bus options include `ATH10K_PCI`, `ATH10K_AHB`, `ATH10K_SDIO`, `ATH10K_USB`, and `ATH10K_SNOC`. Feature switches include `ATH10K_DEBUG`, `ATH10K_DEBUGFS`, `ATH10K_LEDS`, `ATH10K_SPECTRAL`, `ATH10K_TRACING`, and `ATH10K_DFS_CERTIFIED`.

Control flow: `ATH10K` enables the core object and CE support. PCI, SDIO, USB, and SNOC create separate bus modules; AHB is a bool depending on `ATH10K_PCI`, OF, and reset controller support because the AHB implementation reuses PCI internals. Debugfs, tracing, thermal, LEDs, spectral, and DFS support conditionally compile extra code from the Makefile.

State/persistence: Configuration persists in kernel `.config` and controls module composition. Runtime state is in ath10k core/bus drivers.

Dependencies/integration: Integrates with mac80211, DMA, PCI/MMC/USB/platform/QCOM subsystems, debugfs, relay, event tracing, LED class, devcoredump, QMI helpers, power sequencing, and DFS certification policy.

Risks: Some options are intentionally experimental or policy-sensitive. `ATH10K_USB` is marked work in progress. `ATH10K_DFS_CERTIFIED` requires certification onus. The `ATH10K_AHB` dependency on PCI is non-obvious but required by code reuse.

Test signals: Matrix builds across bus variants and feature flags, plus `allmodconfig`/`allyesconfig`, validate dependency correctness and object inclusion.
