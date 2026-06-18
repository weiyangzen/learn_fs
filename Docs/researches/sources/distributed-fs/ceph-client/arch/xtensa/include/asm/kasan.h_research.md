<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/kasan.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/kasan.h

## Purpose
Defines Xtensa KASAN shadow-memory layout and initialization hooks.

## Important APIs, Types, And Functions
For `CONFIG_KASAN`, defines `KASAN_START_VADDR`, `KASAN_SHADOW_START`, `KASAN_SHADOW_SIZE`, `KASAN_SHADOW_END`, `KASAN_SHADOW_OFFSET`, and declares `kasan_early_init` and `kasan_init`; otherwise provides no-op stubs.

## Control Flow
No runtime flow in the header. Early architecture setup calls the declared init functions when KASAN is enabled.

## State And Persistence
KASAN shadow mappings and memory persist during runtime when enabled.

## Dependencies And Integration Points
Depends on MMU, non-XIP KASAN support selected in Kconfig, page-table layout, and generic KASAN.

## Risks And Edge Cases
Shadow offset and range must not collide with kernel virtual layout. XIP is excluded because writable shadow/text assumptions differ.

## Test Signals
Boot KASAN-enabled Xtensa, trigger slab/page out-of-bounds tests, and inspect shadow mapping setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/kasan.h -->
