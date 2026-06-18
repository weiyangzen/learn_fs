# sources/cloud-native/moby/daemon/internal/builder-next/reqbodyhandler.go

## Purpose
Implements an HTTP round tripper that serves build context request bodies through synthetic one-shot URLs.

## APIs, Control Flow, and Integration
`newReqBodyHandler` wraps a fallback `RoundTripper`. `newRequest` stores an `io.ReadCloser` under a generated ID and returns `http://build-context-<id>` plus a cleanup function. `RoundTrip` intercepts hosts with `build-context-`, requires GET, atomically removes the stored reader, and returns a 200 response with that body. Other requests delegate to the wrapped transport.

## State, Dependencies, and Risks
State is a mutex-protected map of pending bodies. Readers are single-use; retrying the synthetic URL returns `context not found`. Cleanup closes the body and removes the entry. Risks include leaks if cleanup is not called for unused URLs and no response headers/content length metadata. Integration is BuildKit HTTP source transport.
