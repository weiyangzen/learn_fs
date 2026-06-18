# sources/cloud-native/containerd/internal/nri/sandbox_linux.go

## Purpose
Adds Linux pod sandbox fields to NRI conversion.

## Important APIs, Types, And Functions
`podSandboxToNRI` calls `commonPodSandboxToNRI`, obtains `LinuxPodSandbox`, and fills namespaces, pod overhead/resources, cgroup parent/path, and resources.

## Control Flow
Selected on Linux builds and attaches the Linux payload before returning.

## State And Persistence
No state. Produces a snapshot for plugin requests.

## Dependencies And Integration Points
Uses NRI adaptation Linux pod sandbox types and feeds NRI Run/Update/Post lifecycle calls.

## Risks
Assumes `GetLinuxPodSandbox` is non-nil on Linux. No deep copy of nested resource structures.

## Test Signals
No direct tests in this subset; covered through NRI Linux integration.
