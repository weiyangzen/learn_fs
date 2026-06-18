# sources/distributed-fs/ceph-client/kernel/livepatch/state.c

## Purpose
`state.c` tracks compatibility of system state modifications declared by livepatches. It lets patches declare custom state IDs and versions, then prevents cumulative replace patches from discarding or downgrading state already modified by installed livepatches.

## Important APIs, Types, and Functions
`klp_for_each_state()` iterates a patch's state array until an ID of zero. Exported APIs are `klp_get_state()` and `klp_get_prev_state()`. Internal compatibility helpers are `klp_is_state_compatible()` and `klp_is_patch_compatible()`, with the last declared in `state.h` for core enable validation.

## Control Flow
`klp_get_state()` scans a specific patch for an ID. `klp_get_prev_state()` is only valid during a transition and scans installed patches before `klp_transition_patch`, returning the latest matching state. During patch enable, `klp_is_patch_compatible()` checks every state from every active old patch. If the new patch declares the same state, its version must be at least as new; if it omits the state, it is compatible only when the new patch is not an atomic replace patch.

## State and Persistence Behavior
The state table is static metadata in livepatch modules. No state is persisted by this file; it protects semantic persistence of externally modified kernel state across patch stacking and replacement.

## Dependencies and Integration Points
It depends on livepatch metadata structures, the active patch list from `core.h`, and `klp_transition_patch` from `transition.h`. Patch callbacks use `klp_get_state()` and `klp_get_prev_state()` to migrate or understand prior livepatch state.

## Risks and Test Signals
Missing or lower-version state in a replace patch can make kernel state incompatible after old patches are removed, so enable must fail. `klp_get_prev_state()` relies on transition ordering and should not be used outside transition callbacks. Tests should cover cumulative patch compatibility, non-replace patch coexistence, previous-state lookup ordering, and enable rejection for state downgrades.
