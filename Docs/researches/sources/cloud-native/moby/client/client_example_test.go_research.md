<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/client_example_test.go -->
# sources/cloud-native/moby/client/client_example_test.go

Purpose: provides a package example showing how consumers create a client with environment-derived options and list containers. It documents the intended public API shape more than it validates daemon behavior.

Important APIs/functions: `Example` uses `client.New(client.FromEnv)`, `ContainerList`, `ContainerListOptions{All: true}`, and iterates over `ContainerListResult.Items`.

Control flow and integration: the example creates a context, constructs an API client, calls the container list endpoint, and prints selected fields. It integrates with the package doc in `client.go` and with `go test` example compilation.

State, risks, and test signals: no persistent state; network behavior is illustrative and not expected to run against a real daemon in normal unit tests. The signal is compile-time API usability: if names or return shapes change, the example fails to build.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/client_example_test.go -->
