# sources/distributed-fs/ipfs-kubo/client/rpc/requestbuilder.go

## Purpose
This file provides the fluent request builder used by all HTTP RPC sub-APIs.

## Important APIs, Types, And Functions
`RequestBuilder` defines argument/body/option/header/send/exec methods. `requestBuilder` stores command state and shell pointer. `FileBody` wraps readers into multipart `files.MultiFileReader`; `encodedAbsolutePathVersion` controls compatibility for multipart path encoding.

## Control Flow
Callers add args, options, headers, or body, then `Send` applies global API options, builds a `Request`, and sends it. `Exec` sends and decodes JSON or drains/closes response when no result is expected.

## State And Persistence Behavior
State is accumulated builder data plus a deferred `buildError` when remote version lookup fails during `FileBody`.

## Dependencies And Integration Points
It integrates Boxo `files`, remote version negotiation, API offline options, and `Response.decode`.

## Risks And Test Signals
Risks include hidden network call in `FileBody`, reversed/fragile encoded-path compatibility logic, stringification of arbitrary options, and overwriting duplicate option keys. Signals are upload APIs working against old and new daemon versions.
