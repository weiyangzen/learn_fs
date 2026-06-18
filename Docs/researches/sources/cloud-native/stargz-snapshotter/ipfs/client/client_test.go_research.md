# sources/cloud-native/stargz-snapshotter/ipfs/client/client_test.go

## Purpose
Provides an integration test for the IPFS client against a real IPFS API endpoint.

## Important APIs, Types, And Functions
The package-level `ipfsAPI` flag selects the API address. `TestIPFSClient` adds sample data and verifies full and ranged reads. `checkData` calls `StatCID` and `Get`, reads the returned body, and compares size/content.

## Control Flow
If `-ipfs-api` is absent, the test logs and skips. Otherwise it creates a client, adds `"hello world 0123456789"`, checks the whole content, and checks bytes 10 through 13 through `offset` and `length` query parameters.

## State And Persistence
State is external to the test process: `Add` pins data in the configured IPFS node. Test-local state is the CID returned by the node.

## Dependencies And Integration
Depends on a running IPFS daemon and is intended for `make test-ipfs`. It exercises real HTTP Kubo APIs through `client.go`.

## Risks And Test Signals
Passing signals confirm add/stat/cat compatibility with the configured IPFS daemon and ranged reads. It is skipped by default, so normal unit runs do not catch IPFS API regressions. It also leaves pinned data unless the daemon/test harness cleans it up.
