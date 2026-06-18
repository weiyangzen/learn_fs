<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/spinlock.h

## Purpose
`spinlock.h` selects queued spinlock and queued rwlock implementations for UML/x86.

## Important APIs, types, and functions
It includes `asm/qspinlock.h` and `asm/qrwlock.h`.

## Control flow
Lock users receive the generic queued lock APIs through these includes.

## State and persistence behavior
No state is local; lock state lives in lock objects.

## Dependencies and integration points
It depends on Kconfig selections in `um/Kconfig`.

## Risks and edge cases
Incorrect lock implementation selection affects SMP UML synchronization.

## Test signals
Signals are lockdep, SMP boot, and concurrency tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/spinlock.h -->
