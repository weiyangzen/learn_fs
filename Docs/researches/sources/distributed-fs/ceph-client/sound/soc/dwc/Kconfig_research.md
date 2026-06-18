# sources/distributed-fs/ceph-client/sound/soc/dwc/Kconfig

## Purpose
This Kconfig fragment defines the DesignWare ASoC driver menu. It offers the Synopsys DesignWare I2S controller driver and an optional PIO PCM extension for controllers without DMA support.

## Important APIs, Types, And Functions
The file defines `SND_DESIGNWARE_I2S` as a tristate option depending on `HAVE_CLK` and selecting `SND_SOC_GENERIC_DMAENGINE_PCM`. It also defines `SND_DESIGNWARE_PCM` as a bool depending on `SND_DESIGNWARE_I2S`, used to compile the custom PIO backend in `dwc-pcm.c`.

## Control Flow
Kconfig selection controls whether `designware_i2s.o` is built and whether `dwc-pcm.o` is linked into it. Enabling the I2S driver pulls in generic DMAengine PCM support; enabling the PCM extension adds an IRQ/PIO fallback for non-DMA devices.

## State And Persistence
There is no runtime state. The configuration persists in the kernel build config and determines compiled code paths and helper stubs exposed through `local.h`.

## Dependencies And Integration Points
`SND_DESIGNWARE_I2S` integrates with the ASoC sound subsystem and common clock framework. `SND_DESIGNWARE_PCM` integrates with the local DesignWare driver and is consumed by `Makefile` and `local.h` conditional declarations.

## Risks And Edge Cases
The PIO option is bool, not tristate, so it follows the built module/object shape of the parent and cannot be independently loaded. DMAengine support is selected even when platforms will use PIO, which is harmless but broadens build dependencies.

## Test Signals
Build-test combinations should include I2S disabled, I2S built-in, I2S modular, and I2S plus PIO extension. Config tests should verify `dwc-pcm.o` is included only when `SND_DESIGNWARE_PCM=y` and that stubs are used otherwise.
