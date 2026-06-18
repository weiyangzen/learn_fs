<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_resize_test.go -->
# sources/cloud-native/moby/client/container_resize_test.go

Purpose: tests resize endpoints for containers and exec sessions.

Important coverage: daemon errors for both APIs, invalid container id, successful `POST /containers/container_id/resize`, successful `POST /exec/exec_id/resize`, and correct `h`/`w` query values.

Control flow and dependencies: shared helper `resizeTransport` inspects requests.

State and risks: no persistence. The suite protects terminal size query compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_resize_test.go -->
