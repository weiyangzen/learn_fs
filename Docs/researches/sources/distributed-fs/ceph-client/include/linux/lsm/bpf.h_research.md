<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm/bpf.h -->
# sources/distributed-fs/ceph-client/include/linux/lsm/bpf.h

## Purpose
This header defines BPF LSM-specific property storage for the generic LSM property container.

## Important APIs, Types, and Functions
`struct lsm_prop_bpf` carries a BPF LSM identifier field, using Linux integer types.

## Control Flow
There is no executable flow. Security code fills and reads the field through `struct lsm_prop`.

## State and Persistence Behavior
The field is runtime security metadata. It is not persisted by this header.

## Dependencies and Integration Points
It depends on `linux/types.h` and integrates with BPF LSM hooks and generic LSM property aggregation.

## Risks and Test Signals
Risks include uninitialized identifiers or inconsistent interpretation across LSM stacking. Test signals are BPF LSM selftests and LSM property conversion coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm/bpf.h -->
