# sources/control-plane/mayastor/io-engine/tests/reset.rs

Purpose: integration smoke test that a mirrored nexus bdev can be opened and reset successfully.

Important APIs/types/functions: `nexus_reset_mirror` uses compose v0 bdev create/share RPCs, `nexus_create`, `MayastorTest`, `MayastorCliArgs`, and `UntypedBdevHandle::open(...).reset()`.

Control flow: two io-engine containers create and share malloc bdevs over NVMe-oF. A local Mayastor instance creates a 50 MiB nexus over both child URIs, opens it for I/O, and awaits a reset.

State/persistence: transient child bdevs and one nexus; reset state is in SPDK bdev/nexus runtime only.

Dependencies/integration: covers remote NVMe-oF child setup, local nexus creation, bdev handle acquisition, and reset path propagation through mirrored children.

Risks: no post-reset I/O validation; success only means reset returned `Ok`. Requires NVMe-oF network setup and fixed malloc sizes.

Test signals: useful low-level signal for nexus reset path not panicking or returning immediate errors.
