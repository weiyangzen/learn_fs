# sources/distributed-fs/ceph-client/include/sound/sb.h

Source read summary: 363 lines, Sound Blaster legacy DSP/mixer/PCM interface.

Purpose: declares hardware types, DSP/mixer register constants, open/mode flags, core `snd_sb` state, DSP command helpers, mixer helpers, PCM/MIDI setup functions, and mixer-control construction macros for Sound Blaster compatible cards.

Important APIs, types, and functions: `enum sb_hw_type` classifies SB 1.x through ALS4000 variants. `struct snd_sb` stores card, ports/resources, IRQ/DMA, hardware version/type, mode/open/rate locks, mixer locks, rawmidi/PCM/OPL3 pointers, CSP pointer, and private fields. Macros define DSP I/O offsets, DSP commands, mixer device registers, IRQ/DMA setup bits, and mixer control encodings. APIs include DSP command/read/reset/create, mixer read/write/new/suspend/resume, SB8/SB16 PCM and MIDI setup/open/close/configure, PCM ops lookup, and mixer control add helpers.

Control flow: card probe resets the DSP, detects version, initializes mixer, configures IRQ/DMA, registers PCM/MIDI/OPL/CSP devices, and uses DSP commands to start/stop playback/capture DMA. IRQ handlers acknowledge 8/16-bit interrupts through inline helpers.

State and persistence behavior: per-card state tracks hardware resources, open modes, DMA/rate locks, mixer shadow behavior, and attached ALSA devices. Mixer/DSP registers persist only while hardware powered.

Dependencies and integration points: depends on ALSA core/control/PCM/rawmidi/timer/hwdep, OPL3, CSP, I/O port resources, and legacy ISA/PCI SB-compatible drivers.

Risks and edge cases: ISA DMA limits, IRQ/DMA setup mismatches, DSP reset timing, 8/16-bit mode conflicts, mixer register variants, and concurrent MIDI/PCM opens are fragile.

Test signals: DSP reset/version, SB8/SB16 playback/capture, MIDI UART, mixer controls, IRQ acknowledge, suspend/resume mixer restore, DMA channel variants, and ALS4000/DT019x register paths.
