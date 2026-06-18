<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/livepatch_helpers.h -->
# sources/distributed-fs/ceph-client/include/linux/livepatch_helpers.h

## Purpose
This header provides convenience macros for livepatch patch source files. It registers callbacks into discardable metadata sections, supplies object naming, adapts static calls, and helps define syscall replacements.

## Important APIs, Types, and Functions
`KLP_OBJNAME` resolves to the module build name or `vmlinux`. `KLP_PRE_PATCH_CALLBACK`, `KLP_POST_PATCH_CALLBACK`, `KLP_PRE_UNPATCH_CALLBACK`, and `KLP_POST_UNPATCH_CALLBACK` place callback pointers in `.discard.klp_callback_ptrs`. `KLP_STATIC_CALL(name)` converts a static call to an indirect call through the key. `KLP_SYSCALL_DEFINE1` through `KLP_SYSCALL_DEFINE6` wrap syscall replacement definitions, with x86-64-specific stubs.

## Control Flow
The macros expand at compile time into section entries and syscall wrapper functions. The livepatch loader later reads callback pointer sections. Syscall macros generate ABI entry stubs that cast, validate, protect, and call a patch-local implementation.

## State and Persistence Behavior
State is static module metadata and generated functions. There is no runtime storage owned by the header.

## Dependencies and Integration Points
It depends on syscall wrapper macros, livepatch core types, static-call definitions, module build names, and x86 syscall wrapper conventions.

## Risks and Test Signals
Risks include architecture-limited syscall support, wrong object name selection, using `KLP_STATIC_CALL` where direct static-call semantics are required, and callback pointer section mistakes. Test signals are successful patch module build, objtool metadata inspection, livepatch callback execution, and syscall ABI tests on patched syscalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/livepatch_helpers.h -->
