# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/Kconfig

## Purpose
Defines kernel configuration options for the legacy Broadcom 43xx mac80211 driver. It controls whether `b43legacy` builds, which SSB host glue is auto-selected, optional LED and hardware RNG integration, debug support, and whether DMA, PIO, or both transfer backends are compiled.

## Important APIs, Types, and Functions
The top-level symbol is `B43LEGACY`, a tristate depending on `SSB_POSSIBLE`, `MAC80211`, and `HAS_DMA`, selecting `SSB` and `FW_LOADER`. Helper symbols include `B43LEGACY_PCI_AUTOSELECT`, `B43LEGACY_PCICORE_AUTOSELECT`, `B43LEGACY_LEDS`, `B43LEGACY_HWRNG`, `B43LEGACY_DEBUG`, `B43LEGACY_DMA`, and `B43LEGACY_PIO`. The transfer-mode choice selects `B43LEGACY_DMA_AND_PIO_MODE`, `B43LEGACY_DMA_MODE`, or `B43LEGACY_PIO_MODE`.

## Control Flow
Kconfig selection determines compile-time code paths. If both DMA and PIO are compiled, runtime module parameter `pio` can choose PIO; otherwise inline stubs and `b43legacy_using_pio` collapse to the compiled backend. LED and debugfs code are conditionally compiled through their respective config symbols. PCI SSB bridge symbols are auto-selected only when their platform support is possible.

## State and Persistence
Kconfig state persists in kernel build configuration, not driver runtime. It shapes module features, available module parameters, and whether optional state objects such as LED class devices, debugfs entries, or hwrng registration exist.

## Dependencies and Integration Points
Integrates with the kernel build system, SSB bus support, firmware loader, mac80211, LED class/mac80211 LED trigger support, and hwrng. Help text also documents the external requirement for V3 firmware installed with b43-fwcutter.

## Risks
Misconfigured transfer mode can omit the only working data path for a device. PIO-only builds are slower and may not support all devices. `B43LEGACY_DEBUG` defaults to enabled, which improves diagnostics but increases code and logging surface. Firmware absence is not represented as a build dependency and only fails at runtime.

## Test Signals
Build matrix coverage for module/built-in states, DMA-only, PIO-only, DMA+PIO, LED-enabled/disabled, debugfs-enabled/disabled, and hwrng-enabled/disabled is the main signal. Runtime probing should confirm both `b43` and `b43legacy` can coexist and SSB loads the appropriate driver.
