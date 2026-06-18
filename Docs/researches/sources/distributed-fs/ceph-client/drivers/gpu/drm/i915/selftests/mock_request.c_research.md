# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_request.c

Purpose: creates and cancels mock i915 requests for GT scheduler/engine selftests.

Important APIs/functions: `mock_request(struct intel_context *ce, unsigned long delay)` creates a request through `intel_context_create_request()` and stores a mock delay. `mock_cancel_request(struct i915_request *request)` removes a queued request from the mock engine link list under `engine->hw_lock` and calls `i915_request_unsubmit()` when it had been queued.

Control flow and state: request creation relies on the enlarged i915 request slab to include mock request fields. Cancellation derives `struct mock_engine` from `request->engine`, removes `request->mock.link`, and returns whether the request was actually queued.

Dependencies and integration: depends on GT mock engine internals, GEM test utilities, and i915 request/context APIs. Used by selftests that model delayed execution or cancellation without real hardware.

Risks: cancellation assumes the request belongs to a mock engine. Using it on a real engine would make the `container_of()` invalid. Locking must match mock engine queue manipulation.

Test signals: scheduler tests can enqueue mock requests, cancel them, and observe unsubmit behavior and queue removal under lock.
