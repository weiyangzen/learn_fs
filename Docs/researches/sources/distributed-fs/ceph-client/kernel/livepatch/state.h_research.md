# sources/distributed-fs/ceph-client/kernel/livepatch/state.h

## Purpose
`state.h` exposes the internal compatibility check used by livepatch core enable logic.

## Important APIs, Types, and Functions
The only declared function is `bool klp_is_patch_compatible(struct klp_patch *patch)`.

## Control Flow
`core.c` calls this before taking ownership of a new livepatch module and before initializing patch structures. The check scans existing patch state metadata and rejects incompatible replace patches.

## State and Persistence Behavior
The header has no state. It provides access to state compatibility policy implemented in `state.c`.

## Dependencies and Integration Points
It includes `<linux/livepatch.h>` for `struct klp_patch`. It links the state subsystem into the patch enable path.

## Risks and Test Signals
The main risk is bypassing this check in new enable paths. Test signals are livepatch enable tests with state arrays and replace/non-replace combinations.
