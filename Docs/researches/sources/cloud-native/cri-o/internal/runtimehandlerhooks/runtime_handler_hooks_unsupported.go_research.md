# sources/cloud-native/cri-o/internal/runtimehandlerhooks/runtime_handler_hooks_unsupported.go

Purpose: non-Linux runtime hook retriever implementation.

Important APIs/types/functions: `IrqSmpAffinityProcFile`, `NewHooksRetriever`, `HooksRetriever.Get`, and `RestoreIrqBalanceConfig`.

Control flow: constructor stores config. `Get` always returns a `DefaultCPULoadBalanceHooks` instance. `RestoreIrqBalanceConfig` is a no-op.

State and persistence behavior: no host tuning or persistence on unsupported platforms.

Dependencies and integration points: compiles the runtime hook interface for non-Linux builds and uses CRI-O logging span setup.

Risks: always returning a default hook differs from Linux's nil/no-op decisions, but that hook is itself no-op on unsupported platforms.

Test signals: compile-time platform coverage; no local non-Linux behavior tests in this subset.
