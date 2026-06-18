# sources/control-plane/rook/pkg/operator/ceph/test/podspec.go

Purpose: shared assertions for Ceph pod specs, layering Ceph-specific expectations over generic operator pod-spec tests.

Important APIs/types/functions: `PodSpecTester`, `(*PodTemplateSpecTester).Spec`, `NewPodSpecTester`, `AssertVolumesMeetCephRequirements`, `AssertRestartPolicyAlways`, `AssertChownContainer`, `AssertPriorityClassNameMatch`, `RunFullSuite`, `allContainers`, and `containerExists`.

Control flow: `RunFullSuite` builds generic resource expectations, runs generic pod spec checks, then validates required Ceph volumes, restart policy, required chown init container by daemon type, priority class, and all Ceph container requirements. Volume validation computes daemon keyring secret names with special cases for mon and filesystem mirror daemons and validates volume source kinds for data/config/keyring volumes.

State and persistence behavior: no persistence; all checks are in-memory assertions on `v1.PodSpec`.

Dependencies/integration: depends on Ceph daemon type constants, generic `pkg/operator/test` pod-spec helpers, Kubernetes core types, and `containers.go`.

Risks: expected volume-source rules are encoded by daemon type and can become stale as daemon specs evolve. `allContainers` appends to the init container slice, which can reuse backing arrays but only returns a combined slice for reads here.

Test signals: no direct tests in this subset; these helpers are intended to raise consistency failures in many daemon-specific unit tests elsewhere.
