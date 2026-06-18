# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile2llb/convert_norundevice.go

Purpose: default build-tag implementation for Dockerfile RUN device support when labs device feature is not enabled.

Important API: `dispatchRunDevices(c)` returns an error if the parsed RUN command contains devices.

Control flow: selected by `//go:build !dfrundevice`. It checks `instructions.GetDevices(c)` and rejects any device usage with a message requiring Dockerfile frontend 1.14.0-labs or later.

State and persistence: none.

Dependencies and integration: called from `dispatchRun` only when LLB CDI cap support is available. Paired with `convert_rundevice.go`.

Risks and test signals: risk is build-tag/configuration mismatch where device syntax parses but should be unavailable. Labs frontend tests cover the positive variant.
