# sources/distributed-fs/ceph-client/sound/isa/sb/sb_common.c

## Purpose
This file provides the shared low-level Sound Blaster DSP creation, command, byte-read, reset, and hardware-detection routines used by SB8, SB16, and compatible drivers. It also exports mixer functions implemented in `sb_mixer.c`.

## Important APIs, Types, and Functions
Exports include `snd_sbdsp_command()`, `snd_sbdsp_get_byte()`, `snd_sbdsp_reset()`, and `snd_sbdsp_create()`. Internal helpers are `snd_sbdsp_version()` and `snd_sbdsp_probe()`. `snd_sbdsp_create()` allocates and initializes `struct snd_sb`, requests IRQ, IO region, and ISA DMA channels, then probes the DSP.

## Control Flow
`snd_sbdsp_command()` busy-waits until the DSP command port is writable and sends one byte. `snd_sbdsp_get_byte()` busy-waits until data is available and reads one byte. Reset toggles the reset register and expects the 0xaa ready byte. Probe resets the DSP, sends `SB_DSP_GET_VERSION`, maps major/minor version to `SB_HW_10`, `SB_HW_20`, `SB_HW_201`, `SB_HW_PRO`, or `SB_HW_16` for auto hardware mode, and fills `chip->name` and `chip->version`.

`snd_sbdsp_create()` initializes all spinlocks, default resource fields, installs the IRQ handler, stores `card->sync_irq`, requests the base 16-byte port region unless ALS4000 skips allocation, requests DMA8 and DMA16 when available and valid, assigns card/hardware fields, and calls probe. Invalid 16-bit DMA on non-ALS100 cards is silently treated as no duplex by setting `dma16 = -1`.

## State and Persistence
State is the allocated `struct snd_sb`, devm-owned resources, IRQ/DMA numbers, detected hardware enum, DSP version, and name. No persistent storage is used.

## Dependencies and Integration Points
The file depends on Linux IO ports, IRQs, ISA DMA helpers, ALSA core, and `sound/sb.h`. It is the common constructor used by `sb8.c`, `sb16.c`, and clone drivers. It also exports mixer symbols from the same module boundary.

## Risks and Edge Cases
The command and read routines use long busy loops and return generic timeout failures, so dead hardware can stall CPU briefly. Detection relies on version bytes after reset and can misclassify clones unless a specific hardware enum was provided. ALS4000 skips IO/DMA allocation here, so its caller must have already handled resources. Shared IRQ flags are only used for ALS4000 and CS5530 hardware enums.

## Test Signals
Confirm reset returns 0xaa, version mapping produces expected hardware names, resource conflicts fail with `-EBUSY`, invalid DMA16 degrades to no duplex where intended, and exported helpers work for SB8/SB16 card constructors.
