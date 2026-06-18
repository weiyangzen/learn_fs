<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/lockdep.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/lockdep.h

## Purpose

`linux/lockdep.h` stubs lock dependency APIs for userspace tests.

## Important APIs, Types, and Functions

It includes `<linux/spinlock.h>`, defines `struct lock_class_key`, provides no-op `lockdep_set_class()`, and declares `lockdep_is_held()`.

## Control Flow and State

No lock class graph or dependency state is tracked. Callers can compile code that annotates locks without invoking kernel lockdep.

## Dependencies and Integration Points

It is used by shared data-structure code that includes lockdep annotations. The actual `lockdep_is_held()` definition must be supplied elsewhere if referenced.

## Risks and Test Signals

Risks include missing deadlock checking and unresolved references if imported code uses `lockdep_is_held()` without a stub. Successful linkage is the validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/lockdep.h -->
