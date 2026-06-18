## sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/test_utils_pub.rs

Purpose: this hidden public module provides test helpers that require unsafe code, especially for fork/exec scenarios where tests need a process to pause between fork and exec.

Important APIs: `CommandExt` defines `pre_exec_sleep(&mut self, delay: Duration) -> &mut Self`. The implementation for `std::process::Command` calls Unix `CommandExt::pre_exec` and sleeps in the callback before returning `Ok(())`.

Control flow: callers build a `Command`, invoke `pre_exec_sleep`, and then spawn/exec normally. In the child process after fork and before exec, the callback sleeps for the requested duration. The method returns `&mut Self` for builder chaining.

State and persistence: no persistent state. The only side effect is delaying the child process during the unsafe pre-exec window, useful for tests that need fd races or lifetime timing.

Dependencies and integration: depends on `std::os::unix::process::CommandExt`, `std::process::Command`, and `Duration`. It is exported as `#[doc(hidden)]` by the crate root so other crate tests can reuse it while production APIs stay focused.

Risks: `pre_exec` callbacks run in a restricted post-fork context where many operations are unsafe in multi-threaded programs. Sleeping is intentionally simple, but this helper should remain test-only. Non-Unix targets are not supported because the module imports Unix process extensions.

Test signals: there are no tests in this file; its correctness is exercised indirectly by tests that need fork timing.
