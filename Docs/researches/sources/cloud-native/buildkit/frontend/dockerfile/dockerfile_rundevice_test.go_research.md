# sources/cloud-native/buildkit/frontend/dockerfile/dockerfile_rundevice_test.go

## Purpose
This build-tagged file (`//go:build dfrundevice`) tests experimental Dockerfile `RUN --device` support with CDI device specs. It verifies that a CDI device selected in a Dockerfile RUN instruction can inject environment variables into the build container.

## Important APIs, Types, and Functions
The file registers only `testDeviceRunEnv` into `allTests`. It uses `sb.CDISpecDir()` to write a CDI YAML spec, `client.New`, `f.Solve`, local mounts, local exporter output, `integration.SkipOnPlatform`, rootless detection, and `fstest.CreateFile`.

## Control Flow and Assertions
`testDeviceRunEnv` skips rootless and Windows environments. It writes `vendor1-device.yaml` with `cdiVersion: 0.6.0`, kind `vendor1.com/device`, device `foo`, a `containerEdits.env` entry `FOO=injected`, and BuildKit autoallow annotation. The Dockerfile runs BusyBox with `--device=vendor1.com/device=foo,required` plus an optional missing `vendor2.com/device=bar`, captures sorted environment to `foo.env`, exports it, and asserts the output contains `FOO=injected`.

## State, Persistence, and Dependencies
State persists only in the sandbox CDI spec directory for the test lifetime and exported local output. Dependencies include CDI support in the worker, non-rootless execution, Linux devices, Dockerfile frontend device parsing, and local export.

## Integration Points
This file integrates the Dockerfile frontend's `--device` option with worker CDI spec discovery, BuildKit device entitlement/autoallow behavior, environment injection, and exporter validation.

## Risks and Test Signals
Risks include CDI spec discovery failure, required device lookup regressions, optional missing devices incorrectly failing, environment edits not being applied, rootless/Windows unsupported paths accidentally running, and build tag coverage being omitted from default test runs. The signal is simple but strong: successful solve and exported environment containing the injected variable.
