# Research: sources/cloud-native/moby/daemon/libnetwork/drvregistry/ipams_test.go

Purpose: validates the IPAM driver registry after builtin IPAM registration. Important helper/API usage is `getNewIPAMs`, `IPAM`, and `WalkIPAMs`.

Control flow: `getNewIPAMs` constructs a zero-value registry and calls `ipams.Register`. The `IPAM` subtest checks that the `default` driver and capability can be retrieved. The `WalkIPAMs` subtest collects driver names through the callback, sorts them for deterministic comparison, and expects `default` and `null`, plus `windows` on Windows builds.

State/dependencies: tests rely on the registry's zero value being usable and on builtin IPAM registration being platform-sensitive. Dependencies include `runtime.GOOS`, `ipams.Register`, `ipamapi`, and `gotest.tools` assertions. Risks covered include missing builtin registration and callback walking. Risks not covered include duplicate registration, blank names, nil driver values, and concurrent registry use.
