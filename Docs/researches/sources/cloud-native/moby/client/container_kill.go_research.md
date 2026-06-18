<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_kill.go -->
# sources/cloud-native/moby/client/container_kill.go

Purpose: sends a signal to terminate or stop a container process.

Important APIs/types/functions: `ContainerKillOptions{Signal string}`, `ContainerKillResult`, and `Client.ContainerKill`.

Control flow: validates container id, optionally sets `signal=<Signal>`, posts to `/containers/{id}/kill`, closes the response, and returns an empty result.

State and integration behavior: no local persistence; daemon mutates container process state. Depends on shared `post`, id validation, and query encoding.

Risks and test signals: risks are signal query naming and destructive lifecycle route drift. `container_kill_test.go` covers daemon errors, invalid ids, and successful route/query behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_kill.go -->
