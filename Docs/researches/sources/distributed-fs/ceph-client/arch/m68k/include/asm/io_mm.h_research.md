<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/io_mm.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/io_mm.h

## Purpose
`io_mm.h` implements m68k MMU-enabled I/O accessors, especially ISA-style port and memory access for Q40, Amiga PCMCIA, and Atari ROM ISA bridges.

## Important APIs, Types, and Functions
The header defines bridge address translations such as `Q40_ISA_IO_B`, `AG_ISA_IO_B`, and `ENEC_ISA_IO_B`, runtime or compile-time `ISA_TYPE`/`ISA_SEX`, inline translators `isa_itb()`, `isa_itw()`, `isa_mtb()`, and access macros `isa_inb/outb`, `isa_readb/writeb`, string I/O, ROM-ISA variants, delay variants, relaxed accessors, and `IO_SPACE_LIMIT`.

## Control Flow, State, and Persistence
Accessors are inline and branch on `ISA_TYPE` only when multiple ISA bridges are compiled. No persistent state is kept here, but multi-ISA builds depend on external globals `isa_type` and `isa_sex`.

## Dependencies and Integration Points
It depends on `raw_io.h`, `virtconvert.h`, `kmap.h`, and platform headers such as `amigayle.h`. Drivers that use legacy PC `inX/outX` macros on m68k route through this file.

## Risks
Endian selection through `ISA_SEX` is subtle. Atari ROM ISA splits port ranges below 1024 from regular accesses, so callers using unusual ports can hit the wrong path. The file cautions that non-ISA drivers should not use `inX/outX`.

## Test Signals
Build Q40, Amiga PCMCIA, Atari ROM ISA, and multi-ISA configs. Runtime signals are correct register reads/writes, string I/O transfers, and byte order on 16/32-bit port accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/io_mm.h -->
