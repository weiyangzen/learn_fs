# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_rc6.h Research

Purpose: this header declares the two RC6 live selftest functions for registration from other i915 selftest aggregation code.

Important APIs/types/functions: it exposes `int live_rc6_ctx_wa(void *arg);` and `int live_rc6_manual(void *arg);` under include guard `SELFTEST_RC6_H`.

Control flow: there is no runtime behavior in the header. Both functions accept the selftest `void *arg` convention, expected to be an `intel_gt *` by the implementation.

State and persistence: no state is owned by the header. The implementation mutates RC6 and context state, but that is not represented here.

Dependencies/integration: the header is the integration point between RC6 selftest implementation and the broader i915 selftest runner. It deliberately avoids including GT or RC6 structure definitions.

Risks and test signals: build failures are the main signal if prototypes drift. The narrow interface keeps compile-time coupling low.
