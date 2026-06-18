# sources/cloud-native/moby/daemon/server/router/volume/volume_routes.go

## Purpose
`volume_routes.go` implements local and swarm cluster-volume API handlers.

## Important APIs, Types, And Functions
Handlers include `getVolumesList`, `getVolumeByName`, `postVolumesCreate`, `putVolumesUpdate`, `deleteVolumes`, and `postVolumesPrune`. `clusterVolumesVersion` is API 1.42.

## Control Flow
List parses filters, queries local volumes, and appends cluster volumes for API 1.42+ managers while converting cluster errors into warnings. Inspect prefers local volumes and falls back to cluster volumes on local not-found for managers. Create chooses cluster creation if `ClusterVolumeSpec` is present and API supports it, otherwise local create. Update requires manager state and parses a swarm object version. Delete first tries local removal, then cluster removal on not-found or force. Prune adds `all=true` before API 1.42 to preserve old behavior.

## State And Persistence
Backends persist volume creation, update, removal, and prune effects. Router mutations are limited to filters/options.

## Dependencies And Integration Points
Depends on containerd errdefs, daemon filters, version helpers, local volume service options, cluster volume backend options, and logging.

## Risks
Local/cluster name duplication and force-delete semantics are subtle. `force` makes local backend suppress not-found, so the router still attempts cluster removal. Manager availability affects cluster volume visibility and errors.

## Test Signals
`volume_routes_test.go` covers local-vs-cluster lookup/list/create/update/remove behavior, manager availability, conflicts, force removal, and fake backend behavior.
