<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/maple_tree.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/maple_tree.h

## Purpose

`linux/maple_tree.h` adapts the kernel maple-tree header for userspace testing.

## Important APIs, Types, and Functions

It includes `<linux/atomic.h>`, defines `U8_MAX` as `UCHAR_MAX`, and includes `../../../../include/linux/maple_tree.h`.

## Control Flow and State

There is no wrapper flow. Maple-tree behavior comes from the included kernel header and `maple-shim.c`.

## Dependencies and Integration Points

It depends on userspace atomic compatibility, limits definitions, and the kernel maple-tree include. It integrates with `maple-shared.h`, `maple-shim.c`, and VMA tests using maple trees for VMA indexing.

## Risks and Test Signals

Risks include missing constants expected by kernel code and header drift. Successful maple-tree and VMA test builds validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/maple_tree.h -->
