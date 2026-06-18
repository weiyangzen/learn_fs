# sources/cloud-native/moby/daemon/libnetwork/ipams/windowsipam/windowsipam_other.go

## Purpose
Provides a non-Windows build stub for the Windows IPAM package.

## Important APIs, Types, And Functions
- Build-tagged `!windows`.
- `Register(ipamapi.Registerer) error` is a no-op returning nil.

## Control Flow
No runtime behavior beyond successful return.

## State And Persistence
No state.

## Dependencies And Integration Points
Allows `ipams/drivers.go` to import and call `windowsipam.Register` on all platforms without conditional compilation in the caller.

## Risks
None beyond ensuring Windows-only behavior is not accidentally expected on other platforms.

## Test Signals
No direct test; cross-platform compilation is the main signal.
