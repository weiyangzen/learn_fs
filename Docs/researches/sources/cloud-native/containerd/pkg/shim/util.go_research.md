<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util.go -->
# sources/cloud-native/containerd/pkg/shim/util.go

## Purpose
Daemon-side and shared shim utility functions for launching shim binaries, resolving binary names, reading address/options files, and composing ttrpc interceptors.

## Important APIs, Types, And Functions
CommandConfig, Command, BinaryName, BinaryPath, Connect, WritePidFile, ReadAddress, ReadRuntimeOptions, and chainUnaryServerInterceptors are key APIs.

## Control Flow
Command builds legacy flags/env for all shims and sends either legacy options for v1 shim names or new BootstrapParams on stdin for start. Utilities atomically write pid files, read address files, unmarshal Any runtime options, and wrap interceptors from first to last.

## State And Persistence
Writes pid files atomically and reads address files. Command mutates only exec.Cmd fields. Runtime options are read fully from an io.Reader.

## Dependencies And Integration Points
Integrates namespaces, bootapi, protobuf/typeurl, atomicfile, errdefs, log, ttrpc, and version metadata.

## Risks And Edge Cases
Command has compatibility branches based on binary basename; incorrect Action is rejected. ReadRuntimeOptions requires registered typeurl types. Interceptor chaining order is subtle and tested.

## Test Signals
util_test.go covers interceptor order, context propagation, and unmarshaler wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/shim/util.go -->
