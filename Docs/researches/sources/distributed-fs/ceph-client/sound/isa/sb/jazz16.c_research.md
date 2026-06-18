# sources/distributed-fs/ceph-client/sound/isa/sb/jazz16.c

## Purpose
`jazz16.c` is the ALSA ISA driver for Media Vision Jazz16-based sound cards. It detects/configures the Jazz16 DSP, creates Sound Blaster DSP PCM and mixer devices, optional OPL3 and MPU401 devices, and basic suspend/resume support.

## Important APIs, Types, and Functions
- Module arrays configure card index/id/enable, DSP port, MPU port, IRQs, and 8/16-bit DMAs.
- Detection/configuration helpers: `jazz16_configure_ports`, `jazz16_detect_board`, and `jazz16_configure_board`.
- Bus callbacks: `snd_jazz16_match`, `snd_jazz16_probe`, PM suspend/resume, and `snd_jazz16_driver`.
- `jazz16_interrupt` delegates to `snd_sb8dsp_interrupt`.

## Control Flow
Match validates enabled flag, DSP port, DMA choices, MPU port, and MPU IRQ. Probe creates the card, auto-selects IRQ/DMA resources when requested, optionally configures the wakeup port `0x201` to map DSP and MPU ports, resets and identifies the DSP, creates an SB DSP instance, sends Jazz16 DMA/IRQ configuration commands, creates SB PCM and mixer, optionally creates OPL3 and MPU401 devices, registers the card, and stores driver data.

## State and Persistence
`struct snd_card_jazz16` stores the `struct snd_sb *` needed for suspend/resume. Runtime state is otherwise held by ALSA SB, mixer, OPL3, and MPU subsystems. No persistent storage exists.

## Dependencies and Integration Points
It integrates Linux ISA registration, ALSA Sound Blaster common/DSP/mixer APIs, OPL3, MPU401, legacy resource finders, and PM helpers.

## Risks and Test Signals
Risks include use of fixed config port `0x201`, resource mismatch where probed `xirq`/`xdma*` are not consistently passed to `snd_sbdsp_create` in the current code path, limited valid DMA/IRQ mappings, and optional-device failures. Test signals include board detection across wakeup indices, Jazz16 revision/model reads, SB PCM playback, mixer suspend/resume, OPL3 optional creation, MPU optional creation, and validation that auto-selected IRQ/DMA values are actually used.
