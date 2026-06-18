# sources/cloud-native/moby/daemon/libnetwork/ipams/windowsipam/windowsipam_test.go

## Purpose
Windows-only tests for the Windows IPAM driver contract.

## Important APIs, Types, And Functions
- `TestWindowsIPAM` exercises `RequestPool`, `ReleasePool`, `RequestAddress`, and `ReleaseAddress`.

## Control Flow
The test requests default and explicit pools, checks unsupported subpool and IPv6 errors, releases a pool, requests nil and preferred addresses, passes a gateway request option, and releases the address.

## State And Persistence
No persistent state; the allocator is stateless.

## Dependencies And Integration Points
Uses `ipamapi`, `netlabel.Gateway`, libnetwork `types`, and `gotest.tools`. Build tag means it only runs on Windows.

## Risks
Does not verify integration with HNS or controller network creation. It documents the minimal behavior rather than full Windows networking semantics.

## Test Signals
Confirms the driver returns `0.0.0.0/0` by default, echoes explicit pools, rejects unsupported features, and returns preferred IPs with the pool mask.
