# Research: sources/cloud-native/moby/daemon/cluster/executor/container/container_test.go

## sources/cloud-native/moby/daemon/cluster/executor/container/container_test.go

Purpose: unit-tests key conversion invariants in `container.go` without requiring a live daemon. It constructs synthetic SwarmKit tasks and calls `containerConfig.hostConfig` or `labels` directly.

Important tests: `TestIsolationConversion` verifies SwarmKit isolation values map to Engine isolation modes; `TestContainerLabels` verifies system labels override user-specified labels in the reserved namespace; `TestCredentialSpecConversion` checks file, registry, and config credential specs become the expected `SecurityOpt` strings; `TestTmpfsConversion` verifies serialized tmpfs options are decoded into Engine mount options.

Control flow is table-driven with subtests. State is in-memory only; nil dependency getters are accepted because tested cases avoid CSI mounts. Dependencies include Engine container and mount API types, SwarmKit API structs, and `gotest.tools` assertions.

Risks captured by the tests are mostly regression risks in compatibility translation. Gaps include no coverage for port binding filtering, service config generation, network endpoint IP parsing, resource limits, and privilege subfields beyond credential specs. These tests are valuable because small translation changes can break existing swarm service behavior or label-based cleanup/status paths.
