<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_exec_test.go -->
# sources/cloud-native/moby/client/container_exec_test.go

Purpose: tests exec create, start, attach-related request construction, console-size validation, and inspect behavior.

Important coverage: daemon and connection errors, invalid container id for create, successful `POST /containers/{id}/exec`, `POST /exec/{id}/start`, terminal size encoding when TTY is enabled, rejection of console size without TTY, and `GET /exec/{id}/json` decoding.

Control flow and dependencies: mock callbacks inspect requests and JSON bodies. Tests depend on container API types and package mock helpers.

State and risks: no persistent state. This suite is important because exec uses both JSON request/response paths and hijacked stream semantics.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_exec_test.go -->
