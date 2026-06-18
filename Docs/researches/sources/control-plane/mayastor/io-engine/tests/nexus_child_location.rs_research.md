# sources/control-plane/mayastor/io-engine/tests/nexus_child_location.rs

Purpose: verifies nexus children can report whether they are local or remote.

Important APIs/types/functions: uses compose to create/share a remote malloc bdev, then local `nexus_create`, `nexus_lookup_mut`, `children`, and `child.is_local()`.

Control flow: starts one remote Mayastor container, creates/shares remote `disk0`, starts local Mayastor, creates a two-child nexus with one local malloc URI and one remote NVMf URI, and asserts the first child is local while the second is not.

State and persistence: in-memory malloc devices and nexus state.

Dependencies and integration points: v0 bdev share API, NVMf URI handling, nexus child device locality detection.

Risks and edge cases: assumes child order matches URI order. Does not destroy nexus/container explicitly beyond compose drop behavior.

Test signals: targeted coverage for locality metadata used by scheduling/control-plane decisions.
