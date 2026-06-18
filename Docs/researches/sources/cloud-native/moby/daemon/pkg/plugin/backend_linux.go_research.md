<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/backend_linux.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/backend_linux.go

## Purpose
Implements the Linux plugin backend exposed to daemon API operations: enable/disable, inspect, privileges, pull, upgrade, list, push, remove, set, and create-from-context.

## Important APIs, Types, And Functions
Key functions include `Disable`, `Enable`, `Inspect`, `computePrivileges`, `Privileges`, `Upgrade`, `Pull`, `List`, `Push`, `buildManifest`, `getManifestDescriptor`, `writeManifest`, `Remove`, `Set`, `CreateFromContext`, `splitConfigRootFSFromTar`, and `atomicRemoveAll`.

## Control Flow
Remote install flows fetch plugin content into the content store, apply rootfs layers to a temp directory, validate required privileges, and create or upgrade an on-disk plugin directory. Push builds or reuses a Docker schema2-style manifest, streams progress, and retries HTTP fallback. Create-from-context splits `config.json` and `rootfs/` from an uploaded tar, stores blobs, writes a manifest, and creates the plugin.

## State, Dependencies, And Integration Points
Persists plugin rootfs/config under manager root and blobs under the content store. It integrates with registry auth/resolvers, daemon filters, progress streams, pubsub events, authorization middleware, containerfs cleanup, and mount unmounting.

## Risks And Test Signals
Privilege validation is central to security. TODOs note incomplete config validation and layer media-type assumptions. Removal uses rename-to-`-removing` for crash recovery. Tests cover atomic removal; broader plugin integration tests cover lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/backend_linux.go -->
