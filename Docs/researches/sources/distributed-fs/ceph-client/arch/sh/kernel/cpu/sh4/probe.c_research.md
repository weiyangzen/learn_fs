# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/probe.c

## Purpose
`probe.c` identifies SH4 and SH4A CPU types, feature flags, cache geometry, and optional L2 cache properties.

## Important APIs, Types, And Functions
It exports `cpu_probe()`, reads `CCN_PVR`, `CCN_PRR`, and `CCN_CVR`, and populates `boot_cpu_data` fields including family, type, flags, cut version, icache/dcache/scache geometry, and special flags such as `CPU_HAS_PTEAEX`, `CPU_HAS_L2_CACHE`, `CPU_HAS_DSP`, and `CPU_HAS_PERF_COUNTER`.

## Control Flow
The function sets sane SH4 defaults, detects SH4A by PVR family, applies feature defaults, masks PVR to subtype ID, switches over PVR/PRR combinations, then refines cache geometry from CVR. Optional L2 is verified by CVR before scache fields are filled.

## State And Persistence
It mutates global boot CPU metadata used throughout architecture setup, cache maintenance, perf, FPU, and feature checks. There is no external persistence.

## Dependencies And Integration Points
It integrates with raw CCN register access, `asm/processor.h`, cache definitions, FPU/perf/store-queue users, and CPU subtype-specific setup.

## Risks
Misdetecting a CPU can select wrong cache maintenance, feature flags, or errata workarounds. The L2 size calculation comments note hardware/spec mismatch, so this path is hardware-sensitive.

## Test Signals
Boot CPU identification, `/proc/cpuinfo`, cache stress, FPU/perf availability, and L2 cache behavior on SH7785/SH7786/SH7723/SH7724 validate this file.
