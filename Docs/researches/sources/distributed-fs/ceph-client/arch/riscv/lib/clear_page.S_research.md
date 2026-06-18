<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/clear_page.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/clear_page.S

## Purpose
`clear_page.S` provides an optimized RISC-V `clear_page()` implementation using Zicboz cache-block zero when available, with a memset fallback.

## Important APIs, Types, And Functions
`clear_page` is the exported symbol. `CBOZ_ALT` wraps alternative patching for block-size-specific loop exits. The code reads `riscv_cboz_block_size` and emits repeated `CBO_ZERO` operations.

## Control Flow
The function starts with PAGE_SIZE bytes. If Zicboz is absent or the block size is too large, it tails to `__memset(page, 0, PAGE_SIZE)`. Otherwise it loops over cache blocks, using alternatives for block-size orders 8 through 12 to minimize loop overhead.

## State And Persistence
It writes zeros to one physical page through the provided virtual address. No persistent state is held.

## Dependencies And Integration Points
It depends on alternative patching, RISC-V hwcap detection, CBO instruction definitions, `riscv_cboz_block_size`, and the generic page allocator/users that call `clear_page()`.

## Risks
Wrong block-size assumptions can overrun or under-clear pages. Alternative order encoding must match discovered CBOZ size. Fallback must be available before and after boot alternatives.

## Test Signals
Boot on Zicboz and non-Zicboz systems, page allocator poisoning/zero-page tests, and memory selftests checking newly allocated zero pages are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/clear_page.S -->
