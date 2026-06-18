# sources/distributed-fs/ceph-client/sound/ppc/awacs.h

## Purpose

This header describes the AWACS/Screamer MMIO register layout and bit fields used by PowerMac PCM, codec, interrupt, sample-rate, mixer, jack-detect, clipping, and DBDMA status code.

## Important APIs, types, and functions

`struct awacs_regs` defines the mapped control, codec control/status, clip count, and byteswap registers. Macros define control interrupt/rate/subframe bits, codec command format, codec register addresses, gain/mux/mute/volume/sample-rate fields, Screamer mic boost, codec status bits, jack sense masks, clip counters, and rate encodings.

## Control flow

No code executes here. The macros drive control flow in `pmac.c`, `awacs.c`, and codec-specific interrupt paths by naming bits that are tested, set, cleared, or cached.

## State and persistence behavior

The header defines hardware state layout rather than storing state. `awacs.c` persists codec values in `chip->awacs_reg[]`; `pmac.c` reads/writes `struct awacs_regs` through MMIO.

## Dependencies and integration points

It is included by `pmac.h`, which makes these definitions available to most PowerMac sound files. The definitions align with Open Firmware resources mapped in `pmac.c`.

## Risks and test signals

Risks are incorrect bit masks or ambiguous reused encodings such as 48/44.1 kHz sharing a rate code. Test by compiling all users and exercising control interrupts, byteswap, jack detection, and all supported sample-rate indexes on real hardware or emulation with register tracing.
