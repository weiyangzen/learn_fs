# sources/cloud-native/containerd/core/sandbox/controller.go

## Purpose
Defines the runtime sandbox controller interface, option types, and status/instance structs used to manage sandbox lifecycles.

## APIs, Flow, State, Dependencies, Risks, And Tests
`CreateOptions` carries rootfs mounts, marshaled sandbox options, network namespace path, and annotations. `WithRootFS`, `WithOptions`, `WithNetNSPath`, and `WithAnnotations` populate it. `StopOptions` and `WithTimeout` carry optional stop timeout. `Controller` defines create/start/platform/stop/wait/status/shutdown/metrics/update operations. `ControllerInstance`, `ExitStatus`, and `ControllerStatus` model returned runtime state.

The file defines contracts only; it does not persist state. Options marshal arbitrary values through typeurl, so type registration matters. Dependencies include mount types, metrics protobuf, typeurl, image-spec platform, and time.

Integration points are remote sandbox proxy controllers, shim sandbox implementations, CRI, and task manager sandbox reuse. Risks include ambiguous field update semantics, option marshal failures, timeout truncation in proxies, and controllers returning inconsistent address/version values. Test signals are option unit tests, controller conformance tests, and lifecycle integration with a real sandbox shim.
