# sources/control-plane/ceph-csi/internal/nfs/identity/identityserver.go

## Purpose
`identityserver.go` implements the NFS CSI identity server by wrapping the common default identity server and declaring controller-service plugin capability.

## Important APIs, Types, And Functions
`Server` embeds `*csicommon.DefaultIdentityServer`. `NewIdentityServer(d)` constructs the wrapper. `GetPluginCapabilities()` returns CSI `CONTROLLER_SERVICE` capability.

## Control Flow And State
Construction delegates default identity behavior to common CSI code. `GetPluginCapabilities()` ignores request contents and returns a static capability list.

## State And Persistence Behavior
No persistent state is managed here. The server holds only the embedded common identity server.

## Dependencies And Integration Points
The file uses CSI protobuf types and common Ceph-CSI identity support. It is installed by the NFS driver in all modes.

## Risks And Edge Cases
Only controller service capability is advertised explicitly here; other identity behavior comes from the default server. If future plugin capabilities are needed, this static list must be updated.

## Test Signals
No tests are included in this subset. A simple unit test could assert the returned capability list and default identity metadata.
