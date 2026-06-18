# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-pltfm.h

## Purpose
This header defines the shared data structures and helper declarations for SDHCI platform drivers. It also provides optional big-endian 32-bit byte-swapper accessors used by platforms whose register windows require swapped sub-word addressing.

## Important APIs, Types, And Functions
`struct sdhci_pltfm_data` carries a platform driver's ops and initial quirk sets. `struct sdhci_pltfm_host` stores the platform clock, optional fixed clock frequency, transfer-mode shadow, and aligned private storage. `sdhci_pltfm_priv()` returns the private tail after the wrapper. Declarations expose `sdhci_get_property()`, `sdhci_get_of_property()`, `sdhci_pltfm_init()`, `sdhci_pltfm_init_and_add_host()`, `sdhci_pltfm_remove()`, `sdhci_pltfm_clk_get_max_clock()`, `sdhci_pltfm_pmops`, and sleep PM helpers.

## Control Flow
Platform drivers pass `struct sdhci_pltfm_data` and a private-size value into `sdhci_pltfm_init()`. The returned host's `sdhci_priv(host)` points to `struct sdhci_pltfm_host`; driver-private data is retrieved through `sdhci_pltfm_priv()`. With the BE byte-swapper config enabled, drivers can install accessors that map SDHCI sub-word operations onto big-endian 32-bit MMIO. The writew accessor shadows `SDHCI_TRANSFER_MODE` and emits transfer mode together with `SDHCI_COMMAND`.

## State And Persistence
The header defines persistent per-host platform state rather than storing it itself. `xfer_mode_shadow` is important for byte-swapped controllers because transfer mode must be combined with command writes. Conditional PM stubs return success when sleep PM is disabled, allowing drivers to reference helpers without config-specific code.

## Dependencies And Integration Points
It includes the clock framework, platform devices, and `sdhci.h`. Nearly all platform SDHCI glue drivers include it to use the common allocation, private-data layout, and optional PM operations.

## Risks
The private-data layout is easy to misuse: `sdhci_priv(host)` is the platform wrapper, while `sdhci_pltfm_priv()` is driver-private data. The BE byte-swapper accessors rely on exact SDHCI command/transfer register semantics and can corrupt command issue order if reused incorrectly. Conditional accessor definitions mean build coverage must include both endian configurations if touched.

## Test Signals
Compile platform drivers with and without `CONFIG_PM_SLEEP` and with BE byte-swapper enabled where possible. Runtime signals are correct private pointer use, command issuance on byte-swapped controllers, and shared PM helper linkage.
