<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/shared.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/shared.h

## Purpose

`shared.h` is the central userspace compatibility header for imported kernel data-structure tests.

## Important APIs, Types, and Functions

It includes kernel-compatible types, bug, kernel, bitops, GFP, and RCU headers. It stubs module metadata macros `module_init`, `module_exit`, `MODULE_AUTHOR`, `MODULE_LICENSE`, and `MODULE_DESCRIPTION`. It maps missing `dump_stack()` to `assert(0)`.

## Control Flow and State

No runtime flow exists except the `dump_stack()` assertion fallback when invoked.

## Dependencies and Integration Points

It is included by xarray and maple shared headers and indirectly by many imported kernel sources. It provides the minimal module-like environment required to compile kernel code in userspace.

## Risks and Test Signals

Risks include macro collisions with imported headers and over-aggressive stubbing of module behavior. Successful shared test compilation is the main validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/shared.h -->
