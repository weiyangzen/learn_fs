<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/kernel.h -->
# sources/distributed-fs/ceph-client/tools/testing/memblock/linux/kernel.h

## Purpose

This shim `linux/kernel.h` lets the memblock simulator include common kernel utility declarations from the tools include tree while adding user-space headers and local stubs needed by memblock tests.

## Important APIs, Types, and Functions

It wraps the upstream tools kernel header and includes `errno`, C string support, local `printk`, linkage, kconfig, string, and ctype headers. It exports no new functions itself.

## Control Flow

There is no runtime control flow. Inclusion aggregates the headers expected by compiled kernel code.

## State and Persistence Behavior

The header has no state and creates no artifacts.

## Dependencies and Integration Points

It depends on `../../include/linux/kernel.h` and local simulator headers under `tools/testing/memblock/linux`. It is an integration point between real kernel includes and the constrained user-space memblock build.

## Risks and Edge Cases

Header-order changes can expose missing declarations or conflicting definitions between libc and kernel-style headers. Since it acts as an aggregate, unrelated kernel include changes can break this simulator layer.

## Test Signals

The signal is successful compilation of memblock simulator sources that include `<linux/kernel.h>`, especially after kernel header changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/memblock/linux/kernel.h -->
