# sources/distributed-fs/ceph-client/arch/arm/mm/proc-sa1100.S

## Purpose
This file implements StrongARM SA-1100/SA-1110 low-level MMU/cache and suspend/resume support.

## Important APIs, Types, and Functions
It defines `cpu_sa1100_*` init/finish/reset/idle/dcache/switch-mm/set-PTE/suspend/resume hooks, `sa1100_crval`, and `sa1100_processor_functions`. The proc-info macro emits SA1100 (`0x4401a110`) and SA1110 (`0x6901b110`) records with shared function calls and ARMv4 hwcaps.

## Control Flow
Setup invalidates caches/TLBs and computes control bits. Idle drains the write buffer and performs an uncacheable load. `switch_mm()` updates the page-table base and invalidates TLB/cache state. Suspend/resume saves and restores PID/domain/control registers and resumes via `cpu_resume_mmu`.

## State and Persistence Behavior
It mutates CP15 control, cache, TLB, TTB, and PTE state, plus caller-provided suspend buffers. Static proc-info metadata identifies SA1100 and SA1110.

## Dependencies and Integration Points
It depends on StrongARM memory-management behavior, generic CPU suspend, ARMv4 page tables, abort handling, and cacheflush/DMA APIs.

## Risks
SA1100 and SA1110 share hooks but differ by CPU ID/name. Idle and suspend/resume are order-sensitive. Incorrect control masks can leave caches or MMU state inconsistent across reset or resume.

## Test Signals
Boot SA1100 and SA1110 boards, run suspend/resume and idle tests, stress fork/exec/mmap and DMA, and verify CPU identification. Include reset/kexec paths if available.
