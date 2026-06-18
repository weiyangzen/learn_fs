# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_request.h

Purpose: declares mock request creation and cancellation helpers.

Important APIs: `mock_request(struct intel_context *ce, unsigned long delay)` and `mock_cancel_request(struct i915_request *request)`.

Control flow and state: callers create a mock request tied to an Intel context and optional delay, then may cancel it if it remains queued.

Dependencies and integration: includes i915 request definitions and Linux list support. Implementation integrates with mock engine structures.

Risks: helpers are mock-only; tests must not pass requests from real engines to `mock_cancel_request()`.

Test signals: compile use by scheduler and mock engine tests, plus expected boolean return from cancellation paths.
