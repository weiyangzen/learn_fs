# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_cpu_info.h

Purpose: declares the CPU matching helper used by i915 workaround code.

Important APIs/functions: exposes `bool intel_match_g8_cpu(void)`.

Control flow: callers treat the helper as a simple predicate and remain independent from x86 CPU header naming.

State and persistence: none.

Dependencies and integration: includes only `linux/types.h`, making it safe for broad driver inclusion. The implementation handles architecture-specific details.

Risks: the minimal API is easy to use, but its meaning is tied to the implementation's CPU table; callers should document the specific workaround context.

Test signals: compile coverage and whichever platform workaround path consumes the predicate.
