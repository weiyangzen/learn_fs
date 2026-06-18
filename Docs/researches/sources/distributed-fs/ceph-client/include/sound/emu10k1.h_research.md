# sources/distributed-fs/ceph-client/include/sound/emu10k1.h

## Purpose
This is the main internal ALSA header for Creative EMU10K1/SB Live!/Audigy and E-MU Digital Audio System drivers. It defines PCI and indexed-register maps, hardware bit-field helpers, DSP/voice/memory structures, card capability data, FPGA routing constants, and exported driver-internal entry points.

## Important APIs, Types, and Functions
Macro groups cover PCI registers (`PTR`, `DATA`, `IPR`, `INTE`, `WC`, `HCFG`, AC97, P16V), voice/channel registers, DSP microcode/TRAM/GPR ranges, Audigy-specific registers, E-MU Hana FPGA registers, and E-MU source/destination routing IDs. `SUB_REG*` encodes sub-register metadata; `REG_SHIFT/SIZE/MASK/VAL_*` manipulate those encoded fields. Core types include `snd_emu10k1_voice`, `snd_emu10k1_pcm`, `snd_emu10k1_pcm_mixer`, `snd_emu10k1_memblk`, `snd_emu10k1_fx8010_ctl`, `snd_emu10k1_fx8010_irq`, `snd_emu10k1_fx8010_pcm`, `snd_emu10k1_fx8010`, `snd_emu10k1_midi`, `snd_emu_chip_details`, `snd_emu1010`, and the central `struct snd_emu10k1`.

Exported entry points cover device creation, PCM devices, mixer/timer/FX8010 setup, interrupt handling, voice init/allocation/free, pointer register I/O, SPI/I2C, E-MU FPGA access/routing/clock/firmware, interrupt enable/ack helpers, AC97 access, PM save/restore, memory allocation/mapping, MIDI, procfs, and FX8010 IRQ registration.

## Control Flow
Driver probe calls `snd_emu10k1_create()` with PCI/card details, then creates PCM/mixer/timer/MIDI/FX components depending on card capability flags. Stream startup allocates voices and memory pages, maps them into the hardware page table, programs per-voice registers, enables channel loop/half-loop interrupts, and handles buffer interrupts through the main IRQ path. Capture paths use ADC/MIC/EFX/P16V register groups. E-MU cards additionally load FPGA firmware, configure Hana routing matrices, select word clock/optical modes, and update source/destination mappings.

## State and Persistence
`struct snd_emu10k1` owns nearly all runtime state: PCI port, DMA masks, page tables, mapped memory lists, SPDIF bits, I2C capture settings, FX8010 program/control state, AC97, PCM handles, synth pointer, locks, voices, E-MU routing/clock cache, kcontrols, interrupt callbacks, firmware handles, and PM save buffers. Hardware register state is volatile and explicitly saved/restored under `CONFIG_PM_SLEEP`. Memory blocks persist across stream lifetime and must be unmapped/freed in coordinated order.

## Dependencies and Integration Points
The header pulls ALSA PCM/rawmidi/hwdep/AC97/util_mem/timer APIs, Linux PCI/firmware/io/interrupt/mutex primitives, and UAPI EMU10K1 definitions. It integrates with the ALSA PCI driver, FX8010 DSP hwdep/control interfaces, sequencer/synth support, AC97 codecs, P16V, E-MU FPGA firmware, procfs, and PM.

## Risks and Edge Cases
This file is high-risk hardware code. Register definitions encode real side effects, including comments warning that some legacy or debug bits can cause unstable hardware behavior or destroy chip state. Voice/cache loop handling is timing-sensitive. DMA masks differ between EMU10K1 and Audigy. Lock ordering across `reg_lock`, `emu_lock`, `voice_lock`, `spi_lock`, `i2c_lock`, FX8010 mutexes, and FPGA lock must be preserved. E-MU routing constants overlap by sample-rate mode, so routing tables must account for 1x/2x/4x constraints. PM save buffers must cover all active engines.

## Test Signals
Useful tests include probe on SB Live, Audigy, P16V, and E-MU variants; playback/capture/MIC/EFX/multichannel streams; MIDI I/O; voice allocation exhaustion; loop/half-loop IRQs; FX8010 load/control/IRQ paths; AC97 read/write; suspend/resume with streams and DSP program; E-MU clock-source switching and FPGA routing; and memory allocation/free leak checks.
