<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/empty.c -->
# sources/distributed-fs/ceph-client/scripts/mod/empty.c

## Purpose

`empty.c` is an intentionally empty translation unit used to produce `empty.o` for target ELF probing.

## Important APIs, Types, and Functions

It defines no functions or data.

## Control Flow

Kbuild compiles it, then `mk_elfconfig` reads the resulting object to infer target ELF class and endianness.

## State and Persistence Behavior

The only persisted artifact is `empty.o` in the object tree.

## Dependencies and Integration Points

It integrates with `scripts/mod/Makefile` and `mk_elfconfig.c`. LTO flags are removed for this object to keep the probe object simple.

## Risks and Edge Cases

If the compiler emits unusual or non-ELF output due to flags, `mk_elfconfig` may fail. The file itself has no logic risk.

## Test Signals

Build `empty.o` for each target class/endian combination and verify `elfconfig.h` reports the expected `KERNEL_ELFCLASS` and `KERNEL_ELFDATA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/mod/empty.c -->
