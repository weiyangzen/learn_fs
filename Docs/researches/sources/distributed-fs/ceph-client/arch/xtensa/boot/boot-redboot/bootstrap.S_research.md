<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-redboot/bootstrap.S -->
# sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-redboot/bootstrap.S

## Purpose
RedBoot compressed-image loader for Xtensa. It relocates itself, clears BSS, allocates stack/heap, decompresses the embedded gzip kernel into its destination, flushes/invalidate caches, and jumps to the uncompressed kernel.

## Important APIs, Types, And Functions
Important labels and symbols are `__start`, `__start_a0`, `_start`, `_reloc`, `avail_ram`, `end_avail`, `_stack`, `_heap`, and `complen`. It calls external `gunzip` when available and uses cache macros from `cacheasm.h`.

## Control Flow
Entry resets PS/window state, computes the runtime load address, copies the loader to its linked address, flushes writeback dcache and invalidates icache, jumps to `_reloc`, clears BSS, aligns stack, computes the compressed image source from the embedded `image` section, initializes gzip length, and calls `gunzip`. If `gunzip` is not linked it falls back to raw copy. It then flushes/invalidate caches again, restores the boot argument register in call0 ABI, and jumps to `_image_start`.

## State And Persistence
State is loader BSS, stack, heap allocator bounds for zlib, compressed length, and CPU cache state. No durable persistence.

## Dependencies And Integration Points
Depends on Xtensa ABI macros, RedBoot load convention, boot linker script symbols, zlib boot library, cache operation macros, and kernel entry conventions.

## Risks And Edge Cases
Self-relocation assumes limited overlap and that the kernel image is out of the way. Heap size must fit zlib workspace. Cache flush/invalidate is mandatory before executing relocated/decompressed code. ABI register preservation differs between windowed and call0.

## Test Signals
Boot compressed images with windowed and call0 ABI, verify decompression length, run on writeback and non-writeback cache variants, and test failure handling for oversized images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/boot/boot-redboot/bootstrap.S -->
