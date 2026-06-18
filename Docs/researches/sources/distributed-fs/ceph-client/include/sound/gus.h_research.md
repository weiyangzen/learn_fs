# sources/distributed-fs/ceph-client/include/sound/gus.h

## Purpose
This is the main ALSA internal header for Gravis UltraSound/GF1-family cards. It defines I/O ports, GF1 registers, memory/DMA/voice/card state, inline port helpers, and exported functions for memory, DMA, mixer, PCM, MIDI, timers, reset, IRQ, and DRAM access.

## Important APIs, Types, and Functions
Macro groups define GUS I/O port offsets, GF1 global and voice registers, ICS mixer devices, LFO modes, DMA flags, volume ranges, memory-owner flags, interrupt-handler flags, and voice types/flags. Core types include `snd_gf1_mem_block`, `snd_gf1_mem`, `snd_gf1_dma_block`, `snd_gus_port`, `snd_gus_voice`, `snd_gf1`, and `snd_gus_card`. Inline helpers select active voice and access the MIDI UART. Exports cover GF1 register I/O, memory allocation/free/init/proc, DMA transfer/suspend, volume/frequency conversion, voice allocation/start/stop/suspend/resume, mixer/PCM/card creation, IRQ handling, rawmidi, DRAM read/write, and timers.

## Control Flow
Card creation initializes hardware resources, memory banks, GF1 voices, DMA queues, mixer, PCM, MIDI, and timers. Playback/synth code allocates voices and GF1 memory blocks, programs voice registers, and handles voice/DMA/timer interrupts. DMA transfers enqueue `snd_gf1_dma_block` objects and acknowledge through callbacks. MIDI UART helpers directly access port registers.

## State and Persistence
`struct snd_gus_card` owns card-wide state, locks, PCM capture position, MIDI substreams, and a nested `snd_gf1` with hardware ports, memory allocator, active voices, timer/MIDI/DMA queues, PCM volume levels, and interrupt callbacks. GUS DRAM/ROM contents and GF1 registers are hardware state; DRAM sample contents are volatile.

## Dependencies and Integration Points
The header depends on ALSA PCM/rawmidi/timer/sequencer APIs and Linux I/O. It integrates with legacy ISA/PNP GUS drivers, GF1 synth/PCM code, raw MIDI, timers, procfs memory reporting, and userspace DRAM read/write operations.

## Risks and Edge Cases
Hardware port access is immediate and requires correct locks around active voice, registers, DMA queues, UART, and PCM volume. Memory sharing uses share IDs and owner classes; incorrect free paths can leak or release active samples. Equal IRQ/DMA and optional codec/ICS/InterWave/ESS flags complicate resource setup. User DRAM read/write must validate addresses and ROM selection.

## Test Signals
Probe across classic GUS/MAX/InterWave/ACE variants, memory allocator ownership/share behavior, DMA transfers for PCM and synth, voice allocation/free, MIDI UART, timers, IRQ profile under stress, DRAM read/write bounds, and suspend/resume are useful tests.
