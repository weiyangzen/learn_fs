# sources/distributed-fs/ceph-client/lib/raid/xor/sparc/xor-sparc32.c

Purpose: provides SPARC 32-bit optimized XOR using doubleword load/store instructions.

Important APIs and flow: `sparc_{2,3,4,5}` loop over eight `long` words, load destination/source blocks with `ldd`, apply register XOR chains, store with `std`, and advance pointers. `DO_XOR_BLOCKS(sparc32, ...)` emits `xor_gen_sparc32()`, exported through `xor_block_SPARC`.

State and persistence: no persistent state; destination buffers are mutated.

Dependencies and integration: registered by `sparc/xor_arch.h` on non-sparc64 builds alongside generic templates.

Risks and test signals: inline assembly clobber lists and alignment are the main risks. Signals include sparc32 build tests, boot calibration, and KUnit XOR correctness.
