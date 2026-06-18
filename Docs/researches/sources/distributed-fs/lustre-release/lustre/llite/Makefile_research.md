# sources/distributed-fs/lustre-release/lustre/llite/Makefile

## Purpose
This Kbuild Makefile composes the llite client module `lustre.o` from the client filesystem object files.

## Important APIs, Types, and Functions
It defines `obj-m += lustre.o`, accumulates the `lustre-objs` list, conditionally adds `acl.o` through `lustre-$(CONFIG_FS_POSIX_ACL)`, and enables `GCOV_PROFILE := y` for `CONFIG_GCOV_PROFILE_LUSTRE`.

## Control Flow
Kbuild expands the object lists and links them into the loadable Lustre client module. There is no runtime control flow.

## State and Persistence Behavior
The file affects build outputs only. GCOV changes instrumentation in generated objects.

## Dependencies and Integration Points
It integrates with Linux Kbuild and kernel config symbols for POSIX ACL and GCOV support.

## Risks and Edge Cases
Missing objects cause feature loss or unresolved symbols. ACL support is configuration-sensitive. Coverage instrumentation can change performance and should be tested separately from production builds.

## Test Signals
Build llite with ACL on/off and GCOV on/off, checking for link errors and missing exported symbols.
