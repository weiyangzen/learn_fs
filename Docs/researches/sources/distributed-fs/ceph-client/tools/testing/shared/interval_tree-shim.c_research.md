<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/interval_tree-shim.c -->
# sources/distributed-fs/ceph-client/tools/testing/shared/interval_tree-shim.c

## Purpose

`interval_tree-shim.c` pulls the kernel interval tree implementation into userspace tests as a standalone compilation unit.

## Important APIs, Types, and Functions

It simply includes `../../../lib/interval_tree.c`, exposing the interval tree implementation through the userspace shim include path.

## Control Flow and State

All control flow and state come from the included kernel source. The shim itself has no logic.

## Dependencies and Integration Points

It depends on shared userspace kernel-compat headers under `tools/testing/shared/linux` and the kernel `lib/interval_tree.c` source. It integrates with rbtree and interval-tree tests.

## Risks and Test Signals

Risks include include-path drift or missing compatibility stubs. Successful userspace interval-tree builds and tests validate the shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/interval_tree-shim.c -->
