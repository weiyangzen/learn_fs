# sources/cloud-native/containerd/internal/nri/sandbox.go

## Purpose
Defines pod sandbox metadata interfaces and common conversion to NRI pod sandbox objects.

## Important APIs, Types, And Functions
`PodSandbox` exposes domain, ID, name, UID, namespace, labels, annotations, runtime handler, Linux sandbox, PID, and IPs. `LinuxPodSandbox` exposes namespaces and Linux resource/cgroup fields. `commonPodSandboxToNRI` and `podSandboxesToNRI` convert values.

## Control Flow
Common conversion copies platform-neutral fields; platform-specific files add Linux fields on Linux.

## State And Persistence
No state. Output is a metadata snapshot for NRI plugin calls.

## Dependencies And Integration Points
Depends on NRI adaptation types and is used by `nri.go` lifecycle and sync requests.

## Risks
Returned maps/slices are not deep-copied. Nil Linux sandbox on Linux would panic in the Linux conversion.

## Test Signals
No direct tests in this subset; exercised by NRI lifecycle integration.
