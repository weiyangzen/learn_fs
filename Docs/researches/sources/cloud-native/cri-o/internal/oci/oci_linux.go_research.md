# sources/cloud-native/cri-o/internal/oci/oci_linux.go

## Purpose
Linux platform support for OCI runtime creation: conmon cgroup placement, process attributes, and sync-pipe creation.

## Important APIs and Control Flow
`InfraContainerName` is `POD`. `runtimeOCI.createContainerPlatform` builds a small generated spec, applies infra cpuset when configured and monitor cgroup is pod-scoped, mutates the conmon spec from workload annotations, moves conmon to the configured cgroup via the cgroup manager, and records the cgroupfs path for cleanup. `sysProcAttrPlatform` sets a new process group. `newPipe` creates a Unix socketpair used for conmon sync and start pipes.

## Integration, Risks, and Tests
Called from `runtimeOCI.CreateContainer` and `runtimePod.CreateContainer`. It depends on runtime-tools generate, CRI-O workload annotation mutation, cgroup manager, and Unix socketpairs. Risks are cgroup placement failures and mismatched assumptions about monitor cgroup names. Runtime tests use injected `RuntimeOCI`, but this exact cgroup path is mostly integration-tested outside this subset.
