# sources/distributed-fs/lustre-release/lnet/klnds/socklnd/Makefile

## Purpose
This Makefile defines the kernel module build composition for Lustre's socket LNet network driver (`ksocklnd`). It tells kbuild to produce `ksocklnd.o` as a module and lists the object files that make up the module.

## Important APIs, types, and functions
- `obj-m += ksocklnd.o` declares `ksocklnd` as a loadable kernel module target.
- `ksocklnd-objs := ...` composes the module from `socklnd.o`, `socklnd_cb.o`, `socklnd_lib.o`, `socklnd_modparams.o`, and `socklnd_proto.o`.
- `ifdef CONFIG_GCOV_PROFILE_LNET` sets `GCOV_PROFILE := y` to enable coverage instrumentation when LNet GCOV profiling is enabled.

## Control flow
kbuild reads this file during the kernel/module build. When `ksocklnd.o` is selected as a module, it links the listed objects into one module. If the build configuration defines `CONFIG_GCOV_PROFILE_LNET`, kbuild enables GCOV coverage for this directory/module.

## State and persistence behavior
The Makefile has no runtime state. Its persistent effect is build graph structure: adding, removing, or reordering objects changes which translation units become part of `ksocklnd`.

## Dependencies and integration points
It integrates with the Linux kbuild system and the Lustre LNet build configuration. The object list must match actual socket LND source files in the same directory and must stay aligned with any source split or new required translation units.

## Risks and edge cases
- Missing an object from `ksocklnd-objs` can produce unresolved symbols or silently omit required protocol functionality.
- Adding GCOV profiling changes build flags and can affect timing-sensitive kernel code.
- This file is for `socklnd`, not `o2iblnd`; changes should not be conflated with the RDMA driver researched in the other files.

## Test signals
Build `ksocklnd` as a module with and without `CONFIG_GCOV_PROFILE_LNET`; verify all socket LND objects link and module symbols resolve. Packaging tests should confirm `ksocklnd.ko` is produced when the socket LND is enabled.
