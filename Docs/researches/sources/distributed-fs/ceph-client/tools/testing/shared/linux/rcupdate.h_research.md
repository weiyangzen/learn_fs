<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/rcupdate.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/rcupdate.h

## Purpose

`linux/rcupdate.h` maps kernel RCU pointer APIs onto Userspace RCU for shared tests.

## Important APIs, Types, and Functions

It includes `<urcu.h>` and defines `rcu_dereference_raw()`, `rcu_dereference_protected()`, `rcu_dereference_check()`, and `RCU_INIT_POINTER()`.

## Control Flow and State

Pointer dereference helpers collapse to Userspace RCU dereference or plain assignment. RCU callback scheduling is provided elsewhere by liburcu and wrappers such as `radix-tree.h`.

## Dependencies and Integration Points

It depends on liburcu development headers and is used by imported kernel data structures that rely on RCU pointer annotations.

## Risks and Test Signals

Risks include weaker checking than kernel RCU debug modes and simplified protected/check variants. Successful concurrent userspace data-structure tests are the practical signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/rcupdate.h -->
