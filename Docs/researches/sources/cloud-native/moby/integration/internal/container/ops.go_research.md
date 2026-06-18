# sources/cloud-native/moby/integration/internal/container/ops.go

Purpose: functional-option library for constructing `TestContainerConfig` values used by integration container helpers.

Important APIs and helpers: `ConfigOpt` plus option functions including `WithName`, `WithHostname`, `WithLinks`, `WithImage`, `WithCmd`, `WithNetworkMode`, `WithDNS`, `WithSysctls`, `WithPublishAllPorts`, `WithExposedPorts`, `WithPortMap`, `WithTty`, `WithWorkingDir`, `WithMount`, `WithVolume`, `WithBind`, `WithBindRaw`, `WithTmpfs`, `WithMacAddress`, `WithIPv4`, `WithIPv6`, `WithEndpointSettings`, `WithLogDriver`, `WithAutoRemove`, `WithPidsLimit`, `WithRestartPolicy`, `WithUser`, `WithAdditionalGroups`, `WithPrivileged`, `WithCgroupnsMode`, `WithExtraHost`, `WithPlatform`, `WithWindowsDevice`, `WithIsolation`, `WithConsoleSize`, `WithAnnotations`, `WithRuntime`, `WithCDIDevices`, `WithCapability`, `WithDropCapability`, `WithSecurityOpt`, `WithPIDMode`, `WithStopSignal`, and `WithHostConfig`.

Control flow: each option mutates one part of `TestContainerConfig`: container config, host config, networking config, endpoint settings, platform, mounts, capabilities, devices, or raw host config replacement. IP/MAC options ensure endpoint settings exist before mutation.

State and persistence: no direct daemon state; options shape subsequent `ContainerCreate` requests. Some options append to slices and may accumulate when multiple options target the same field.

Dependencies and integration: depends on Moby container/network/mount types, NAT port parsing, `netip`, and OCI platform. It integrates with `NewTestConfig`, `Create`, and `Run`.

Risks: `WithHostConfig` replaces the whole host config and can discard earlier options if applied later. Several options initialize maps/slices lazily, so order can matter when callers pass overlapping settings.

Test signals: helper-only; correctness affects a broad range of integration tests by generating API request shapes.
