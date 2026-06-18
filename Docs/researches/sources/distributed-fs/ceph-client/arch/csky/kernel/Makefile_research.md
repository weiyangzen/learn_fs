# sources/distributed-fs/ceph-client/arch/csky/kernel/Makefile

## Purpose

builds objects or generated artifacts for `sources/distributed-fs/ceph-client/arch/csky/kernel`

## Important APIs, Types, and Functions

Source read size: 20 lines, 696 bytes. Build selections: `obj-y -> head.o entry.o atomic.o signal.o
traps.o irq.o time.o vdso.o vdso/`, `obj-y -> power.o syscall.o syscall_table.o setup.o`, `obj-y ->
process.o cpu-probe.o ptrace.o stacktrace.o`, `obj-y -> probes/`.

## Control Flow and Behavior

Kbuild variables select object files, subdirectories, generated headers, or boot targets

## State and Persistence

state is build output only

## Dependencies and Integration Points

integrates with parent Kbuild recursion and configuration symbols

## Risks and Test Signals

wrong dependencies or object lists cause missing code or stale generated artifacts; clean builds are
the signal
