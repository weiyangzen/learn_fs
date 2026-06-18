# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_memory_region.h

Purpose: declares the memory-region abstraction used by i915 GEM allocation, local memory, stolen memory, and TTM-backed managers.

Important APIs/types: defines `enum intel_memory_type`, `enum intel_region_id`, `I915_ALLOC_CONTIGUOUS`, `for_each_memory_region`, `struct intel_memory_region_ops`, and `struct intel_memory_region`. Declares lookup, create/destroy, hardware probe/release, type string, reserve, debug, availability, and system/shmem setup functions.

Control flow: backend implementations provide ops for init/release/object initialization. Probe code creates regions and stores them in `i915->mm.regions`; users iterate with `for_each_memory_region` or look up by class/instance/type.

State and persistence: `struct intel_memory_region` holds the authoritative in-driver state for a region: resources, iomap, type, instance, UAPI name, object list, range-manager flag, and backend-private pointer.

Dependencies and integration: includes IO resources, mutex, IO mapping, `drm_mm`, and i915 UAPI memory classes. It bridges user-visible memory classes with internal GEM/TTM allocation backends.

Risks: object list locking is local to each region and must be honored by alloc/free paths. `private` hides regions from userspace but does not prevent internal misuse. Region IDs must stay aligned with capability bits and `intel_region_map`.

Test signals: compile coverage, memory-region selftests, object allocation tests by memory class, and debug/availability output.
