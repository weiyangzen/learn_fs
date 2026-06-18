<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_llc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_llc.h

Purpose: exposes the minimal LLC programming interface to GT initialization and teardown code.

Important APIs: `intel_llc_enable(struct intel_llc *llc)` programs the hardware ring/IA frequency table; `intel_llc_disable(struct intel_llc *llc)` is the matching shutdown hook and currently has no hardware work.

Control flow: callers include this header, pass the `intel_gt.llc` member, and rely on `intel_llc.c` to recover the containing GT.

State and persistence: no state is defined here; state lives in hardware PCU tables and the empty `struct intel_llc` declared in `intel_llc_types.h`.

Dependencies and integration points: forward-declares `struct intel_llc` to avoid leaking GT internals. Used by GT power-management setup.

Risks: the API assumes `intel_llc` is embedded in `struct intel_gt`; standalone allocation would break `container_of()` in the implementation.

Test signals: compile coverage of GT setup and selftest coverage from `intel_llc.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_llc.h -->
