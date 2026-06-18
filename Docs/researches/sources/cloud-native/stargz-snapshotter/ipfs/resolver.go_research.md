# sources/cloud-native/stargz-snapshotter/ipfs/resolver.go

## Purpose
Implements a containerd `remotes.Resolver` for immutable IPFS/IPNS references whose root object is a JSON-encoded OCI descriptor containing IPFS URLs.

## Important APIs, Types, And Functions
`ResolverOptions` selects `Scheme` (`ipfs` or `ipns`) and optional `IPFSPath`. `NewResolver` resolves the local IPFS API URL and returns a resolver. `Resolve` fetches and decodes the root descriptor. `Fetcher` returns a fetcher whose `Fetch` downloads descriptor content by CID. `Pusher` returns an immutable-remote error.

## Control Flow
`NewResolver` validates the scheme, chooses `IPFS_PATH` or explicit option, and creates an IPFS client. `Resolve` calls `/api/v0/cat` for `/<scheme>/<ref>`, decodes an OCI descriptor, and requires at least one `ipfs://` URL. `Fetch` extracts the CID from the requested descriptor and cats `/<scheme>/<cid>`.

## State And Persistence
Resolver state is just scheme and IPFS client. Content persistence is external in IPFS. The resolver does not cache descriptors or fetched blobs.

## Dependencies And Integration
Depends on containerd remotes interfaces, local IPFS client, OCI descriptors, JSON decoding, and `GetCID` from `converter.go`. It lets containerd pull image content from IPFS-addressed descriptors.

## Risks And Test Signals
Risks include unsupported schemes, lack of push support, assuming the root ref is a CID/path compatible with containerd reference constraints, and no context-aware IPFS client calls. Tests are not in this subset; signals come from IPFS live client tests and resolver integration elsewhere.
