# sources/distributed-fs/ceph-client/tools/testing/selftests/tc-testing/TdcPlugin.py

## Purpose
Defines the base plugin interface for the tc-testing Python runner. Subclasses override lifecycle hooks to prepare suites, cases, command execution, and command rewriting.

## Important APIs, Types, And Functions
Class `TdcPlugin` exposes `pre_suite()`, `post_suite()`, `pre_case()`, `post_case()`, `pre_execute()`, `post_execute()`, `adjust_command()`, `add_args()`, and `check_args()`. It stores `args`, `argparser`, `testcount`, `testlist`, `caseinfo`, and `test_skip` as shared plugin state.

## Control Flow
The runner calls hooks around suite start/end, each case, and each command stage. The base implementation mostly records state and emits verbose traces. `adjust_command()` returns the input command unchanged, allowing subclasses to wrap it.

## State And Persistence
State is in the plugin instance for the duration of one runner invocation. It persists parsed arguments and current case metadata.

## Dependencies And Integration Points
Imported by `nsPlugin.py`, `rootPlugin.py`, `scapyPlugin.py`, and `valgrindPlugin.py`. It assumes subclasses set `self.sub_class` before invoking the base constructor.

## Risks
If a subclass does not set `sub_class`, base logging can raise an attribute error during construction. The base `check_args()` must be called by subclasses that rely on `self.args`.

## Test Signals
Verbose runner output showing hook order and successful plugin command adjustments without changing commands in the base class.
