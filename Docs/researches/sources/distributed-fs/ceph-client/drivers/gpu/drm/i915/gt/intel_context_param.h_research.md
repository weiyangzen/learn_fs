<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context_param.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context_param.h

## Purpose
`intel_context_param.h` provides a tiny context-parameter helper for setting the per-context watchdog timeout.

## Important APIs, Types, and Functions
The only helper is `intel_context_set_watchdog_us(struct intel_context *ce, u64 timeout_us)`, which stores the timeout in `ce->watchdog.timeout_us`.

## Control Flow
There is no branching. Callers include this header when translating a user or internal context parameter into the context watchdog field.

## State and Persistence
The helper persists the timeout in the context object. Enforcement is elsewhere; this header only sets the stored value.

## Dependencies and Integration Points
It depends on `intel_context.h` and Linux integer types. It integrates with context parameter plumbing and watchdog/hang detection code that later reads `ce->watchdog.timeout_us`.

## Risks and Edge Cases
There is no validation in this helper, so callers must clamp or reject invalid timeout values before calling it. Concurrent updates require external serialization if the field is visible to submission or watchdog code.

## Test Signals
Tests should cover context parameter setting, boundary timeout values, and watchdog behavior that consumes the stored microsecond timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_context_param.h -->
