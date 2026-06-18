# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/selftest_llc.h Research

Purpose: this small header exposes the LLC selftest entrypoint to the i915 selftest wiring while avoiding a hard include dependency on the full LLC type definition.

Important APIs/types/functions: it forward-declares `struct intel_llc` and declares `int st_llc_verify(struct intel_llc *llc);`. The include guard is `SELFTEST_LLC_H`.

Control flow: there is no runtime control flow. The header lets callers compile against `st_llc_verify()` without needing internal implementation details from `selftest_llc.c`.

State and persistence: the header owns no state. The pointed-to `intel_llc` instance remains owned by GT/LLC code; the implementation only borrows it.

Dependencies/integration: it is consumed by selftest registration or LLC init/check paths that want to run table verification. Its narrow forward declaration reduces rebuild coupling and avoids accidental dependency on broader GT headers.

Risks and test signals: the main risk is prototype drift with the implementation or callers. Since it declares a single external function, build success is the signal that the interface remains synchronized.
