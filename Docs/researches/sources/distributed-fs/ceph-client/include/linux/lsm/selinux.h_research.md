<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm/selinux.h -->
# sources/distributed-fs/ceph-client/include/linux/lsm/selinux.h

## Purpose
This header defines the SELinux-specific property payload used by the generic LSM property model.

## Important APIs, Types, and Functions
`struct lsm_prop_selinux` contains SELinux security identifiers, typically subject/object SID-style values represented with fixed-width types.

## Control Flow
There is no control flow. SELinux fills these properties and generic LSM helpers consume them for audit, context conversion, or object labeling.

## State and Persistence Behavior
The structure stores runtime security IDs. Actual label policy state and persistence are managed by SELinux policy and object xattrs, not the header.

## Dependencies and Integration Points
It depends on `linux/types.h` and integrates with SELinux, generic LSM properties, audit, and security context conversion hooks.

## Risks and Test Signals
Risks include SID mismatch, zero/uninitialized IDs, and stacking bugs when multiple LSMs provide properties. Test signals are SELinux policy tests, audit context output, and secctx conversion selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm/selinux.h -->
