# Research: sources/cloud-native/buildkit/contrib/cdisetup/nvidia/log.go

Purpose: adapts command stdout/stderr bytes from NVIDIA CDI setup into BuildKit progress logs.

Important APIs and flow: `newStream` returns a `streamWriter` bound to a progress writer, stream number, and vertex digest. `streamWriter.Write` emits a `client.VertexLog` with timestamp, stream, byte payload, and vertex digest, then returns the full write length.

State and dependencies: no persistence; it writes progress events into the active setup context. Depends on BuildKit progress writer, `client.VertexLog`, time stamps, and digest identifiers.

Risks and test signals: this writer assumes progress writes do not need partial-write semantics; it reports success after emitting a log event. There are no direct tests, but it is used by NVIDIA setup command execution.
