# sources/cloud-native/moby/daemon/pkg/oci/caps/defaults.go

## Purpose
This file defines Docker's default Linux capability set for non-privileged containers.

## Important APIs, Types, And Functions
`DefaultCapabilities()` returns a new slice containing capabilities such as `CAP_CHOWN`, `CAP_DAC_OVERRIDE`, `CAP_MKNOD`, `CAP_NET_RAW`, `CAP_NET_BIND_SERVICE`, `CAP_SYS_CHROOT`, `CAP_KILL`, and `CAP_AUDIT_WRITE`.

## Control Flow
The function simply returns a literal slice each call.

## State, Persistence, And Dependencies
There is no state, persistence, or external dependency.

## Integration Points
`oci/defaults.go` uses this set in the default Linux spec, and `oci_linux.go` passes it through `TweakCapabilities` with container `CapAdd`, `CapDrop`, and privileged settings.

## Risks And Edge Cases
Changing this list directly changes the security posture of default containers. Returning a new slice avoids caller mutation of package-level state.

## Test Signals
No direct tests in this subset; capability behavior is indirectly covered by OCI and container security tests.
