# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/selftests/mock_gem_device.c

Purpose: constructs and tears down an in-kernel mock `drm_i915_private` suitable for GEM, GT, GTT, context, memory-region, and engine selftests without real hardware.

Important APIs/functions: `mock_gem_device()` allocates a fake PCI device, DRM device, display descriptor, runtime-PM state, mock uncore, GGTT, memory regions, workqueues, contexts, and a mock RCS engine. `mock_device_flush()` repeatedly flushes all mock engines and retires GT requests. `mock_destroy_device()` removes display data and releases devres/device references. `mock_device_release()` performs release-time cleanup when the DRM device is dropped.

Control flow and state: creation is staged with explicit unwind labels. The fake device disables IOMMU via a fake `dev_iommu` when Intel IOMMU support is enabled, initializes mock platform info, disables real wakeref hardware by incrementing GT wakeref count, assigns a GGTT, creates one mock engine, clears the wedged bit, and sets `i915->do_release`. Cleanup flushes requests, removes GT driver objects, drains GEM work, finalizes GGTT, destroys workqueues, releases TTM and memory-region state, and cleans mode config.

Dependencies and integration: integrates many i915 subsystems: display device probing, runtime PM, GT driver setup, mock engine/request/context helpers, memory regions, region TTM, GGTT, GEM MM, and DRM managed allocation.

Risks: partial initialization paths must exactly mirror successful initialization or leak workqueues, memory regions, devres, or fake devices. Because it fakes power/IOMMU/uncore behavior, it is good for unit-level GEM logic but not hardware timing.

Test signals: successful selftests should create/destroy mock devices repeatedly without leaks, workqueue leftovers, active requests, or WARNs from GT/memory-region teardown.
