<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/plugin/plugin.go -->
# sources/cloud-native/moby/api/types/plugin/plugin.go

## Purpose
Plugin A plugin for the Engine API swagger:model Plugin

## Important APIs, Types, And Functions
- Exported types: Plugin, Config, Args, Interface, LinuxConfig, NetworkConfig, RootFS, User, Settings.
- `Plugin` fields include Config, Enabled, ID, Name, PluginReference, Settings.
- `Config` fields include Args, Description, Documentation, Entrypoint, Env, Interface, IpcHost, Linux, Mounts, Network, PidHost, PropagatedMount, User, WorkDir, and others.
- `Args` fields include Description, Name, Settable, Value.
- `Interface` fields include ProtocolScheme, Socket, Types.
- `LinuxConfig` fields include AllowAllDevices, Capabilities, Devices.
- Wire JSON fields include AllowAllDevices, Args, Capabilities, Config, Description, Devices, Documentation, Enabled, Entrypoint, Env, GID, Id, Interface, IpcHost, Linux, Mounts, Name, Network, and others.
- Source comments highlight: Plugin A plugin for the Engine API swagger:model Plugin Config The config of a plugin. Args args swagger:model Args

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.

## Dependencies And Integration Points
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- Package-level tests include `capability_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/plugin/plugin.go -->
