<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/nommu_context.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/nommu_context.h

## Purpose
Provides no-op Xtensa MMU/KIO initialization for noMMU builds and includes generic noMMU context handling.

## Important APIs, Types, And Functions
Defines inline `init_mmu` and `init_kio`, then includes `<asm-generic/nommu_context.h>`.

## Control Flow
No-op initialization functions return immediately; generic noMMU context code handles the rest.

## State And Persistence
No MMU context state is owned by this header.

## Dependencies And Integration Points
Used when `CONFIG_MMU` is disabled via `mmu_context.h`.

## Risks And Edge Cases
NoMMU platforms still may need cache attribute setup elsewhere; these stubs only mean there is no full MMU context to initialize.

## Test Signals
Build and boot noMMU Xtensa, run FLAT binaries, and verify memory map/cacheattr setup occurs in the correct boot path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/nommu_context.h -->
