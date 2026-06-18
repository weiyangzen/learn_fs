<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_pause.go -->
# sources/cloud-native/moby/client/container_pause.go

Purpose: pauses a running container.

Important APIs/types/functions: `ContainerPauseOptions`, `ContainerPauseResult`, and `Client.ContainerPause`.

Control flow: validates container id, posts to `/containers/{id}/pause`, closes the response, and returns an empty result.

State and integration behavior: no local persistence; daemon mutates container cgroup/process state. Depends on shared id validation and `post`.

Risks and test signals: destructive lifecycle route must remain stable. `container_pause_test.go` covers daemon errors, invalid ids, and method/path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_pause.go -->
