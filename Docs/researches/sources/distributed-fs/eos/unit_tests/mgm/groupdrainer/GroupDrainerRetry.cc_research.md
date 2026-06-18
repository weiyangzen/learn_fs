# sources/distributed-fs/eos/unit_tests/mgm/groupdrainer/GroupDrainerRetry.cc

## sources/distributed-fs/eos/unit_tests/mgm/groupdrainer/GroupDrainerRetry.cc

Purpose: tests `RetryTracker`, the small timing helper used to decide when a group-drainer retry/update should run.

Important APIs and types: `RetryTracker`, fields `count` and `last_run_time`, methods `need_update()` and `update()`, and `eos::common::SteadyClock` test clock.

Control flow: verifies the initial tracker needs an update, `update()` increments count and sets time, a fresh tracker does not need another update before the retry interval, and a manually advanced test clock beyond 900 seconds permits update.

State and persistence: state is local to `RetryTracker` fields. Time can be read from real steady clock or injected test clock.

Dependencies and integration: guards retry throttling for group drainer workflows. Correct behavior avoids excessive retries while ensuring stalled drains can be revisited.

Risks and test signals: mixed use of real `std::chrono::steady_clock::now()` and test clock requires careful interpretation. Time-dependent code can become flaky if the clock abstraction changes.
