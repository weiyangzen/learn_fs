<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_kill_test.go -->
# sources/cloud-native/moby/client/container_kill_test.go

Purpose: validates `ContainerKill` error mapping and request construction.

Important coverage: daemon internal errors, invalid empty/whitespace ids, expected `POST /containers/container_id/kill`, and optional signal query.

Control flow and dependencies: mock callbacks inspect requests and return empty responses.

State and risks: no persistent state. The test is important because this is a destructive lifecycle operation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_kill_test.go -->
