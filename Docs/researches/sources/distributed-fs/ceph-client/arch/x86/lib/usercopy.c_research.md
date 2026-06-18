# sources/distributed-fs/ceph-client/arch/x86/lib/usercopy.c

## Purpose
This file implements `copy_from_user_nmi()`, an x86 user-copy helper that is safe in NMI context by disabling page faults and aborting on fault instead of sleeping or faulting in pages.

## Important APIs, Types, and Functions
The exported GPL API is `copy_from_user_nmi(void *to, const void __user *from, unsigned long n)`. It uses `__access_ok()`, `nmi_uaccess_okay()`, `pagefault_disable()`, `raw_copy_from_user()`, `pagefault_enable()`, and instrumentation hooks `instrument_copy_from_user_before()`/`after()`.

## Control Flow
The function first rejects out-of-range user pointers and architectures/states where NMI uaccess is not allowed. It disables page faults, emits copy instrumentation, performs the raw copy, emits completion instrumentation with the uncopied byte count, re-enables page faults, and returns the number of bytes not copied.

## State and Persistence
There is no persistent state. The function temporarily changes the current execution context's pagefault-disabled state and reads user memory into a kernel buffer.

## Dependencies and Integration Points
It integrates with x86 NMI fault handling, CR2 preservation rules, uaccess helpers, fault disabling, KASAN/KCSAN/usercopy instrumentation, and callers such as profiling, tracing, or diagnostics that may need best-effort user reads in NMI/IRQ-like contexts.

## Risks and Test Signals
Risks include using it when faults must be resolved, missing access checks, instrumentation mismatches, and architecture changes that make NMI uaccess unsafe. Test signals include invalid pointer returns, pagefault-disabled behavior, NMI/profiling stack sampling, and instrumentation/usercopy sanitizer coverage.
