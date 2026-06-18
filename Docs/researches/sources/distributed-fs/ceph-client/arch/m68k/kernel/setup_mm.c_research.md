# sources/distributed-fs/ceph-client/arch/m68k/kernel/setup_mm.c

## Purpose

`setup_mm.c` is the architecture setup implementation for MMU-capable m68k. It parses bootinfo, records CPU/FPU/MMU/memory metadata, configures the selected machine family, initializes memblock/paging, exposes `/proc/cpuinfo` and optional `/proc/hardware`, and provides NVRAM operation routing.

## Important APIs, Types, and Functions

Global exports include `m68k_machtype`, `m68k_cputype`, `m68k_mmutype`, `vme_brdtype`, `m68k_is040or060`, `m68k_num_memory`, `m68k_realnum_memory`, and `m68k_memory`. Hooks include `mach_sched_init`, `mach_init_IRQ`, `mach_get_model`, `mach_get_hardware_list`, `mach_reset`, `mach_halt`, `mach_heartbeat`, and `mach_l2_flush`. Major functions are `m68k_parse_bootinfo()`, `setup_arch()`, `show_cpuinfo()`, `proc_hardware_init()`, `arch_cpu_finalize_init()`, and the NVRAM accessors behind `arch_nvram_ops`.

## Control Flow

`setup_arch()` parses bootinfo from `_end` unless on ColdFire, sets the 040/060 marker, clears FPU state when available, applies a 68060 PCR erratum workaround, initializes `init_mm`, appends U-Boot command-line data, initializes jump labels and early params, dispatches to the platform `config_*()` routine based on `m68k_machtype`, reserves initrd memory, calls `paging_init()`, maps initrd virtual addresses, initializes natfeat, reserves Atari ST-RAM, initializes Sun3x DVMA, and sets ISA compatibility metadata for supported boards.

`m68k_parse_bootinfo()` walks big-endian bootinfo records, stores memory chunks, ramdisk metadata, command line, and RNG seed data, delegates unknown records to machine parsers, saves bootinfo for later inspection, and optionally collapses to a single memory chunk.

## State and Persistence Behavior

This file owns persistent boot metadata, memory chunk arrays, platform hook pointers, command line storage, optional initrd metadata, and NVRAM operations. RNG seed bootinfo is zeroed after `add_bootloader_randomness()` to preserve forward secrecy and prevent kexec reuse.

## Dependencies and Integration Points

It depends on `head.S` for early machine/CPU globals and `availmem`, platform `config_*()` and parse helpers, memblock/paging initialization, initrd, natfeat, Atari ST-RAM, Sun3x DVMA, `/proc` seq operations, and Mac/Atari NVRAM backends.

## Risks and Edge Cases

Malformed bootinfo sizes can mis-walk records. Too many memory chunks are truncated to `NUM_MEMINFO`, and `CONFIG_SINGLE_MEMORY_CHUNK` discards all but the first. Machine dispatch panics if `m68k_machtype` lacks a configured handler. FPU type is trusted from bootloader metadata with a FIXME noting possible confusion. NVRAM operations return board-specific errors when called on unsupported machines.

## Test Signals

Boot logs should show no unknown critical bootinfo, correct `/proc/cpuinfo`, correct memory totals, reserved initrd ranges, platform config hook execution, and valid `/proc/hardware` when enabled. Check RNG seed zeroing across kexec and NVRAM read/write behavior on Mac and Atari configs.
