# Research: sources/cloud-native/buildkit/cmd/buildkitd/service_unix.go

Purpose: provides no-op service-management hooks on non-Windows builds so the cross-platform main daemon code can call service helpers uniformly.

Important APIs and flow: `serviceFlags` returns no flags, `applyPlatformFlags` does nothing, `registerUnregisterService` returns `(false, nil)`, and `launchService` returns nil.

State and dependencies: no state or persistence. Depends only on urfave/cli and gRPC types to match the shared signatures.

Risks and test signals: low-risk shim; incorrect behavior would unexpectedly stop or alter daemon startup on Unix. There are no direct tests.
