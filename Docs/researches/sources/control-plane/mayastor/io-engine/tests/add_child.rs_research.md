# sources/control-plane/mayastor/io-engine/tests/add_child.rs

Purpose: integration test for adding and removing nexus children on both unshared and NVMf-shared nexuses backed by AIO files.

Important APIs/types/functions: uses `nexus_create`, `nexus_lookup_mut`, `Nexus::add_child`, `remove_child`, `share(Protocol::Nvmf)`, and `unshare_nexus`. `test_start`/`test_finish` manage two 64 MiB temp disk files.

Control flow: creates a one-child nexus, adds the second child without rebuild, asserts two children and that the added child is opened unsynchronized, removes it, shares the nexus over NVMf, repeats add/remove while shared, then unshares and deletes files.

State and persistence: uses temporary files under `/tmp`; nexus state is in memory. The test observes child state transitions but does not persist metadata.

Dependencies and integration points: depends on `MayastorTest` reactor harness, AIO bdev creation through child URIs, and NVMf sharing stack.

Risks and edge cases: fixed `/tmp/disk1.img` and `/tmp/disk2.img` names can collide with parallel tests. It assumes NVMf target initialization succeeds. It does not verify rebuild completion, only initial unsync state.

Test signals: confirms child add/remove works before and after sharing and protects expected unsynchronized state for newly added children.
