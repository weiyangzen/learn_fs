# sources/control-plane/csi-driver-smb/pkg/smb/identityserver.go

## Purpose
CSI identity service implementation for the SMB driver.

## Important APIs, Types, and Functions
Implements `GetPluginInfo`, `Probe`, and `GetPluginCapabilities` on `Driver`.

## Control Flow
Plugin info validates configured name/version and returns them. Probe always returns ready true. Capabilities advertise controller service support.

## State and Persistence
Reads driver metadata only; no persistence.

## Dependencies
Depends on CSI protobufs, gRPC status/codes, and wrapperspb.

## Integration Points
Registered by the common gRPC server and used by sidecars/liveness checks.

## Risks and Edge Cases
Empty name/version makes GetPluginInfo unavailable. Probe does not verify backend mount readiness.

## Test Signals
`identityserver_test.go` covers info errors, probe readiness, and advertised plugin capabilities.
