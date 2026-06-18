<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/container.go -->
# sources/cloud-native/moby/api/types/container/container.go

## Purpose
PruneReport contains the response for Engine API: POST "/containers/prune"

## Important APIs, Types, And Functions
- Exported types: PruneReport, PathStat, MountPoint, State, Summary, InspectResponse.
- `PruneReport` fields include ContainersDeleted, SpaceReclaimed.
- `PathStat` fields include Name, Size, Mode, Mtime, LinkTarget.
- `MountPoint` fields include Type, Name, Source, Destination, Driver, Mode, RW, Propagation.
- `State` fields include Status, Running, Paused, Restarting, OOMKilled, Dead, Pid, ExitCode, Error, StartedAt, FinishedAt, Health.
- `Summary` fields include ID, Names, Image, ImageID, ImageManifestDescriptor, Command, Created, Ports, SizeRw, SizeRootFs, Labels, State, Status, HostConfig, and others.
- Wire JSON fields include GraphDriver, Id, ImageManifestDescriptor, Storage, linkTarget, mode, mtime, name, size.
- Source comments highlight: PruneReport contains the response for Engine API: POST "/containers/prune" PathStat is used to encode the header from GET "/containers/{name:.*}/archive" "Name" is the file or directory name. MountPoint represents a mount point configuration inside the container.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `os`, `time`, `github.com/moby/moby/api/types/mount`, `github.com/moby/moby/api/types/storage`, `github.com/opencontainers/image-spec/specs-go/v1`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Uses OCI image-spec descriptors/platform structures, so it participates in registry and content-store interoperability.
- Carries timestamp or duration fields that must remain JSON-compatible across daemon/client boundaries.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.
- Duration and timestamp fields need stable units and timezone/zero-value behavior across API versions.

## Test Signals
- Package-level tests include `config_test.go`, `health_test.go`, `hostconfig_test.go`, `hostconfig_unix_test.go`, `state_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/container.go -->
