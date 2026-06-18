# sources/cloud-native/cri-o/internal/runtimehandlerhooks/composite_hooks.go

Purpose: adapts multiple runtime handler hooks into one `RuntimeHandlerHooks` implementation.

Important APIs/types/functions: `CompositeHooks` and methods `PreCreate`, `PreStart`, `PreStop`, and `PostStop`.

Control flow: each lifecycle method iterates hooks in configured order and stops immediately on the first error.

State and persistence behavior: stores only an ordered slice of hook implementations; no persistence.

Dependencies and integration points: used by `HooksRetriever.Get` when high-performance/default CPU-load-balance behavior and GOMAXPROCS injection both apply. It passes through OCI generator, sandbox, and container pointers.

Risks: hook ordering is semantically important. A failing earlier hook prevents later hooks from running, which can skip compensating behavior.

Test signals: no direct file-local tests, but hook retriever and GOMAXPROCS/high-performance tests exercise composed behavior indirectly.
