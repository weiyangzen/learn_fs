<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/hostconfig.go -->
# sources/cloud-native/moby/api/types/container/hostconfig.go

## Purpose
Defines the large host-side container runtime configuration surface: namespaces, devices, cgroups,
logging, restart policy, resources, security, networking, and storage mounts.

## Important APIs, Types, And Functions
- Exported types: CgroupnsMode, Isolation, IpcMode, NetworkMode, UsernsMode, CgroupSpec, UTSMode, PidMode, DeviceRequest, DeviceMapping, RestartPolicy, RestartPolicyMode, LogMode, LogConfig, Ulimit, Resources, UpdateConfig, HostConfig.
- Exported functions/methods: IsPrivate, IsHost, IsEmpty, Valid, IsDefault, IsHyperV, IsProcess, IsPrivate, IsHost, IsShareable, IsContainer, IsNone, IsEmpty, Valid, and others.
- Constants: CgroupnsModeEmpty, CgroupnsModePrivate, CgroupnsModeHost, IsolationEmpty, IPCModeNone, IPCModeHost, IPCModeContainer, IPCModePrivate, IPCModeShareable, RestartPolicyDisabled, RestartPolicyAlways, RestartPolicyOnFailure, RestartPolicyUnlessStopped, LogModeUnset, LogModeBlocking, LogModeNonBlock.
- `DeviceRequest` fields include Driver, Count, DeviceIDs, Capabilities, Options.
- `DeviceMapping` fields include PathOnHost, PathInContainer, CgroupPermissions.
- `RestartPolicy` fields include Name, MaximumRetryCount.
- `LogConfig` fields include Type, Config.
- `Resources` fields include CPUShares, Memory, NanoCPUs, CgroupParent, BlkioWeight, BlkioWeightDevice, BlkioDeviceReadBps, BlkioDeviceWriteBps, BlkioDeviceReadIOps, BlkioDeviceWriteIOps, CPUPeriod, CPUQuota, CPURealtimePeriod, CPURealtimeRuntime, and others.
- Wire JSON fields include CpuCount, CpuPercent, CpuPeriod, CpuQuota, CpuRealtimePeriod, CpuRealtimeRuntime, CpuShares, Dns, DnsOptions, DnsSearch, NanoCpus.
- Source comments highlight: CgroupnsMode represents the cgroup namespace mode of the container Isolation represents the isolation technology of a container. IpcMode represents the container ipc stack.
- Most logic consists of string-mode predicates and validators that preserve Docker API compatibility across Linux and Windows.

## Control Flow
- Runtime behavior is limited to helper methods such as validators, stringers, comparison functions, sort methods, or error adapters.
- Predicate/validation methods compare string modes or enum values against known constants and return booleans or formatted errors.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `errors`, `fmt`, `net/netip`, `strings`, `github.com/docker/go-units`, `github.com/moby/moby/api/types/blkiodev`, `github.com/moby/moby/api/types/mount`, `github.com/moby/moby/api/types/network`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Uses `net/netip` typed IP/prefix values, preserving validated address semantics instead of raw strings.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.
- Address parsing and JSON behavior depend on `netip` semantics; invalid or legacy textual addresses need explicit handling upstream.

## Test Signals
- Adjacent test file `sources/cloud-native/moby/api/types/container/hostconfig_test.go` exercises related behavior.
- Package-level tests include `config_test.go`, `health_test.go`, `hostconfig_test.go`, `hostconfig_unix_test.go`, `state_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/hostconfig.go -->
