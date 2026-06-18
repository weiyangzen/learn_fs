<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_restart.go -->
# sources/cloud-native/moby/client/container_restart.go

Purpose: restarts a container with optional signal and timeout controls.

Important APIs/types/functions: `ContainerRestartOptions` with signal and timeout-style fields, `ContainerRestartResult`, and `Client.ContainerRestart`.

Control flow: validates container id, maps non-default options to query values, posts to `/containers/{id}/restart`, closes the response, and returns an empty result.

State and integration behavior: no local persistence; daemon stops and starts container process state. Depends on shared lifecycle request helpers.

Risks and test signals: risks are timeout encoding and connection failure classification during lifecycle changes. `container_restart_test.go` covers internal errors, connection errors, route, and query behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_restart.go -->
