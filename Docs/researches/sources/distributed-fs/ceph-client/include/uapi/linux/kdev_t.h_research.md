# sources/distributed-fs/ceph-client/include/uapi/linux/kdev_t.h

## Purpose
`kdev_t.h` provides old userspace macros for encoding and decoding device numbers when not compiling inside the kernel.

## Important APIs, Types, and Functions
`MAJOR(dev)` extracts the high 8 bits, `MINOR(dev)` extracts the low 8 bits, and `MKDEV(ma, mi)` composes the old 8:8 device number format. The macros are hidden under `#ifndef __KERNEL__`.

## Control Flow
There is no runtime flow. Userspace source code may use these macros to interpret legacy device IDs.

## State and Persistence
Device numbers appear in filesystem metadata and stat results, but this header stores no state.

## Dependencies and Integration Points
It has no external include dependency. It integrates with legacy userspace code that expects Linux device-number helpers.

## Risks and Test Signals
Tests should ensure the header compiles in userspace and that legacy 8:8 encoding is not confused with modern wider `dev_t` encoding. Risk is mainly misuse in code that should rely on libc `major()`, `minor()`, and `makedev()`.
