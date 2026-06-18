<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_prune.go -->
# sources/cloud-native/moby/client/container_prune.go

Purpose: prunes stopped containers using optional filters.

Important APIs/types/functions: `ContainerPruneOptions{Filters Filters}`, `ContainerPruneResult{ContainersDeleted []string, SpaceReclaimed uint64}`, and `Client.ContainerPrune`.

Control flow: encodes filters into query values, posts to `/containers/prune`, closes response, decodes `container.PruneReport`, and maps deleted IDs plus reclaimed bytes into the result.

State and integration behavior: no local persistence; daemon deletes container resources. Depends on shared filter helper, JSON decoding, and container prune API types.

Risks and test signals: destructive operation; filter encoding must be exact. `container_prune_test.go` covers internal errors, route, filter query combinations such as dangling/until/label, and decoded results.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_prune.go -->
