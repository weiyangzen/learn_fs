<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_pause_test.go -->
# sources/cloud-native/moby/client/container_pause_test.go

Purpose: tests `ContainerPause` error mapping and route construction.

Important coverage: daemon internal error, invalid empty/whitespace ids, and successful `POST /containers/container_id/pause`.

Control flow and dependencies: uses mock client helpers and gotest assertions.

State and risks: no persistence. The test protects lifecycle endpoint method/path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_pause_test.go -->
