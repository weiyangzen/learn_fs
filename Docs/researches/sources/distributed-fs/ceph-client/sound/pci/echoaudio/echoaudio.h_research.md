# sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio.h

## Purpose

This header is the shared Echoaudio driver contract. It documents the pipe/bus model, defines common constants, state structures, helper declarations, and inline channel-layout accessors used by all Echoaudio card wrappers.

## Important APIs, types, and functions

It defines PCI IDs, subsystem IDs, max channel/pipe/MIDI sizes, clock constants and bitmasks, digital mode constants/capability masks, gain limits, pipe states, `struct audiopipe`, `struct audioformat`, and the large `struct echoaudio`. It declares shared DSP helper entry points and optional MIDI hooks. Inline helpers wrap DSP register reads/writes, handshake clearing, pipe/bus index macros, channel counts, and monitor matrix indexing.

## Control flow

Each card wrapper defines `PX_*`, `BX_*`, and feature macros before including this header. Shared code then uses the inline helpers to compute PCM counts, control counts, and bus/pipe offsets without knowing whether values are constants or dynamic 3G fields.

## State and persistence behavior

`struct echoaudio` is the persistent per-card state for the whole shared driver: synchronization, ALSA objects, PCI/MMIO/IRQ resources, comm page, pipe masks, sample rate, digital/clock settings, firmware/ASIC state, gains, monitor/vmixer matrices, nominal levels, firmware cache, MIDI state, and Echo3G dynamic channel layout.

## Dependencies and integration points

It depends on `echoaudio_dsp.h`, ALSA core/PCM/DMA types through included sources, and card-defined macros. It is included by every Echoaudio card module and by shared implementation files.

## Risks and test signals

Risks include macro-order dependency, dynamic-vs-static pipe index confusion, oversized shared state changes affecting all card modules, and comment/API drift from the DSP helpers. Test signals include building multiple card wrappers, verifying channel counts for Darla20/Darla24/Echo3G, and exercising controls that index gain matrices.
