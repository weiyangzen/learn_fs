<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_restart_test.go -->
# sources/cloud-native/moby/client/container_restart_test.go

Purpose: validates `ContainerRestart` error handling, connection failure behavior, and route construction.

Important coverage: internal daemon errors, transport connection errors classified through `IsErrConnectionFailed`, invalid ids, successful `POST /containers/container_id/restart`, and timeout/signal query expectations.

Control flow and dependencies: uses both mock response and failing transport scenarios.

State and risks: no persistence. The test protects lifecycle behavior and shared connection-failure wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_restart_test.go -->
