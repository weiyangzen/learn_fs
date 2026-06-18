# sources/distributed-fs/ceph-client/tools/arch/x86/include/uapi/asm/mman.h

## Purpose
Adds the x86-specific `MAP_32BIT` memory mapping flag before including generic UAPI mmap constants.

## APIs, Types, and Functions
Defines `MAP_32BIT` as `0x40` and includes `<uapi/asm-generic/mman.h>`.

## Control Flow, State, and Persistence
No runtime behavior. It is a UAPI constant shim.

## Dependencies and Integration
Used by tool builds that include x86 UAPI mmap flags. It integrates generic Linux mmap/mprotect/madvise definitions with the x86-only low-address mapping hint.

## Risks and Test Signals
Risks are duplicate or mismatched `MAP_32BIT` definitions and include-order problems. Test signals are compile checks for perf and other tools using mmap flags and comparison with exported kernel x86 UAPI headers.
