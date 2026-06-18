# sources/control-plane/longhorn-engine/app/cmd/profiler.go

## Purpose
Defines `profiler show|enable|disable` commands to control the engine process profiler through gRPC.

## Important APIs, Types, and Functions
- Constants `opShow`, `opEnable`, `opDisable`, and `profilerPortBase`.
- `ProfilerCmd()` and subcommand constructors.
- `getProfilerClient()` creates a `go-common-libs/profiler.Client` with identity validation interceptor.
- `showProfiler()`, `enableProfiler()`, `disableProfiler()` call `Client.ProfilerOP`.
- `validatePortNumber()` rejects explicit ports between 1 and 29999.

## Control Flow
`enableProfiler` validates a user-supplied port; if unset, it parses the controller gRPC port from `--url` and adds 20001 to avoid Longhorn reserved ranges. Each operation creates a profiler client, calls the operation with a port argument as needed, prints the result, and closes the client.

## State and Persistence Behavior
No on-disk state. It toggles runtime profiler server state inside the target engine process. The chosen port becomes active process state until disabled or process exit.

## Dependencies and Integration Points
Uses `go-common-libs/profiler`, gRPC dial options, and `pkg/interceptor.WithIdentityValidationClientInterceptor` with global volume/instance identity flags.

## Risks and Edge Cases
Default port derivation assumes `--url` is `host:port` and uses `strings.Split(grpcURL, ":")[1]`, which can fail for unusual address forms. Validation permits port 0 as auto mode and ports above 30000 but does not check upper TCP port bounds.

## Test Signals
No direct tests in the listed files. Identity behavior is analogous to `test_identity.py`, but profiler-specific enable/show/disable output is not covered here.
