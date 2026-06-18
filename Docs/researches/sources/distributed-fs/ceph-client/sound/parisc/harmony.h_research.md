# sources/distributed-fs/ceph-client/sound/parisc/harmony.h

## Purpose

`harmony.h` provides the private data structures, buffer sizing constants, register offsets, bit masks, gain-field definitions, and sample-rate encoding constants used by the PA-RISC Harmony ALSA driver.

## Important APIs, Types, and Functions

The primary types are `struct harmony_buffer`, describing DMA address, current buffer offset, period count, total size, and coherency flag, and `struct snd_harmony`, the complete per-device driver state. Constants define one PCM device, four substreams maximum, no MIDI devices, 64 bytes of MMIO space, page-sized periods, 16 maximum periods, and one-page graveyard/silence buffers.

Register constants cover `HARMONY_ID`, `RESET`, `CNTL`, `GAINCTL`, next/current playback and record addresses, `DSTATUS`, overflow, PIO, and diagnostic registers. Bitfields define control command/stereo/rate bits, interrupt status and enable bits, data formats, mono/stereo selectors, gain mute/default values, output enable/input select bits, monitor/input/output gain masks, and Harmony sample-rate codes.

## Control Flow

There is no executable control flow. The constants are consumed by `harmony.c` to program control words, interpret interrupt status, configure PCM formats and rates, expose mixer controls, and allocate DMA buffers with constraints that match hardware register behavior.

## State and Persistence

The header defines the shape of runtime state but stores none itself. Its fields persist in each allocated `struct snd_harmony` for the life of a probed device.

## Dependencies and Integration Points

It depends on ALSA and PA-RISC types included by `harmony.c` before this header. Register definitions are tightly coupled to the Harmony/Vivace hardware and to ALSA PCM constraints in the C file.

## Risks and Edge Cases

Register and bit constants have no type safety, so incorrect shifts or masks can affect unrelated gain/control bits. `BUF_SIZE` is fixed at `PAGE_SIZE`, making period size inflexible. The `coherent` field in `struct harmony_buffer` is present but unused in the current C file. Any hardware variant with different MMIO size or rate encodings would need header changes.

## Test Signals

Compile coverage is the main signal. Runtime validation should confirm that each ALSA supported rate maps to the intended `HARMONY_SR_*` code, gain controls affect the expected bits, and period buffer constraints match the hardware DMA address stepping.
