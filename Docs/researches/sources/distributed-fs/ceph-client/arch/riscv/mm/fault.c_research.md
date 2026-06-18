<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/fault.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/fault.c

## Purpose
`fault.c` is the RISC-V page fault handler. It diagnoses kernel faults, handles vmalloc synchronization on limited configurations, invokes generic MM fault handling, and delivers signals or oopses.

## Important APIs, Types, And Functions
Key helpers are `show_pte()`, `die_kernel_fault()`, `no_context()`, `mm_fault_error()`, `bad_area_nosemaphore()`, `bad_area()`, `vmalloc_fault()`, `access_error()`, and exported `handle_page_fault()`.

## Control Flow
The handler records cause/address, lets kprobes consume faults, traces user/kernel faults, handles vmalloc faults without locks in applicable builds, enables interrupts when safe, rejects faults in atomic/no-mm contexts, checks kernel access to user memory without SUM, sets fault flags, tries lockless VMA handling for user faults, falls back to mmap locking, calls `handle_mm_fault()`, retries as requested, and maps final errors to SIGSEGV/SIGBUS/OOM or kernel oops.

## State And Persistence
It mutates task bad-cause state, page tables through generic fault handling, and may synchronize vmalloc top-level mappings. No disk persistence exists.

## Dependencies And Integration Points
It depends on Linux MM fault core, kprobes, kfence, perf software events, exception fixups, RISC-V trap fields, TLB flushes, and signal/trap delivery.

## Risks
Kernel faults in atomic context must never take mmap locks. SUM checks prevent unsafe direct user access. VMA lock retry logic must release locks correctly. Vmalloc fault synchronization assumes global kernel mappings and explicit TLB flushes.

## Test Signals
Page fault selftests, user SIGSEGV/SIGBUS cases, COW/mmap stress, kprobes, KFENCE, invalid kernel access tests, and vmalloc fault tests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/fault.c -->
