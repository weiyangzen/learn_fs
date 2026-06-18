# sources/cloud-native/stargz-snapshotter/ipfs/client/client.go

## Purpose
Implements a small HTTP client for Kubo/IPFS RPC APIs used by the snapshotter's IPFS conversion and resolver paths.

## Important APIs, Types, And Functions
`Client` holds an API base address and HTTP client. `New` constructs it. `FileInfo` mirrors `/api/v0/files/stat` JSON. `StatCID` posts to files/stat, `Get` posts to cat with optional offset and length, `Add` streams multipart form data to add with CID v1 and pin enabled, and `GetIPFSAPIAddress` reads the local IPFS repo `api` file and converts its multiaddr to a URL.

## Control Flow
Each RPC checks that `Address` is set, defaults nil HTTP client, builds a POST request with query parameters, executes it, drains/closes the body on error, validates 2xx status, and decodes or returns the body. `Add` uses `io.Pipe` and a multipart writer goroutine so content streams without prebuffering.

## State And Persistence
Client state is only address and HTTP client. IPFS persistence occurs externally in the IPFS daemon: `Add` pins uploaded data. `GetIPFSAPIAddress` reads `~/.ipfs/api` or a specified repository path.

## Dependencies And Integration
Depends on standard HTTP/multipart/JSON packages, homedir expansion, multiaddr parsing, and multiaddr/net dial args. Used by `ipfs/converter.go` and `ipfs/resolver.go`.

## Risks And Test Signals
Risks include no explicit request contexts, body ownership differences between success and error paths, blocking pipe writes if request construction fails late, and assuming HTTP scheme. `client_test.go` provides optional live IPFS coverage for add/stat/ranged cat.
