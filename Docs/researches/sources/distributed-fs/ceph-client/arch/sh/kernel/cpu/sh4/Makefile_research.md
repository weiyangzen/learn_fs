# sources/distributed-fs/ceph-client/arch/sh/kernel/cpu/sh4/Makefile

## Purpose
The SH4 `Makefile` selects common SH4 objects, reused SH3 low-level entry code, optional FPU/store-queue/perf support, subtype setup, and the generic SH4 clock file when not building SH4A.

## Important APIs, Types, And Functions
It always builds `probe.o` and `common.o`; `common-y` pulls `../sh3/entry.o` and `../sh3/ex.o`. Optional selections include `../sh3/swsusp.o`, `fpu.o`, `softfloat.o`, `sq.o`, `perf_event.o`, `setup-sh7750.o`, `setup-sh7760.o`, and `clock-sh4.o`.

## Control Flow
Kbuild expands objects from Kconfig symbols. Perf events are only selected for SH7750, SH7750S, and SH7091. `clock-sh4.o` is skipped when `CONFIG_CPU_SH4A` is set because SH4A has subtype clock files.

## State And Persistence
No runtime state; it controls linked kernel contents.

## Dependencies And Integration Points
It integrates SH4 Kconfig with shared SH3 assembly, SH4 FPU emulation, store queue module, PMU support, and platform setup files.

## Risks
Because SH4 reuses SH3 entry/exception/hibernate assembly, build changes here can affect both families. Conditional perf selection means some CPUs with counters may still use separate SH4A perf code.

## Test Signals
Build matrix coverage across SH7750 variants, SH7760, FPU on/off, hibernation, store queues, and perf events is the main signal.
