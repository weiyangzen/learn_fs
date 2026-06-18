# sources/cloud-native/moby/daemon/network/network_mode.go

## Purpose
This file exposes platform-independent network mode constants and predefined-network checks for the daemon network package.

## Important APIs, Types, And Functions
`DefaultNetwork` aliases the platform-specific `defaultNetwork`. `IsPredefined(network string)` delegates to the platform-specific `isPreDefined`.

## Control Flow
At compile time, Unix or Windows companion files provide the default network name and predefined logic. Consumers call this file's stable API regardless of platform.

## State, Persistence, And Dependencies
No mutable state or persistence. It depends only on the platform-specific files in the same package.

## Integration Points
Daemon network creation, deletion, filtering, and use/dangling checks rely on `IsPredefined` and `DefaultNetwork`.

## Risks And Edge Cases
The TODO notes predefined checks are not fully aligned across platforms, so callers must expect Windows and Unix differences.

## Test Signals
Platform behavior is indirectly covered by network filter and daemon network tests.
