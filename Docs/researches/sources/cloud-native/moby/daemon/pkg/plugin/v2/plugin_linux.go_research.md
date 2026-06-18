<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/v2/plugin_linux.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/v2/plugin_linux.go

## Purpose
Builds an OCI runtime spec for a managed plugin on Linux.

## Important APIs, Types, And Functions
`Plugin.InitSpec(execRoot string)` is the exported behavior. It uses `oci.DefaultSpec`, `oci.RemoveNamespace`, `oci.DevicesFromPath`, rootless mount option helpers, and optional runtime spec modifiers.

## Control Flow
The function sets rootfs, prepares plugin runtime bind mounts, handles propagated mount storage, applies host network/PID/IPC namespace requests, adds configured mounts and devices, removes default `/dev` mounts overridden by user mounts, builds env and process args, adds Linux capabilities, applies spec modifiers, and adjusts bind mount flags/rootless spec conversion when running in user namespaces.

## State, Dependencies, And Integration Points
Creates the plugin exec root directory and returns an in-memory spec. It depends on rootless detection, mount flag introspection, OCI helpers, and plugin settings from `PluginObj`.

## Risks And Test Signals
Mount source nil values error out. Device paths are dereferenced and must be present. User-namespace mount flags are subtle. Linux manager tests exercise spec use indirectly.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/v2/plugin_linux.go -->
