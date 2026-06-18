# sources/distributed-fs/ceph-client/arch/arm/mm/tlb-v4.S

## Purpose
Provides ARMv4 write-through/no-write-buffer range TLB invalidation for processors such as ARM720T with split I/D TLBs and no write buffer.

## Important APIs, Types, And Functions
Exports `v4_flush_user_tlb_range` and `v4_flush_kern_tlb_range`. The kernel function is either a CFI-safe branch wrapper or a global equate to the shared internal label.

## Control Flow
User flush compares the target VMA mm to `current->active_mm`; inactive address spaces are skipped. The shared range loop aligns the start address and invalidates TLB entries page by page through CP15 c8 unified-entry invalidation, then returns. No explicit write-buffer drain is needed for this CPU class.

## State, Dependencies, And Integration
State is split TLB contents. Dependencies include `asm/tlbflush.h`, `proc-macros.S`, and CFI macros. Integration occurs through `v4_tlb_fns` in `tlb.c`, which pairs these callbacks with `v4_tlb_flags`.

## Risks And Test Signals
Risks include CFI symbol exposure issues, assuming unified invalidation behavior on unsupported hardware, and missing flushes for inactive but soon-to-run address spaces if context switch behavior changes. Test signals are ARM720T builds, CFI builds, and VM range invalidation stress.
