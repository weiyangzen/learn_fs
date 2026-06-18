<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/src/main.rs -->
## sources/cloud-native/ostree/tests/bootc-integration/src/main.rs

Purpose: implements the executable custom harness for bootc integration tests using `libtest_mimic`, with optional JUnit XML output.

Important APIs/types/functions: `TestOutcome` records name, duration, and stringified result. `main()` converts each `IntegrationTest` to a `Trial`, records outcomes in `Arc<Mutex<Vec<_>>>`, runs `libtest_mimic`, writes JUnit if `JUNIT_OUTPUT` is set, and exits 101 on failure. `write_junit()` builds a `quick_junit::Report`.

Control flow/state: outcomes are shared across trial closures and accumulated while tests run. JUnit output is post-run best-effort; failure to write XML only warns.

Dependencies/integration: integrates `INTEGRATION_TESTS` from the library, the `tests` module tree, CLI args accepted by `libtest_mimic`, and CI systems consuming JUnit.

Risks/test signals: mutex poisoning is unhandled via `unwrap()`. Parallel execution ordering can affect outcome order. Exit code and XML failures/successes are the main signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/bootc-integration/src/main.rs -->
