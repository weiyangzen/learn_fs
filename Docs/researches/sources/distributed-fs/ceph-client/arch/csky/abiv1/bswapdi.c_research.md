# sources/distributed-fs/ceph-client/arch/csky/abiv1/bswapdi.c

## Purpose

provides the C-SKY ABI v1 libgcc-style 64-bit byte-swap helper expected by compiler-generated code

## Important APIs, Types, and Functions

Source read size: 12 lines, 302 bytes. Includes: `linux/export.h`, `linux/compiler.h`,
`uapi/linux/swab.h`. Functions: `__bswapdi2`. Exported symbols: `__bswapdi2`.

## Control Flow and Behavior

the helper reverses byte order for integer values and supplies a symbol that may be emitted by the
compiler or linked by kernel code

## State and Persistence

there is no persistent state

## Dependencies and Integration Points

integrates with compiler runtime expectations and any generic code using byte-swap operations on ABI
v1

## Risks and Test Signals

wrong symbol semantics corrupt endian conversions; build/link tests and byte-order selftests cover
it
