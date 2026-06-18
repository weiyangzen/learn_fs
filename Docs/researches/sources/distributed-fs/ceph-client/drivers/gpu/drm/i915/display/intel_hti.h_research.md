# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hti.h

Purpose: exposes the small HTI reservation query interface.

Important APIs/types/functions: declares `intel_hti_init()`, `intel_hti_uses_phy()`, and `intel_hti_dpll_mask()`.

Control flow: init snapshots HTI state, and display resource discovery queries the cached PHY/DPLL reservations.

State and persistence behavior: the header has no state; APIs operate on `display->hti.state`.

Dependencies and integration points: integrates HTI register decoding with encoder/PHY/DPLL allocation code through `struct intel_display` and `enum phy`.

Risks: the API assumes HTI state was initialized before resource decisions.

Test signals: build coverage and resource filtering tests on HTI-capable platforms.
