# sources/cloud-native/moby/daemon/libnetwork/network_unix.go

## Purpose
Non-Windows platform implementation for network platform hooks: DNS resolver stubs, default IPAM selection, advertise-address option validation, and prune eligibility.

## Important APIs, Types, And Functions
`platformNetwork` is empty. `startResolver` and `deleteEpFromResolver` are stubs. `defaultIpamForNetworkType` returns default IPAM. `validatedAdvertiseAddrNMsgs` and `validatedAdvertiseAddrInterval` parse driver options and enforce `osl` min/max bounds. `IsPruneable` rejects predefined Docker networks.

## Control Flow
Advertise validators fetch string driver options, convert with `strconv.Atoi`, construct typed values, and return nil when unset. Prune checks call `network.IsPredefined(n.Name())`.

## State And Persistence
No local state. The validators read network driver options stored in `Network.generic`.

## Dependencies And Integration Points
Used by `network.go` validation and advertisement behavior. Integrates with `netlabel`, `osl`, default IPAM, and daemon network predefined-name helpers.

## Risks
Invalid advertise option strings prevent network creation on Unix. Stub DNS resolver behavior means Unix internal DNS setup is handled elsewhere rather than at the network platform hook.

## Test Signals
Linux integration tests exercise network creation with driver options and prune/lifecycle paths indirectly; no direct advertise-option tests in this subset.
