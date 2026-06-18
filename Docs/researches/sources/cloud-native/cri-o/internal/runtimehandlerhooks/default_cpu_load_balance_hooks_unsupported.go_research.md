# sources/cloud-native/cri-o/internal/runtimehandlerhooks/default_cpu_load_balance_hooks_unsupported.go

Purpose: non-Linux no-op implementation of default CPU-load-balance hooks.

Important APIs/types/functions: empty `DefaultCPULoadBalanceHooks` and no-op lifecycle methods.

Control flow: every method returns nil.

State and persistence behavior: no state and no filesystem/cgroup writes.

Dependencies and integration points: selected by `//go:build !linux` so callers can compile against the same interface on unsupported platforms.

Risks: behavior differs from Linux intentionally; tests on non-Linux cannot validate cgroup behavior.

Test signals: compile-time platform coverage is the main signal.
