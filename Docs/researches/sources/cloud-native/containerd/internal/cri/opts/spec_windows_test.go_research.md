# sources/cloud-native/containerd/internal/cri/opts/spec_windows_test.go

## Purpose

This Windows-focused test file validates Windows device parsing, Windows resource mapping, and drive mount behavior.

## Important APIs, Types, and Functions

`TestWithDevices` exercises `WithWindowsDevices`. `TestWithWindowsResources` checks CPU/memory/affinity resource conversion. `TestDriveMounts` checks mount parsing and path normalization for drive-style Windows paths.

## Control Flow

The tests construct CRI configs/resources/mounts, apply the Windows spec options to OCI specs, and assert expected fields or errors.

## State and Persistence Behavior

The tests use in-memory specs and mocked filesystem/OS interactions where needed. They should not require real HCS containers.

## Dependencies and Integration Points

They cover `spec_windows_opts.go` and indirectly guard behavior used by `server/container_create.go` Windows spec construction.

## Risks and Edge Cases

Coverage is strongest for explicit table cases but may not include named pipe mounts, credential specs, or every invalid path form.

## Test Signals

Passing tests signal that CRI Windows devices and resources are translated into valid OCI Windows fields and that mount path handling remains compatible with hcsshim expectations.
