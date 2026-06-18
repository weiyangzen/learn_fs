<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/spear_dma.h -->
# sources/distributed-fs/ceph-client/include/sound/spear_dma.h

## Purpose

`sources/distributed-fs/ceph-client/include/sound/spear_dma.h` is SPEAr platform audio header
carrying DMA or SPDIF platform data from board/platform setup into the ASoC driver. The source was
read as a complete 20-line header for this report.

## Important APIs, Types, and Functions

types: `spear_dma_data`; macros/constants: `SPEAR_DMA_H`

## Control Flow

Platform setup fills the small data structure before device registration; the audio driver consumes
DMA filter/channel or SPDIF capability data during probe and PCM configuration.

## State and Persistence Behavior

The header owns no state. The populated platform data is fixed for the platform-device lifetime and
may be cached by the driver.

## Dependencies and Integration Points

Direct includes: `linux/dmaengine.h`. Integrates with ALSA core, ASoC codec/card drivers,
rawmidi/seq, firmware loading, or legacy card drivers depending on the matching subsystem.

## Risks and Edge Cases

Risks include invalid DMA filter data, missing channel names, stale board data, and probe failures
when platform data is absent.

## Test Signals

Test platform-device probe, DMA channel lookup, playback/capture startup, SPDIF format negotiation,
and missing-data error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/spear_dma.h -->
