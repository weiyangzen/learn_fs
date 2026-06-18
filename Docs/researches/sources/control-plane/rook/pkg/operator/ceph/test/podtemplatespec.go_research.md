# sources/control-plane/rook/pkg/operator/ceph/test/podtemplatespec.go

Purpose: top-level test helper for validating complete Ceph `PodTemplateSpec` objects.

Important APIs/types/functions: `PodTemplateSpecTester`, `NewPodTemplateSpecTester`, `AssertLabelsContainCephRequirements`, and `RunFullSuite`.

Control flow: `RunFullSuite` first checks labels on the pod template, then delegates to `Spec().RunFullSuite` for pod spec, volumes, containers, resources, restart policy, chown container, and priority class checks.

State and persistence behavior: no persistence; wraps an in-memory pointer to a `v1.PodTemplateSpec`.

Dependencies/integration: depends on `spec.go` label checks and `podspec.go` pod spec checks.

Risks: this helper assumes caller supplies all daemon identity strings correctly; wrong expectations can make tests pass against wrong labels if both code and test use the same bad inputs.

Test signals: no local tests. Its effectiveness comes from daemon-specific tests using the shared full suite.
