# sources/cloud-native/buildkit/source/containerblob/blobfetch/fetch.go

## Purpose
This package provides a shared helper for fetching a single content-addressed blob from either a registry-backed docker-image blob source or a client-side OCI layout content store. It is factored so both the container blob source and git bundle flow can reuse the same blob locator logic.

## Important APIs
`FetchOpt` carries scheme, reference, digest, registry hosts, session manager, optional session ID, and OCI store ID. `FetchBlob` validates the digest, dispatches by scheme, and returns an owned `io.ReadCloser` plus the digest. `fetchFromOCILayoutStore` reads from a session content store. `withOCICaller` selects either a pinned session or any caller in a session group.

## Control Flow
For `OCIBlobScheme`, `FetchBlob` requires `StoreID`, gets a caller, opens `sessioncontent.NewCallerStore(caller, "oci:"+StoreID)`, reads content info, and wraps `ReaderAt` as a read closer. For `DockerImageBlobScheme`, it obtains a resolver from the default pool, creates a fetcher for the ref, asserts `remotes.FetcherByDigest`, and fetches the digest directly.

## State and Persistence
No local persistent state. Registry and OCI content are external. Returned readers must be closed by callers. Pinned OCI sessions use a five-second lookup timeout before falling back to the parent context for actual IO.

## Dependencies and Integration Points
It depends on containerd remotes/docker, BuildKit sessions/content, source type scheme constants, resolver pool, and IO helpers. It is used by `containerblob/pull.go` and `source/git/bundle.go`.

## Risks
Unsupported schemes fail fast. OCI layout calls require a non-nil session manager and valid store ID. Registry fetchers must implement `FetcherByDigest`; otherwise the function returns an explicit type error. There is no size cap at this layer, so callers must handle large streams safely.

## Test Signals
No direct tests in this subset. Git bundle identifier tests validate locator parsing, while integration-style source tests elsewhere would cover actual fetch behavior.
