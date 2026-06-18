<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_stop.go -->
# sources/cloud-native/moby/client/container_stop.go

Purpose: stops a running container with optional signal and timeout controls.

Important APIs/types/functions: `ContainerStopOptions`, `ContainerStopResult`, and `Client.ContainerStop`.

Control flow: validates container id, encodes signal/timeout query fields when present, posts to `/containers/{id}/stop`, closes the response, and returns an empty result.

State and integration behavior: no local persistence; daemon changes container lifecycle state. Depends on shared post/id helpers.

Risks and test signals: risks are timeout/signal query compatibility and connection failure mapping. `container_stop_test.go` covers daemon errors, transport connection errors, route, and query behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_stop.go -->
