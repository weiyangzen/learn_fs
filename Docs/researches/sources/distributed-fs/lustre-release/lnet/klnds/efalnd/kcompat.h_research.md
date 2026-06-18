# sources/distributed-fs/lustre-release/lnet/klnds/efalnd/kcompat.h

## Purpose
This compatibility header provides EFALND-local shims for kernel API differences.

## Important APIs, Types, And Functions
When `HAVE_IBDEV_TO_NODE` is not defined, it defines `ibdev_to_node(struct ib_device *ibdev)`, which returns `NUMA_NO_NODE` without a parent device or `dev_to_node(parent)` otherwise.

## Control Flow
Including files get the native `ibdev_to_node()` when the kernel provides it. Older kernels compile the inline fallback and use the RDMA device's parent device to choose a NUMA node.

## State, Persistence, And Dependencies
There is no state. The header depends on RDMA `ib_verbs.h`, Linux device NUMA helpers, and the build-system feature macro.

## Integration Points
`efalnd.c` uses `ibdev_to_node()` during EFA device initialization to select a libcfs CPU partition when the NI does not specify CPTs.

## Risks
The fallback is only as accurate as the RDMA device parent relationship. If parent is absent, EFALND falls back through `NUMA_NO_NODE` and later chooses CPT 0, which can reduce locality.

## Test Signals
Build tests should cover kernels with and without `HAVE_IBDEV_TO_NODE`; runtime startup should verify CPT selection on devices with parent NUMA nodes and parentless mocks.
