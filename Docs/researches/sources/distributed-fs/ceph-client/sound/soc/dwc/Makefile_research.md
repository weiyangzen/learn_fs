# sources/distributed-fs/ceph-client/sound/soc/dwc/Makefile

## Purpose
This Makefile maps DesignWare ASoC Kconfig symbols to build objects. It builds the core I2S driver and conditionally folds in the PIO PCM extension.

## Important APIs, Types, And Functions
`obj-$(CONFIG_SND_DESIGNWARE_I2S) += designware_i2s.o` emits the aggregate driver object. `designware_i2s-y := dwc-i2s.o` always includes the platform/DAI driver. `designware_i2s-$(CONFIG_SND_DESIGNWARE_PCM) += dwc-pcm.o` conditionally adds the PIO component implementation.

## Control Flow
Kbuild evaluates the configuration symbols, builds `dwc-i2s.o`, optionally builds `dwc-pcm.o`, links them into `designware_i2s.o`, and then links that aggregate as built-in or module according to `SND_DESIGNWARE_I2S`.

## State And Persistence
There is no runtime state. The Makefile encodes build-time composition of the driver.

## Dependencies And Integration Points
It integrates directly with `sound/soc/dwc/Kconfig` symbols and the local `local.h` conditional prototypes. The resulting object provides the platform driver named `designware-i2s`.

## Risks And Edge Cases
If `SND_DESIGNWARE_PCM` is disabled, the core can still call `dw_pcm_register()` only through the inline `-EINVAL` stub in `local.h`; platforms requiring PIO will fail PCM registration at runtime. Object aggregation means symbol visibility and module metadata come from `dwc-i2s.c`.

## Test Signals
Inspect generated build commands for both config states. Runtime smoke tests should verify DMAengine registration when PIO is absent and custom PCM registration when `dwc-pcm.o` is present.
