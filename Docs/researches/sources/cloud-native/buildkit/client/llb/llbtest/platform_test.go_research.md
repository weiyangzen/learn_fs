# sources/cloud-native/buildkit/client/llb/llbtest/platform_test.go

Purpose: tests platform propagation through LLB source, exec, file, merge, mount, and marshal-capability paths by loading definitions through the solver.

Important APIs/types/functions: `TestCustomPlatform`, `TestDefaultPlatform`, `TestPlatformOnMarshal`, `TestPlatformMixed`, and `TestFallbackPath`. Helpers inspect solver edges, protobuf ops, parent edges, mount edges, source IDs, exec args, and environment variables.

Control flow: tests build LLB graphs with explicit per-state platforms, default platforms, marshal-time platforms, mixed-platform mounts, and cap-dependent PATH behavior; marshal definitions; load them with `llbsolver.Load`; traverse loaded solver edges; assert platform and metadata results.

State and persistence: in-memory definitions and solver edge graphs only.

Dependencies/integration points: `llbsolver.Load`, solver edges, `containerd/platforms`, `system.DefaultPathEnvUnix`, exec PATH cap negotiation in `exec.go`, and platform propagation in `state.go`/`source.go`.

Risks/test signals: strong signal for cross-platform graph correctness and default PATH compatibility. It does not execute the graph, but validates solver interpretation of marshaled definitions.
