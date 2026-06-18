<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/container_wait_example_test.go -->
# sources/cloud-native/moby/client/container_wait_example_test.go

Purpose: documents using `ContainerWait` with a timeout context.

Important APIs/functions: the example calls `ContainerWait`, then selects between `Result`, `Error`, and context cancellation paths.

Control flow and dependencies: demonstrates channel-based consumption and context timeout integration.

State and risks: no persistent state. The compile-time example protects the public channel result API and shows callers must handle both channels.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/container_wait_example_test.go -->
