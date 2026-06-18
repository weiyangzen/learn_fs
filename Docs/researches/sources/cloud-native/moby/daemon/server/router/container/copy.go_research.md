# sources/cloud-native/moby/daemon/server/router/container/copy.go

## Purpose
`copy.go` implements the container archive endpoints: stat a path, download a path as a tar stream, and upload/extract a tar stream into a container path.

## Important APIs, Types, And Functions
`setContainerPathStatHeader` JSON-encodes `container.PathStat` and stores it as base64 in `X-Docker-Container-Path-Stat`. Route handlers are `headContainersArchive`, `getContainersArchive`, and `putContainersArchive`. `writeCompressedResponse` negotiates `gzip` or `deflate` with `gddo/httputil.NegotiateContentEncoding`.

## Control Flow
Handlers parse archive form values through `httputils.ArchiveFormValues`, call the backend (`ContainerStatPath`, `ContainerArchivePath`, or `ContainerExtractToDir`), set metadata headers, then stream tar data. Upload converts the legacy `noOverwriteDirNonDir` flag into `allowOverwriteDirWithFile` and passes `copyUIDGID` plus the request body to the backend.

## State And Persistence
The router itself holds no durable state. Persistent effects happen only through the backend: archive extraction can modify the container filesystem, ownership, and overwrite behavior.

## Dependencies And Integration Points
This file integrates the container router with backend copy/archive operations, HTTP content negotiation, compression writers, `io.Copy`, and API `PathStat`.

## Risks
Header encoding must remain compatible because clients decode it directly. Streaming responses can only return structured errors before data is flushed. Upload semantics around directory/file overwrite are inverted for historical compatibility, which is easy to regress.

## Test Signals
No direct tests in this file; behavior is usually covered by API/integration tests for `GET/HEAD/PUT /containers/{id}/archive`.
