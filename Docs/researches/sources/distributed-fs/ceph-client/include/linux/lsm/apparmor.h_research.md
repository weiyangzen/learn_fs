<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm/apparmor.h -->
# sources/distributed-fs/ceph-client/include/linux/lsm/apparmor.h

## Purpose
This header defines the AppArmor-specific portion of the generic `struct lsm_prop` property model.

## Important APIs, Types, and Functions
It forward-declares `struct aa_label` and defines `struct lsm_prop_apparmor` with an AppArmor label pointer.

## Control Flow
There is no control flow. LSM property producers fill this field and consumers inspect it through generic LSM property plumbing.

## State and Persistence Behavior
The structure stores a runtime pointer to an AppArmor label; label lifetime is managed by AppArmor, not this header.

## Dependencies and Integration Points
It integrates with the LSM property aggregation code and AppArmor's label implementation.

## Risks and Test Signals
Risks include stale label pointers and missing initialization when AppArmor is disabled or absent. Test signals are AppArmor label propagation tests and build coverage with different LSM configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm/apparmor.h -->
