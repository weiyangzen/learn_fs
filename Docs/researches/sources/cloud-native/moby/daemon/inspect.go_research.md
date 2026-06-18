<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/inspect.go -->
# sources/cloud-native/moby/daemon/inspect.go

Purpose: implements container and exec inspect responses.

Important APIs and control flow: `ContainerInspect` resolves the container, builds base inspect data, and optionally adds size information outside the container lock. `containerInspect` locks the container, calls `getInspectData`, and fills graphdriver metadata for non-snapshotter containers, tolerating missing metadata for dead containers. `getInspectData` copies host config, legacy links, ulimits, health state, ports, endpoint settings, mount points, image manifest descriptor, and either snapshotter storage or graphdriver name. `ContainerExecInspect` returns exec process state, process config, IO flags, pid, and removal state.

State and persistence: reads container state, host config, network settings, link index, RW layer metadata, image service layer sizes, and exec store. It does not mutate persisted state.

Dependencies and integration: backs API inspect endpoints and integrates daemon container store, config, network endpoint settings, storage driver metadata, snapshotter mode, and exec command store.

Risks: shallow copying host config plus selective deep copies requires care to avoid races. Size calculation is intentionally outside the lock. Missing RW layers are fatal for live non-snapshotter containers but tolerated for dead containers.

Test signals: `inspect_test.go` covers basic `getInspectData` success and dead-container RW-layer tolerance/error behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/inspect.go -->
