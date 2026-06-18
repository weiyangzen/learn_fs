# sources/control-plane/mayastor/io-engine/tests/nexus_add_remove.rs

Purpose: compose-based integration test for creating, sharing, adding children to, removing/destroying, and handling child bdev destruction for NVMf-backed nexuses.

Important APIs/types/functions: helper functions `create_targets`, `nexus_3_way_create`, `nexus_destroy`, `nexus_share`, `nexus_create_2_way_add_one`, and `nexus_2_way_destroy_destroy_child`. Uses v0 bdev gRPC create/share, `nexus_create`, `nexus_lookup_mut`, `add_child`, `share_nvmf`, `bdev_destroy`, and `Share` trait.

Control flow: starts three Mayastor containers, creates/shares `disk0` on each, creates a three-way nexus and shares it then destroys it, creates a two-way nexus and adds the third remote child before sharing then destroys, creates another two-way shared nexus, adds a third child, then destroys one original child bdev by NVMf URL before stopping Mayastor and bringing compose down.

State and persistence: compose containers with malloc bdevs and in-process nexus state. No durable disk state.

Dependencies and integration points: docker compose, gRPC v0 bdev API, NVMf target/initiator, nexus dynamic child management, bdev destruction path.

Risks and edge cases: global `OnceCell` compose/Mayastor instances and fixed names make test order important. Last scenario does not explicitly assert post-destroy nexus state; it mainly checks no panic/error through teardown.

Test signals: covers NVMf remote child add/remove lifecycle and interaction with remote bdev destruction.
