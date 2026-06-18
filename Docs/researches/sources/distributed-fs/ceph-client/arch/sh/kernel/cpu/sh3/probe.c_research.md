# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh3/probe.c

## Purpose
`probe.c` identifies SH3 CPU subtypes and initializes `boot_cpu_data` cache geometry and feature flags.

## Important APIs, Types, And Functions
The file exports `cpu_probe()`. It reads CPU version registers, assigns `boot_cpu_data.type`, family, cache way/sets/line details, and flags such as MMU/FPU/DSP support according to detected subtype.

## Control Flow
During architecture CPU setup, `cpu_probe()` reads processor identification state, applies common SH3 defaults, switches on version/revision encodings, and updates per-CPU cache descriptors.

## State And Persistence
It mutates global boot CPU metadata used for cache management, feature checks, proc/cpuinfo, and architecture setup. No external persistence exists.

## Dependencies And Integration Points
It integrates with `asm/processor.h`, `asm/cache.h`, and the broader SH CPU initialization path. Cache and MMU code consume the populated fields.

## Risks
Misidentification causes wrong cache maintenance parameters and feature flags. Because many subtype IDs are old and close together, revision-specific handling is easy to regress.

## Test Signals
Boot CPU identification messages, correct `/proc/cpuinfo`, cache alias behavior, and successful boot on each SH3 subtype are the main validation points.
