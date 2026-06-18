# sources/cloud-native/buildkit/source/containerimage/ocilayout.go

## Purpose
This file implements a containerd `remotes.Resolver`/`Fetcher` backed by a client-side OCI layout content store exposed over a BuildKit session. It lets the normal image resolution and pull utilities operate against local OCI content.

## Important APIs and Types
`getOCILayoutResolver` constructs an `ociLayoutResolver` for a store/session group. `Fetcher` returns the resolver as its own fetcher. `Fetch` opens content by descriptor from `sessioncontent.NewCallerStore`. `Resolve` maps a digest-qualified reference to a descriptor with detected media type. `info` reads content info, and `withCaller` selects a pinned or group session caller.

## Control Flow
`Resolve` parses the ref, requires a digest, gets content info from the remote store, creates a descriptor with digest and size, fetches the root blob, reads up to `maxReadSize` bytes, detects whether it is an image manifest or index, and sets descriptor media type. `Fetch` and `info` use `withCaller`; pinned sessions use a five-second lookup timeout.

## State and Persistence
No local durable state. The resolver reads remote content through the session. `maxReadSize` limits root manifest media-type probing to 4 MiB.

## Dependencies and Integration Points
It integrates with BuildKit `sourceresolver.ResolveImageConfigOptStore`, sessions, session content stores, containerd remotes/content interfaces, reference parsing, and image media-type detection. It is used by container image source metadata and pull paths when resolver type is OCI layout.

## Risks
OCI layout tag references are not supported; references must include a digest. Missing or wrong store IDs fail at session content lookup. The root manifest reader is not explicitly closed after `io.ReadAll`, which relies on the wrapped reader's lifecycle and could be tightened. Large or malformed root blobs fail media type detection.

## Test Signals
No direct tests in this subset. It is covered indirectly by OCI layout source integration tests outside this subset.
