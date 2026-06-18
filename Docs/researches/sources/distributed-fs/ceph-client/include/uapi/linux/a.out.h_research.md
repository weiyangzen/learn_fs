<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/a.out.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/a.out.h

## Purpose
Defines legacy GNU/Linux a.out executable, object, symbol, and relocation ABI helpers. It preserves constants and layout macros for old loaders, tools, and compatibility consumers.

## Important APIs, Types, And Functions
Exports machine type constants, magic values `OMAGIC`, `NMAGIC`, `ZMAGIC`, `QMAGIC`, `CMAGIC`, macros for `N_MAGIC`, machine type, flags, section offsets, text/data/bss addresses, symbol table constants, `struct nlist`, and `struct relocation_info`.

## Control Flow
Consumers inspect `struct exec.a_info`, validate magic with `N_BADMAG`, calculate file offsets for text/data/relocation/symbol/string sections, then load or link according to magic-specific alignment rules.

## State And Persistence
The persistent state is the on-disk a.out file format: header fields, symbol table records, relocation records, and string tables. Runtime state is derived by loaders/linkers.

## Dependencies And Integration Points
Includes architecture-specific `<asm/a.out.h>` unless overridden and uses page/segment sizing from architecture or libc. Integrates with obsolete binary loaders, binutils-like tools, and core-file/symbol consumers.

## Risks And Edge Cases
Architecture overrides, page-size assumptions, old Sun/m68k/SPARC machine constants, bitfield layout in relocations, and `SEGMENT_SIZE` depending on userspace `getpagesize()` are compatibility hazards. This format should not be extended casually.

## Test Signals
Layout tests for `struct nlist` and relocation records, offset macro tests for each magic value, cross-architecture compile checks, and loader tests against known a.out fixtures are the best signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/a.out.h -->
