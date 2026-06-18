<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/io-engine-tests-macros/src/lib.rs -->
# sources/control-plane/mayastor/io-engine-tests/io-engine-tests-macros/src/lib.rs

Purpose: Provides the `#[spdk_test]` attribute for tests that need all SPDK work to run on one designated thread while still using Tokio test syntax.

Important APIs/types/functions: `spdk_test(_args, item)` parses the annotated item as `syn::ItemFn`, keeps a clone of the original function, and emits a `#[tokio::test] async fn` with the same identifier. Inside the wrapper it defines the original function, then calls `io_engine_tests::test_task::run_single_thread_test_task(|| { #fn_ident(); }).await`.

Control flow: Cargo sees the wrapper as the test entry point. The original async function becomes a nested item and is invoked through the test-task executor; the single-thread executor serializes these tests through a channel.

State and dependencies: depends on downstream `tokio` and `io_engine_tests::test_task`. It does not use macro args.

Risks and test signals: the macro assumes the annotated function shape can be called as `#fn_ident()` inside a sync closure; it is intended for async Tokio tests but the generated closure does not explicitly await the nested function. Any change to `test_task` or async handling should be verified with a real annotated SPDK test.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine-tests/io-engine-tests-macros/src/lib.rs -->
