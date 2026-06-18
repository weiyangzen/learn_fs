# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/Kconfig

## Purpose

This Kconfig file defines build-time configuration for ath5k: the main Atheros 5xxx mac80211 driver plus optional debug, tracing, AHB bus, PCI bus, and testing-channel support.

## Important Symbols

- `ATH5K`: main tristate driver option. It depends on `(PCI || ATH25) && MAC80211`, selects `ATH_COMMON`, selects `MAC80211_LEDS` when LED dependencies allow, and selects AHB on ATH25 or PCI otherwise.
- `ATH5K_DEBUG`: enables ath5k debug messages/debugfs controls.
- `ATH5K_TRACER`: enables ath5k tracepoints and depends on `EVENT_TRACING`.
- `ATH5K_AHB`: enables WiSoC/AHB support and depends on `ATH25 && ATH5K`.
- `ATH5K_PCI`: enables PCI support and depends on `!ATH25 && PCI`.
- `ATH5K_TEST_CHANNELS`: enables non-standard channels only under `CFG80211_CERTIFICATION_ONUS`.

## Control Flow

Kconfig resolution decides which Makefile conditionals include `ahb.o`, `pci.o`, and `debug.o`. ATH25 systems automatically select the AHB backend; non-ATH25 PCI systems select the PCI backend. The resulting module remains `ath5k`.

## State And Persistence Behavior

No runtime state is defined here. The persistent effect is the generated kernel configuration and the object set linked into `ath5k.o`. `ATH5K_TEST_CHANNELS` is a build-time regulatory/testing policy rather than a runtime toggle.

## Dependencies And Integration Points

The file integrates with `MAC80211`, `ATH_COMMON`, `PCI`, `ATH25`, `MAC80211_LEDS`, and event tracing. Its config symbols are consumed by the local Makefile.

## Risks

Bus selection assumes ATH25 means AHB and non-ATH25 PCI means PCI. Debug/tracing alter observability and may affect timing. Testing channels must remain certification-gated because they enable non-standard channels.

## Test Signals

Build matrix coverage should include module/built-in, ATH25 AHB, non-ATH25 PCI, debug on/off, tracer on/off, and testing-channel gating with `CFG80211_CERTIFICATION_ONUS`.
