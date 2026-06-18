# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/resctrl/Makefile

## Purpose

This Makefile selects the x86 resctrl architecture objects built for Resource Director Technology support. It wires core resource detection, control, monitoring, optional Intel Application Energy Telemetry, and optional pseudo-locking into the kernel build.

## Important APIs, Types, And Functions

Build targets are `core.o`, `rdtgroup.o`, `monitor.o`, `ctrlmondata.o`, optional `intel_aet.o`, and optional `pseudo_lock.o`. `CFLAGS_pseudo_lock.o = -I$(src)` is required so `define_trace.h` can recursively include `pseudo_lock_trace.h` from the source directory.

## Control Flow

There is no runtime control flow. Kconfig symbols `CONFIG_X86_CPU_RESCTRL`, `CONFIG_X86_CPU_RESCTRL_INTEL_AET`, and `CONFIG_RESCTRL_FS_PSEUDO_LOCK` choose which objects are compiled and linked.

## State, Dependencies, And Integration

This file affects build-time composition only. It integrates the architecture-specific files with generic resctrl filesystem code and tracepoint generation.

## Risks And Test Signals

Missing objects create unresolved symbols or silently remove features. Missing include flags break pseudo-lock tracepoint builds. Test with all three configurations: base resctrl, Intel AET enabled, and pseudo-lock enabled, including incremental builds that regenerate trace headers.
