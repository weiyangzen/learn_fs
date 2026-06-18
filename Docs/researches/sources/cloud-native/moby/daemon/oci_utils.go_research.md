# sources/cloud-native/moby/daemon/oci_utils.go

## Purpose
This file maps Docker's Linux domainname configuration into an OCI-compatible sysctl.

## Important APIs, Types, And Functions
`setLinuxDomainname(c *container.Container, s *specs.Spec)` ensures `s.Linux.Sysctl` exists and sets `kernel.domainname` when `c.Config.Domainname` is non-empty.

## Control Flow
The function lazily initializes `s.Linux` and `s.Linux.Sysctl`, then writes the sysctl. It is called by `withCommonOptions`.

## State, Persistence, And Dependencies
Only the in-memory OCI spec is mutated. Dependencies are Docker container config and runtime-spec types.

## Integration Points
OCI has no explicit NIS domainname field, so Linux daemon spec generation relies on this sysctl to match `setdomainname(2)` behavior.

## Risks And Edge Cases
Explicit host config sysctls are merged later by `WithSysctls` and intentionally override this implicit value. The helper is Linux-specific.

## Test Signals
`oci_linux_test.go` verifies implicit domainname sysctl creation and explicit override behavior.
