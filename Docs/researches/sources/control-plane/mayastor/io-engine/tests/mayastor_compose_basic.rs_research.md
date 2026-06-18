# sources/control-plane/mayastor/io-engine/tests/mayastor_compose_basic.rs

Purpose: basic compose integration test that starts two Mayastor containers, creates and shares remote bdevs, then creates a local nexus over those NVMf exports and verifies device lookup behavior.

Important APIs/types/functions: compose `Builder`, v0 `GrpcConnect`, `BdevUri`, `BdevShareRequest`, `nexus_create`, `nexus_lookup_mut`, `bdev_create`, `UntypedBdev::bdev_first`, and `device_lookup`.

Control flow: bring up two debug containers, create/share `malloc:///disk0` on each, start an in-process Mayastor, create a two-child NVMf nexus, collect child device names, create an extra local malloc bdev, enumerate SPDK bdevs, assert only local/SPDK-visible devices count as two, and verify NVMf child devices are found by `device_lookup`.

State and persistence: compose containers and in-memory malloc devices. No durable state.

Dependencies and integration points: docker compose harness, v0 bdev gRPC API, NVMf target/initiator, local Mayastor reactor harness, device abstraction.

Risks and edge cases: asserts SPDK enumeration excludes NVMf device abstraction entries, so changes to enumeration semantics may require test updates. Fixed network CIDR/name.

Test signals: end-to-end signal for compose startup, remote share, local nexus creation, and NVMf device lookup outside SPDK bdev enumeration.
