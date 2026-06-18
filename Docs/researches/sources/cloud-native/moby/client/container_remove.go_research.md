<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_remove.go -->
# sources/cloud-native/moby/client/container_remove.go

Purpose: removes a container with optional volume, force, and link flags.

Important APIs/types/functions: `ContainerRemoveOptions{RemoveVolumes, RemoveLinks, Force bool}`, `ContainerRemoveResult`, and `Client.ContainerRemove`.

Control flow: validates container id, maps options to query keys `v`, `link`, and `force`, issues `DELETE /containers/{id}`, closes the response, and returns an empty result.

State and integration behavior: no local persistence; daemon deletes container state and optionally volumes/links. Depends on shared request helpers and id validation.

Risks and test signals: destructive route; option query names are terse and easy to regress. `container_remove_test.go` covers internal errors, not found, invalid ids, route, and option query behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_remove.go -->
