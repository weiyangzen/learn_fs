<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_unpause.go -->
# sources/cloud-native/moby/client/container_unpause.go

Purpose: unpauses a paused container.

Important APIs/types/functions: `ContainerUnpauseOptions`, `ContainerUnpauseResult`, and `Client.ContainerUnpause`.

Control flow: validates container id, posts to `/containers/{id}/unpause`, closes the response, and returns an empty result.

State and integration behavior: no local persistence; daemon mutates lifecycle/cgroup state. Depends on shared post/id helpers.

Risks and test signals: lifecycle route drift is the main risk. `container_unpause_test.go` covers errors, invalid ids, and successful method/path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_unpause.go -->
