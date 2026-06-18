# sources/distributed-fs/ceph-client/tools/include/nolibc/elf.h

## Purpose
Exposes Linux UAPI ELF constants and structs through the nolibc include tree.

## APIs, Types, and Functions
It has no local functions or types beyond the include guard; it includes `<linux/elf.h>`.

## Control Flow, State, and Persistence
There is no control flow or state. It is a compatibility facade so nolibc consumers can include an ELF header path without depending on system libc headers.

## Dependencies and Integration
Depends on the kernel UAPI `linux/elf.h`. Integration points include startup/auxv parsing, binary inspection tools, and code that uses ELF constants while building against nolibc.

## Risks and Test Signals
Risks are UAPI availability differences and callers assuming full glibc `<elf.h>` coverage. Test signals are compiling ELF consumers under nolibc and comparing required constants against the kernel UAPI header.
