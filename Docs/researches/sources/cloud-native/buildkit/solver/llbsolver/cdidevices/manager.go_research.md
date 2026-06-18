<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/manager.go -->
## sources/cloud-native/buildkit/solver/llbsolver/cdidevices/manager.go

Purpose: manages Container Device Interface devices for BuildKit, including listing, auto-allow evaluation, name/class resolution, OCI spec injection, cache refresh, and on-demand device installers.

Important APIs and types: `Setup`, global `Register`, `Device`, `Manager`, `NewManager`, `ListDevices`, `GetDevice`, `Refresh`, `InjectDevices`, `FindDevices`, `OnDemandInstaller`, plus helpers `parseDevice`, `isAutoAllowed`, `hasDevice`, `deviceAnnotations`, and `dedupSlice`.

Control flow: `FindDevices` lists current CDI devices, parses each requested `pb.CDIDevice`, resolves qualified names by exact/first/wildcard kind, falls back to BuildKit class annotations when the qualifier is invalid or no device matched, and errors for missing non-optional devices. `InjectDevices` resolves then delegates to CDI cache injection. `ListDevices` annotates registered devices and adds validated on-demand installer kinds not already present. `OnDemandInstaller` serializes setup by kind with a locker, validates preconditions, runs installer, refreshes cache, and auto-allows the kind.

State and persistence: manager keeps a CDI cache pointer, per-kind locker, and in-memory `autoAllowed` set. On-demand auto-allow is not persisted and has a TODO to encode it as annotation.

Dependencies and integration: integrates with `tags.cncf.io/container-device-interface`, BuildKit protobuf CDI requests, OCI runtime specs, and worker entitlement checks.

Risks and test signals: risks include global installer mutation, non-persistent auto-allow, class annotation collisions, and optional device warning-only behavior. `manager_test.go` covers exact, first, wildcard, class, and missing required devices.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/cdidevices/manager.go -->
