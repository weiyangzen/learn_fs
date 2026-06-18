# sources/cloud-native/cri-o/internal/oci/runtime_vm_linux.go

## Purpose
Linux VM runtime stats implementation, translating shim-returned cgroup v1/v2 metrics into CRI-O `stats.CgroupStats`.

## Important APIs and Control Flow
`runtimeVM.CgroupStats` calls task `Stats`, unmarshals the protobuf `Any`, accepts either containerd cgroups v1 or v2 metrics, and dispatches to `metricsV1ToCgroupStats` or `metricsV2ToCgroupStats`. `DiskStats` returns an empty stats object. The translation functions map CPU usage/throttling, memory/cache/swap/kernel fields, pids, hugetlb stats, and `SystemNano`.

## Dependencies, Integration, Risks, and Tests
Depends on containerd cgroup metrics, opencontainers cgroups stats, typeurl, and CRI-O errdefs/logging. The code accounts for guest cgroup version differing from host cgroup version. Risks are incomplete metric field mapping and empty disk stats. No direct tests in this subset.
