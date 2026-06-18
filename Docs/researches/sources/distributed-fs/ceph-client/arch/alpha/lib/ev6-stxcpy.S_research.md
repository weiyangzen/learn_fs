# sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-stxcpy.S

## Purpose
EV6-optimized internal null-terminated string copy primitive used by string functions such as strcpy, stpcpy, and strcat. The source was read as part of `subset-b-000628` and contains 322 lines.

## Important APIs, Types, and Functions
Defines global `__stxcpy` plus internal aligned/unaligned procedure bodies. It follows special linkage: `t9` is return address, `a0` destination, `a1` source, and on return `t12` marks the last byte written while `a0` points at the last word written.

## Control Flow
The routine first checks source/destination co-alignment. The aligned path masks the first destination word if needed, copies full source words while `cmpbge` detects a zero byte, then writes the final partial word without unnecessary destination loads. The unaligned path assembles shifted source words from paired unaligned loads, avoids reading too far past the terminating byte, and handles final partial stores.

## State and Persistence Behavior
Writes the destination string including the terminating NUL and returns internal linkage state to the public wrapper. It has no global state.

## Dependencies
Depends on Alpha string wrapper conventions in adjacent `stxcpy`/`strcpy`/`strcat` code, EV6 scheduling, Alpha byte-compare and zap instructions, and kernel string ABI.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
This is an internal ABI, so public wrappers depend on preserved registers and return values. It must avoid source over-read across invalid pages. Final partial store masks must preserve destination bytes after the NUL when not overwritten.

## Test Signals
Run string-copy tests for all source/destination alignments, page-boundary strings, empty and long strings, and wrappers using `__stxcpy`; compare final pointers and destination contents with generic string helpers.
