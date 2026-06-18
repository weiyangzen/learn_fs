# sources/cloud-native/cri-o/internal/runtimehandlerhooks/runtime_handler_hooks_linux.go

Purpose: Linux hook retriever implementation selecting high-performance, default CPU-load-balance, and GOMAXPROCS hooks from runtime config and sandbox annotations.

Important APIs/types/functions: `NewHooksRetriever`, `Get`, `highPerformanceAnnotationsSpecified`, and `cpuLoadBalancingAllowed`.

Control flow: constructor logs deprecation warnings for high-performance handlers lacking allowed annotations. `Get` selects high-performance hooks if runtime name contains `high-performance` or sandbox has high-performance annotations; otherwise selects default CPU-load-balance hooks if the annotation is allowed anywhere. It appends GOMAXPROCS hooks when configured and returns nil, one hook, or `CompositeHooks`.

State and persistence behavior: caches one `HighPerformanceHooks` instance per retriever and uses package-global once-cached CPU-load-balancing allowance.

Dependencies and integration points: reads CRI-O runtime/workload config, annotation constants, cgroup manager config, IRQ balance path, shared CPU set, exec CPU affinity, and host sysfs/proc defaults.

Risks: `strings.Contains` runtime-name matching can include unintended names. Global `cpuLoadBalancingAllowedAnywhere` may become stale across config reloads unless process/tests reset it. Missing runtime config for a selected high-performance runtime logs an error and returns nil.

Test signals: high-performance tests cover high-performance name, arbitrary runtime with allowed annotations, default runtime with annotations, default CPU-load-balance selection, and nil hook cases.
