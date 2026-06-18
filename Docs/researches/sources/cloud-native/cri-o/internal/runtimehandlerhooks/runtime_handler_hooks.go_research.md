# sources/cloud-native/cri-o/internal/runtimehandlerhooks/runtime_handler_hooks.go

Purpose: declares the runtime handler hook interfaces and retriever state shared across platform implementations.

Important APIs/types/functions: package globals `cpuLoadBalancingAllowedAnywhereOnce` and `cpuLoadBalancingAllowedAnywhere`, `RuntimeHandlerHooks`, `HighPerformanceHook`, and `HooksRetriever`.

Control flow: no executable hook selection here; it defines the lifecycle interface that platform files implement.

State and persistence behavior: contains process-local cached global state for whether CPU load balancing is allowed anywhere, plus retriever fields for config and cached high-performance hook instance.

Dependencies and integration points: imports runtime-tools generator, sandbox, OCI container, and CRI-O config. Used by runtime code that invokes pre-create/pre-start/pre-stop/post-stop hooks.

Risks: `sync.Once` cache is global, so tests and config reload behavior must reset or account for it. Interface duplication is intentional but can drift from callers if lifecycle signatures change.

Test signals: hook selection tests reset the once value to simulate CRI-O restart/config changes.
