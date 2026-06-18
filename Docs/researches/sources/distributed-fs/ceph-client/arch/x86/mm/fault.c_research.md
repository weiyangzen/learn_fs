# sources/distributed-fs/ceph-client/arch/x86/mm/fault.c

## Purpose
Implements the x86 page-fault handler, from low-level IDT entry through kernel/user address classification, recoverable kernel faults, VMA lookup, `handle_mm_fault()`, signal delivery, and fatal oops reporting.

## Important APIs, Types, And Functions
The IDT entry is `exc_page_fault()`. Core helpers include `handle_page_fault()`, `do_kern_addr_fault()`, `do_user_addr_fault()`, `kernelmode_fixup_or_oops()`, `bad_area_nosemaphore()`, `bad_area_access_error()`, `do_sigbus()`, `spurious_kernel_fault()`, `fault_in_kernel_space()`, `show_fault_oops()`, and 32-bit vmalloc synchronization helpers. Global `show_unhandled_signals` controls fatal segfault logging.

## Control Flow
The entry obtains CR2 or FRED event data, lets KVM async page faults consume synthetic events, enters irq context, traces the fault, checks mmiotrace, and dispatches by address space. Kernel faults attempt 32-bit vmalloc sync, CPU errata workarounds, spurious TLB-fault handling, kprobe handling, exception-table fixup, prefetch erratum handling, then oops. User faults reject reserved-bit faults, SMAP violations, disabled fault handlers, and missing `mm`; otherwise they enable IRQs, set fault flags, emulate vsyscall faults, try RCU VMA locking, fall back to mmap locking, call `handle_mm_fault()`, retry when needed, and translate failures to OOM, SIGBUS, SIGSEGV, or kernel fixups.

## State And Persistence
Updates task thread fault metadata (`trap_nr`, `error_code`, `cr2`), emits perf software fault events and tracepoints, may acquire/release VMA or mmap locks, may alter `pt_regs` through fixups, and can terminate tasks or oops the kernel. 32-bit code synchronizes process page tables with init mappings.

## Dependencies And Integration Points
Integrates with core MM fault handling, VMA locking, pkeys, shadow stacks, SMAP/SMEP/NX, KASAN/KFENCE, KVM async PF, mmiotrace, kprobes, VDSO/vsyscall emulation, exception tables, EFI crash handling, SNP RMP diagnostics, and architecture entry code.

## Risks
This is security and stability critical. User/kernel access classification, sanitized error codes, SMAP and pkey enforcement, shadow-stack rules, and vsyscall emulation must be exact. Locking paths must avoid sleeping in disabled-fault or interrupt contexts. Spurious-fault acceptance must not mask real permission bugs. Signal and oops paths must preserve useful diagnostics without leaking layout to userspace.

## Test Signals
Page-fault selftests for demand faults, COW, protection faults, pkeys, shadow stacks, vsyscall, SMAP, NX/SMEP, user versus kernel faults, disabled pagefaults, exception-table recovery, OOM/SIGBUS/HWPOISON paths, KVM async PF, 32-bit vmalloc races, and boot-time/kprobe/mmiotrace interactions.
