# sources/distributed-fs/ceph-client/mm/kmsan/kmsan.h

## Purpose
`kmsan.h` is the private runtime header shared by the KMSAN implementation files. It defines metadata constants, origin encoding helpers, bug-reason types, runtime recursion guards, and internal function prototypes.

## Important APIs, Types, And Functions
`struct shadow_origin_ptr` returns paired shadow and origin metadata pointers to instrumentation. Constants include origin magic values, poison flags, origin slot size, maximum origin-chain depth, stack depth, and metadata-kind booleans. `enum kmsan_bug_reason` distinguishes generic uninitialized uses, copy-to-user leaks, and USB submission leaks. Inline helpers `kmsan_get_context()`, `kmsan_in_runtime()`, `kmsan_enter_runtime()`, and `kmsan_leave_runtime()` manage the current runtime context. `kmsan_extra_bits()`, `kmsan_uaf_from_eb()`, and `kmsan_depth_from_eb()` encode stack-depot extra bits. The header declares internal poisoning, checking, metadata, reporting, page, vmalloc, and task functions.

## Control Flow
Runtime code calls `kmsan_enter_runtime()` before operations that may call instrumented code or allocate, then `kmsan_leave_runtime()` afterward. `kmsan_in_runtime()` suppresses recursive KMSAN work and conservatively bails out in nested hard IRQ or NMI contexts. Origin extra-bit helpers are used when saving or interpreting stack-depot handles.

## State And Persistence
The header itself stores no state, but its inline functions access `current->kmsan_ctx` or the per-CPU `kmsan_percpu_ctx`. It defines the encoding that persists in stack-depot handles for UAF status and origin-chain depth.

## Dependencies And Integration Points
It includes scheduler, IRQ, NMI, printk, stackdepot, stacktrace, mm, pgtable, and public `linux/kmsan.h` definitions. It hides implementation details from public KMSAN users while providing shared contracts among `core.c`, `hooks.c`, `instrumentation.c`, `report.c`, `shadow.c`, and `init.c`.

## Risks
The recursion guard is central to avoiding deadlocks and false recursion; incorrect depth accounting triggers `KMSAN_WARN_ON`. The hard IRQ/NMI shortcut can reduce coverage but protects against unsafe locking/allocation. Extra-bit packing must remain compatible with `STACK_DEPOT_EXTRA_BITS` and `KMSAN_MAX_ORIGIN_DEPTH`.

## Test Signals
Compile-time users across all KMSAN runtime files validate declarations. Runtime test signals include lack of recursive reports, correct UAF vs uninitialized bug-type selection, and origin-chain depth handling in KUnit tests.
