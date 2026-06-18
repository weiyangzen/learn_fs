# Research: sources/distributed-fs/ipfs-kubo/config/remotepin.go

Purpose: Defines remote pinning service configuration and selectors for concealing API keys.

Important APIs/types/functions: `RemoteServicesPath`, `PinningConcealSelector`, `Pinning`, `RemotePinningService`, `RemotePinningServiceAPI`, `RemotePinningServicePolicies`, and `RemotePinningServiceMFSPolicy`.

Control flow, state, and persistence: No functions. Service endpoints and API keys persist in config; conceal selector identifies `Pinning.RemoteServices.*.API.Key` as sensitive for display.

Dependencies and integration points: Used by pin remote commands/services and MFS remote pin policy logic. Init creates an empty `RemoteServices` map.

Risks and test signals: API keys are stored in config and must be concealed in output. Repin intervals are strings and require downstream validation. No direct tests in this subset.
