<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_logs_example_test.go -->
# sources/cloud-native/moby/client/container_logs_example_test.go

Purpose: documents example usage for `Client.ContainerLogs`.

Important APIs/functions: the example calls `ContainerLogs` with output options, defers `Close`, and reads or copies the returned stream.

Control flow and dependencies: it demonstrates caller-owned stream lifecycle and integration with standard `io` helpers.

State and risks: no persistent state. The compile-time example protects public API usability and reinforces the need to close log streams.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_logs_example_test.go -->
