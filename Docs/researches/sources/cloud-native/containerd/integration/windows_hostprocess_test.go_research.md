# sources/cloud-native/containerd/integration/windows_hostprocess_test.go

## Purpose

`windows_hostprocess_test.go` verifies Windows HostProcess container behavior, allowed identities, host command execution, host networking, stats, and argument escaping.

## Important APIs, Types, and Functions

- `hpcAction` is a callback run after a HostProcess container starts.
- Global option variables define Local Service, Local System, HostProcess, and default pause command options.
- `TestWindowsHostProcess` runs subtests for accepted users, rejected Guest user, host command execution, host network environment, OS-version image mismatch tolerance, and stats.
- `runHostProcess` creates a HostProcess pod/container and applies the callback.
- `runExecAndRemoveContainer` creates, starts, execs `cmd /c echo hello`, stops, and removes a container.
- `TestArgsEscapedImagesOnWindows` checks images with ArgsEscaped metadata on supported builds, with and without explicit container command.

## Control Flow

HostProcess subtests pull pause image, create HostProcess pods, create containers with different options, start them, optionally expect start failure, then run checks such as stats polling. ArgsEscaped coverage detects host build, creates a sandbox, pulls the ArgsEscaped image, and runs exec/remove cycles for two container config variants.

## State and Persistence Behavior

The tests exercise Windows HostProcess runtime state, CRI stats, labels/annotations in stats validation, and container lifecycle cleanup. They do not inspect persistent files beyond normal CRI state.

## Dependencies and Integration Points

They integrate hcsshim OS version constants, Windows registry, CRI runtime service, image fixtures, HostProcess pod/container config helpers, stats helper `testStats`, and Windows command execution.

## Risks and Edge Cases

The file contains an unusual assignment `_, err = t, runtimeService.StartContainer(cn)` that discards `t` and captures the start error; it compiles but is easy to misread. HostProcess availability, Windows identity rules, OS build compatibility, and image availability are major environmental factors.

## Test Signals

Failures identify regressions in HostProcess validation/execution, Windows user handling, host network behavior, stats for HostProcess containers, or ArgsEscaped command handling.
