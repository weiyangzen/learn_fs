<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/cri_server_fuzz_test.go -->
# sources/cloud-native/containerd/contrib/fuzz/cri_server_fuzz_test.go

## Purpose
Fuzzes CRI runtime and image service API sequences against a local containerd daemon.

## Important APIs, Types, And Functions
Defines `FuzzCRIServer`, fake runtime service, service registration, execution logging, dispatcher `fuzzCRI`, and per-CRI-method fuzz wrappers.

## Control Flow
Requires root, starts daemon once, constructs CRI image/runtime services, chooses up to 40 random operations, generates request structs, invokes methods, and logs execution order on panic.

## State And Persistence
Mutates the fuzz daemon, image store, pods/containers/sandboxes depending on generated calls.

## Dependencies And Integration Points
containerd client/CRI server, Kubernetes CRI API, grpc instrumentation, go-fuzz-headers, daemon helper.

## Risks And Test Signals
Root/environment-heavy and broad stateful fuzzing; errors are mostly ignored to find panics. Strong crash signal but not deterministic semantics. Source size reviewed: 470 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/fuzz/cri_server_fuzz_test.go -->
