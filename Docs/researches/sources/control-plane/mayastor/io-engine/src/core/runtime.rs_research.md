# sources/control-plane/mayastor/io-engine/src/core/runtime.rs

## Purpose
Provides a small global Tokio multi-threaded runtime helper for background tasks that do not need to run on SPDK reactors.

## Important APIs, Types, and Functions
- `spawn(f)` submits a `Send + 'static` future and detaches it.
- `spawn_await(f)` submits and awaits completion.
- `block_on(f)` runs a future to completion on the global runtime.
- `spawn_blocking(f)` delegates blocking work to Tokio.
- `Runtime` wraps `tokio::runtime::Runtime`.

## Control Flow and State
`RUNTIME` is lazily created with `Builder::new_multi_thread().enable_all()`. Helper functions call through to that singleton. The runtime exists for process lifetime and is separate from the current-thread runtime used in `MayastorEnvironment::start`.

State is the Tokio runtime and its task queues. No persistence exists.

## Dependencies and Integration Points
Used by io-engine modules that need generic Tokio execution. Coexists with SPDK reactor-local future execution, so callers must choose the correct runtime based on SPDK thread affinity.

## Risks and Test Signals
Tasks spawned here must be `Send` and must not directly use SPDK APIs requiring current SPDK thread context. `spawn_await` awaits a join handle and ignores panics only through unwrap semantics? It awaits with `let _ =`, so panic results are dropped. Tests should cover runtime initialization, spawn completion, blocking task execution, and absence of reactor-affine calls in runtime tasks.
