# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_execlists_submission.h

## Purpose
This header exposes the execlists submission backend interface for engine setup and debug reporting.

## Important APIs, Types, and Functions
It defines context-status notifier values `INTEL_CONTEXT_SCHEDULE_IN`, `INTEL_CONTEXT_SCHEDULE_OUT`, and `INTEL_CONTEXT_SCHEDULE_PREEMPTED`. It declares `intel_execlists_submission_setup()`, `intel_execlists_show_requests()`, `intel_execlists_dump_active_requests()`, and `intel_engine_in_execlists_submission_mode()`.

## Control Flow
There is no in-header flow. Engine initialization calls setup to install execlists callbacks. Debug/error reporting paths call the request display helpers. Backend checks can use `intel_engine_in_execlists_submission_mode()`.

## State and Persistence Behavior
The header owns no state. Its declarations operate on persistent `intel_engine_cs` and request state defined in other headers and implemented in `intel_execlists_submission.c`.

## Dependencies and Integration Points
It connects engine setup, debugfs/error-state dumping, GVT/context-status notifiers, and code that needs to distinguish execlists from other submission backends.

## Risks
The notifier enum values are consumed by context-status callbacks and must stay semantically stable. Exposing too much of the backend would make replacing execlists harder; the current header keeps the public surface narrow.

## Test Signals
Build coverage, successful engine setup, correct debug request dumps, and context-status notifier behavior under GVT/selftests are the primary signals.
