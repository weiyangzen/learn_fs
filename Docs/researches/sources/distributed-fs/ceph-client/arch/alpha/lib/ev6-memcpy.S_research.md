# sources/distributed-fs/ceph-client/arch/alpha/lib/ev6-memcpy.S

## Purpose
EV6/21264 optimized `memcpy` implementation with aligned and misaligned copy paths. The source was read as part of `subset-b-000628` and contains 250 lines.

## Important APIs, Types, and Functions
Exports `memcpy` and provides global `__memcpy = memcpy` for compatibility.

## Control Flow
For aligned copies it moves to 64-byte alignment, uses unrolled loops and `wh64` write hints, then handles quadword and byte tails. For misaligned copies it byte-aligns the destination, uses rotating unaligned loads/extracts to assemble aligned stores, and finishes trailing bytes.

## State and Persistence Behavior
Mutates destination memory and reads source memory; returns the destination pointer in the normal C ABI.

## Dependencies
Selected by EV6 Makefile prefix, depends on Alpha 21264 scheduling/write-hint behavior, and is used by broad kernel C code and modules.

## Integration Points
This file integrates with the Alpha architecture build and boot path under `arch/alpha`. Platform files are selected through `struct alpha_machine_vector`; syscall/linker files are consumed by Kbuild, low-level entry assembly, and the final kernel image; library files provide symbols used by the MM, networking, string, usercopy, module, and firmware-console subsystems.

## Risks
`memcpy` assumes non-overlap; using it for overlapping ranges is a caller bug. Alignment paths are complex and can corrupt tails. `wh64` hints must not target invalid cache lines.

## Test Signals
Run memory copy selftests over all alignments and sizes, compare with generic implementation, check `__memcpy` alias for module compatibility, and stress boot/filesystem/network paths on EV6.
