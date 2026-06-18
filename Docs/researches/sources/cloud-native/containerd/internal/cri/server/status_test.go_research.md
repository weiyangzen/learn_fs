# Research: sources/cloud-native/containerd/internal/cri/server/status_test.go

This test file covers two pieces of `status.go`: deprecation-warning condition construction and stable runtime-handler ordering. `TestRuntimeConditionContainerdHasNoDeprecationWarnings` builds one introspection deprecation warning and verifies the condition becomes false with the expected type, reason, and JSON message when not ignored, then true when the warning ID appears in the ignore list.

The rest of the file creates a fake introspection service and injects it into a private field of `containerd.Client` using reflection and unsafe pointers. This avoids a live gRPC connection while allowing `criService.Status` to call `client.IntrospectionService().Server`. `newStatusTestCRIService` returns a minimal service with that fake client and an empty runtime handler map.

`TestStatusRuntimeHandlersOrdering` creates 100 random runtime handlers, calls `Status` twice, and asserts the returned handler names stay in the same order. This specifically protects the sort added over map-derived values. Risks covered include nondeterministic map iteration leaking into CRI responses and deprecation ignore handling. Gaps include network-ready condition behavior, verbose info content, CNI config serialization, and introspection errors.
