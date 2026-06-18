# sources/distributed-fs/ceph-client/sound/soc/au1x/psc.h

## Purpose
Shared private header for Alchemy Au1x ASoC PSC/legacy audio drivers. It defines the common per-device state container and convenience macros for PSC/I2S/AC97 register offsets.

## Important APIs, Types, And Functions
- `struct au1xpsc_audio_data` holds MMIO base, cached config/rate, cloned DAI driver, PM save slots, mutex, and two DMA IDs.
- Macros such as `PSC_CTRL`, `PSC_SEL`, `I2S_STAT`, `I2S_CFG`, `I2S_PCR`, `AC97_CFG`, `AC97_CDC`, `AC97_EVNT`, `AC97_PCR`, `AC97_RST`, and `AC97_STAT` compute register addresses from `mmio`.

## Control Flow
No executable control flow; it is included by Au1x AC97/I2S/DMA/machine support files.

## State And Persistence
Defines the shared state shape. Actual state lifetime is controlled by each platform driver.

## Dependencies And Integration Points
Assumes Alchemy PSC offset macros are visible from architecture headers included by C files. It also requires ASoC DAI and mutex types through including translation units.

## Risks
The generic name `_AU1X_PCM_H` and shared struct are private conventions. Any field layout change affects multiple drivers. Register macros perform raw pointer arithmetic and rely on valid MMIO mapping.

## Test Signals
Build coverage of all Au1x files after header changes and runtime register access through AC97/I2S drivers.
