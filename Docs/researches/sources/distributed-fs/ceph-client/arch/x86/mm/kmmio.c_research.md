# sources/distributed-fs/ceph-client/arch/x86/mm/kmmio.c

## Purpose
This file implements low-level MMIO probing for mmiotrace. It marks MMIO mapping pages non-present, handles the resulting page faults, single-steps the faulting instruction, and calls registered pre/post probe handlers.

## Important APIs, Types, and Functions
- `register_kmmio_probe()` and `unregister_kmmio_probe()` add/remove `struct kmmio_probe` ranges and arm/disarm affected pages.
- `kmmio_handler()` handles page faults from armed MMIO pages and sets trap flag state for single stepping.
- `post_kmmio_handler()` completes the single-step debug trap and rearms pages.
- `kmmio_init()` and `kmmio_cleanup()` register/unregister the die notifier.
- `struct kmmio_fault_page` tracks an armed page, saved presence bits, refcount, and delayed release state; `struct kmmio_context` is per-CPU in-flight state.

## Control Flow and State
Probe registration inserts the probe in an RCU-protected global list and arms each page by clearing PTE/PMD presence while saving the old entry. On page fault, the handler looks up the fault page and probe under scheduler RCU, records per-CPU context, invokes the pre-handler, enables TF, disables IF, restores page presence, and returns handled. The debug-trap notifier calls the post-handler, rearms the page if still referenced, restores flags, and releases RCU. Unregistration decrements page refcounts, disarms zero-count pages, removes probes, and uses a two-stage RCU delayed release before freeing fault-page records.

## Dependencies and Integration Points
The code integrates with x86 page-fault handling, debug trap die notifications, `lookup_address()`, TLB flush helpers, debug registers, RCU, local interrupt control, and `linux/mmiotrace.h`. `mmio-mod.c` registers the actual mmiotrace probes and supplies pre/post callbacks.

## Risks
This code runs in fault/debug trap context with interrupts disabled and cannot sleep. Recursive faults, multiple CPUs accessing the same page during single-step, or premature RCU freeing can lose events or crash. Large PMD mappings are handled, but unexpected page levels are rejected. Locking uses an arch spinlock hidden from lockdep because it is used in NMI-like contexts.

## Test Signals
Expected signals include successful mmiotrace enable/disable, probe callbacks around MMIO instructions, no leaked fault pages at cleanup, warnings on recursive probes or unexpected debug traps, and stable behavior under concurrent CPU access. Testing usually pairs this with `testmmiotrace` or mmiotrace debugfs workflows.
