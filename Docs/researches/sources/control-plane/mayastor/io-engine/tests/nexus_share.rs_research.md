# sources/control-plane/mayastor/io-engine/tests/nexus_share.rs

Purpose: tests in-process nexus sharing semantics: idempotent nexus NVMf sharing, rejection of generic bdev NVMf sharing for a nexus bdev, and consistent unshare state.

Important APIs/types/functions: `nexus_create`, `nexus_lookup_mut`, `MayastorTest`, `MayastorCliArgs`, `Reactor::block_on`, `Share`, `Protocol`, `UntypedBdev`, and `mayastor_env_stop`.

Control flow: the test starts Mayastor with two reactors, creates a two-child malloc nexus, shares it over NVMf twice through the nexus-specific path, verifies the returned URI is stable, then attempts direct generic bdev NVMf sharing and expects an error. It unshares the nexus, checks both nexus and underlying bdev report `Protocol::Off`, destroys the nexus, and stops the environment.

State and persistence behavior: no persistent store. State is local SPDK/nexus share status and the relationship between nexus abstraction and underlying bdev status.

Dependencies and integration points: in-process SPDK environment, reactor blocking, nexus APIs, and untyped bdev APIs.

Risks: direct generic sharing policy may change; environment stop is required to avoid leaking reactors.

Test signals: repeated share returns the same URI, direct bdev share errors, unshare leaves both objects off, and destroy/stop succeeds.
