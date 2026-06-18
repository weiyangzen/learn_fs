# sources/cloud-native/nydus/contrib/nydusify/examples/converter/main.go

## Purpose
This example demonstrates embedding the converter package directly from Go instead of invoking the `nydusify` CLI.

## Important APIs, Types, and Functions
It imports `converter`, builds a `converter.Opt`, and calls `converter.Convert(context.Background(), opt)`.

## Control Flow
`main` sets sample work directory, nydus-image path, source, target, platform, insecure flags, prefetch patterns, merge setting, and Docker-to-OCI conversion flag. It panics on conversion error.

## State, Persistence, and Dependencies
State and persistence are delegated to `converter.Convert`, which may create temporary work directories, push images, and invoke `nydus-image`. This file depends on `context` and the local converter package.

## Integration Points
It is a developer-facing code sample for library-style integration of conversion behavior.

## Risks and Test Signals
The hard-coded `nydus-image` path and registry references are placeholders, so running it as-is will usually fail. It does not expose backend, cache, or retry options. The companion test monkeypatches `converter.Convert` to validate the option wiring.
