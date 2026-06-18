# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_tdf.h

Purpose: declares the Transient Data Flush display hook for Xe2+ cache-coherency handling. The comment explains that display surfaces rendered with special L3:XD PAT caching need KMD-enforced transient cache flushes before display flips because the display engine is not coherent with CPU/GPU caches.

Important API: `intel_td_flush(struct intel_display *display)`. Under `I915` it is an inline no-op. Non-I915 builds get an external declaration, allowing Xe display code to provide a real implementation.

Control flow and integration: flip or scanout paths can call `intel_td_flush()` through shared display code without branching on driver family. I915 keeps zero behavior because this cache mode is not active there.

State and persistence: the header stores no state. The relevant persistent behavior is cache visibility before a display flip; the no-op versus real implementation boundary is build-time.

Risks and tests: the main risk is forgetting to call the hook before a scanout surface becomes visible on platforms that enable transient caching. Tests should include Xe display flip coherency with PAT modes, I915 build coverage for the no-op inline, and static checks that shared code can include this header without pulling in driver-private cache definitions.
