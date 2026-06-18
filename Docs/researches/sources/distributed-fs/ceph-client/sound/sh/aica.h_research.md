# sources/distributed-fs/ceph-client/sound/sh/aica.h

## Purpose
`aica.h` defines the Dreamcast AICA hardware addresses, command values, buffer layout, DMA constants, and driver-private state structures shared by `aica.c`.

## Important APIs, Types, And Functions
The header defines fixed addresses such as `G2_FIFO`, `SPU_MEMORY_BASE`, `ARM_RESET_REGISTER`, `SPU_REGISTER_BASE`, `AICA_CONTROL_POINT`, and `AICA_CONTROL_CHANNEL_SAMPLE_NUMBER`; commands `AICA_CMD_START`, `AICA_CMD_STOP`, and `AICA_CMD_VOL`; sample mode constants; buffer/period sizes; channel offsets; and DMA channel/mode constants. `struct aica_channel` is the command block copied to SPU memory. `struct snd_card_aica` holds ALSA card state, work/timer objects, the active channel, substream, period counters, volume, and DMA phase flag.

## Control Flow
No code executes here. `aica.c` fills `struct aica_channel` during PCM open/prepare, uploads it through `spu_memload()`, and uses the constants to address SPU memory and control registers during reset, start, stop, DMA, and pointer reporting.

## State And Persistence
The structures define the persistent runtime state allocated by `aica.c`. The constants encode hardware layout and therefore form a stable ABI with the Dreamcast SPU firmware loaded by the driver.

## Dependencies And Integration Points
This header is private to the AICA driver and depends on kernel integer types and work/timer/ALSA declarations already included by `aica.c`. It is tightly coupled to the firmware command block format.

## Risks And Edge Cases
Changing field order, command values, buffer sizes, or offsets can break firmware communication or DMA placement. Buffer and period constants are hard-coded into ALSA hardware constraints, DMA scheduling, and SPU memory layout.

## Test Signals
Tests should verify that channel control fields written by the driver match firmware expectations, pointer reads use the correct sample counter, and buffer/period constants remain consistent with ALSA hardware constraints and DMA transfer sizes.
