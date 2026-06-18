# sources/distributed-fs/ceph-client/kernel/livepatch/patch.h

## Purpose
`patch.h` defines the internal ftrace patching interface used by the livepatch core and transition logic.

## Important APIs, Types, and Functions
`struct klp_ops` groups the global list node, RCU-visible `func_stack`, and registered `struct ftrace_ops`. The header declares `klp_find_ops()`, `klp_patch_object()`, `klp_unpatch_object()`, `klp_unpatch_objects()`, and `klp_unpatch_objects_dynamic()`.

## Control Flow
Core code calls `klp_patch_object()` after an object's symbols and relocations are ready. Transition and replace cleanup call unpatch helpers to remove normal or dynamic NOP stack entries. `klp_find_ops()` lets stack-checking logic find the previous active function for a given original function.

## State and Persistence Behavior
The header does not allocate state; it describes the in-memory ftrace state stack used by `patch.c`. The stack is part of live runtime redirection and is not persistent across module unload or reboot.

## Dependencies and Integration Points
It includes livepatch, list, and ftrace headers. It is used by `core.c` and `transition.c` to connect lifecycle management to function redirection.

## Risks and Test Signals
The `func_stack` contract is central: the first element is active unless transition state selects a lower entry. Tests should verify that stack traversal, replace cleanup, and transition stack checks agree on ordering.
