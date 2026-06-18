<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_start.go -->
# sources/cloud-native/moby/client/container_start.go

Purpose: starts a stopped or created container.

Important APIs/types/functions: `ContainerStartOptions`, `ContainerStartResult`, and `Client.ContainerStart`.

Control flow: validates container id, posts to `/containers/{id}/start`, closes the response, and returns an empty result.

State and integration behavior: no local persistence; daemon mutates container lifecycle state. Depends on shared `post` and id validation.

Risks and test signals: route drift is the main risk. `container_start_test.go` covers internal errors, invalid ids, and successful method/path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_start.go -->
