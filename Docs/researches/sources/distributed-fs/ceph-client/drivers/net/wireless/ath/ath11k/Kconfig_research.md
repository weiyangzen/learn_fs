# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/Kconfig

## Purpose
This Kconfig file defines build-time configuration switches for the ath11k Qualcomm 802.11ax driver family. It controls the core ath11k module, AHB and PCI bus frontends, debug/debugfs/tracing features, spectral scan support, and channel frequency response dump support.

## Important Symbols
- `ATH11K` is the core tristate for Qualcomm Technologies 802.11ax chipset support. It depends on `MAC80211` and `HAS_DMA`, selects `ATH_COMMON` and `QCOM_QMI_HELPERS`, and builds a module named `ath11k` when modular.
- `ATH11K_AHB` is a tristate bus support option depending on `ATH11K` and `REMOTEPROC`; it enables AHB platform support.
- `ATH11K_PCI` is a tristate bus support option depending on `ATH11K` and `PCI`; it selects `MHI_BUS`, `QRTR`, `QRTR_MHI`, and conditionally `PCI_PWRCTRL_PWRSEQ` when `HAVE_PWRCTRL` is available.
- `ATH11K_DEBUG` is a boolean debug support switch depending on `ATH11K`.
- `ATH11K_DEBUGFS` is a boolean debugfs support switch depending on `ATH11K`, `DEBUG_FS`, and `MAC80211_DEBUGFS`.
- `ATH11K_TRACING` is a boolean tracing support switch depending on `ATH11K` and `EVENT_TRACING`.
- `ATH11K_SPECTRAL` is a boolean spectral scan switch depending on `ATH11K_DEBUGFS` and `RELAY`.
- `ATH11K_CFR` is a boolean channel frequency response dump switch depending on `ATH11K_DEBUGFS` and `RELAY`.

## Control Flow
Kconfig resolution determines which object lists in the ath11k Makefile are active. Enabling `ATH11K` provides the common module foundation. Enabling a bus option adds either the AHB or PCI module objects. Optional booleans then add debugfs, trace, spectral, CFR, thermal, PM, testmode, and coredump compilation paths via Makefile conditionals and broader kernel configuration symbols.

## State and Persistence Behavior
The file has no runtime state. It persists only build configuration choices in the kernel `.config`. Those choices determine which source files compile into built-in objects or modules and which runtime interfaces can exist.

## Dependencies and Integration Points
The file integrates ath11k into Linux wireless configuration. Its direct dependencies are mac80211, DMA support, remoteproc for AHB, PCI/MHI/QRTR for PCI devices, debugfs and mac80211 debugfs for debug interfaces, event tracing for tracepoints, and relay for spectral/CFR data export. The selected symbols ensure common ath support and QMI helpers are available to the driver.

## Risks and Edge Cases
- Incorrect dependency/select relationships can produce link failures or unusable runtime features. PCI support relies on MHI and QRTR selections; AHB relies on remoteproc.
- Debug-oriented options increase built code and expose debugfs or tracing surfaces. They are useful for diagnostics but should remain explicitly gated.
- `ATH11K_SPECTRAL` and `ATH11K_CFR` both depend on debugfs and relay; enabling either without the supporting kernel infrastructure would otherwise leave incomplete data paths.
- The help text recommends enabling debug options for easier problem diagnosis; distribution configs may choose differently to reduce attack surface or footprint.

## Test Signals
Configuration tests should cover `ATH11K=m` with `ATH11K_PCI=m`, `ATH11K_AHB=m`, and combinations of debugfs/tracing/spectral/CFR. Build output should show the matching module names from the Makefile. Kconfig tools should reject impossible combinations, such as PCI support without PCI or spectral support without debugfs/relay.
