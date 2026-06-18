# sources/cloud-native/moby/integration-cli/docker_api_attach_test.go

## Purpose
Integration tests for container attach over websocket, HTTP hijack, and client API.

## Important APIs and Types
Defines attach tests plus helpers `requestHijack`, `bodyIsWritable`, and `readTimeout`.

## Control Flow, State, and Persistence
Tests create interactive BusyBox containers, attach through `/containers/{id}/attach/ws` or hijacked HTTP POST, write stdin, and assert stdout/stderr multiplexing or TTY behavior. Not-found tests assert 404 responses. Client API tests validate media type, log replay, and stdcopy demultiplexing.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on Docker daemon API, raw socket connections, websocket package, stdcopy, and test request helpers. It mutates daemon container state and open streams. Risks include timing-sensitive reads, goroutine/socket leaks, and platform TTY differences. It provides strong signals for attach protocol compatibility and error response behavior.
