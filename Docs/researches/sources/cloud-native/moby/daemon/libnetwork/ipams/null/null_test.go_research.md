# sources/cloud-native/moby/daemon/libnetwork/ipams/null/null_test.go

## Purpose
Tests the stateless null IPAM driver's accepted and rejected request forms.

## Important APIs, Types, And Functions
- `TestPoolRequest` validates default IPv4/IPv6 pool allocation and invalid pool request errors.
- `TestOtherRequests` validates nil address responses and unknown pool ID errors.

## Control Flow
Tests instantiate `allocator{}` directly and issue IPAM API calls. Assertions check exact pool IDs, prefixes, and error substrings.

## State And Persistence
No persistent or shared state.

## Dependencies And Integration Points
Uses `ipamapi` and `gotest.tools`. The tests establish the behavior expected by users selecting the `null` IPAM driver.

## Risks
The tests do not cover `ReleasePool`, `ReleaseAddress` valid path, or `Register`, but those paths are trivial.

## Test Signals
Confirms the driver is intentionally narrow: only empty pool/subpool requests in the `"null"` address space are valid.
