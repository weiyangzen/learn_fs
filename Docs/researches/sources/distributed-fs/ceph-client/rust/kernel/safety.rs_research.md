## sources/distributed-fs/ceph-client/rust/kernel/safety.rs

Purpose: provides `unsafe_precondition_assert!`, a macro for documenting and optionally checking unsafe-function preconditions in debug Rust kernel builds.

Important APIs/types/functions: the exported macro accepts either a condition alone or a condition plus formatted message. Both forms route to an internal arm that calls `core::debug_assert!` with a standardized "unsafe precondition violated" prefix.

Control flow: the macro expands at call sites. With debug assertions enabled it evaluates the condition and panics on violation; otherwise it compiles to the normal `debug_assert!` no-op behavior.

State/persistence: no runtime state and no persistence. It only affects debug-time checks.

Dependencies/integration: uses the kernel prelude formatting macro for message construction and integrates with unsafe APIs as a lightweight guardrail in debug builds.

Risks: it is not a safety mechanism in production configurations where debug assertions are disabled. Callers must still uphold the unsafe contract. Format arguments should avoid side effects because they may not be evaluated in release-like builds.

Test signals: doctest demonstrates guarding an unchecked buffer write. Broader signal comes from compiling unsafe APIs under `CONFIG_RUST_DEBUG_ASSERTIONS` and inducing violations in KUnit or debug-only tests.
