<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_hwconfig.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_hwconfig.h

Purpose: declares the GT hardware-configuration blob container and init/fini entry points.

Important APIs and types: `struct intel_hwconfig` holds a byte size and pointer to parsed/raw hardware configuration data. `intel_gt_init_hwconfig(struct intel_gt *gt)` is the setup hook and `intel_gt_fini_hwconfig(struct intel_gt *gt)` releases the blob.

Control flow: GT initialization is expected to populate `gt->hwconfig` through the init function, and GT teardown releases any allocated memory through fini. This header does not define parsing semantics; it is a small contract between GT setup and hardware-config users.

State and persistence: the persistent state is a pointer/size pair attached to the GT for the lifetime between init and fini. It may represent firmware-provided or hardware-discovered capability data.

Dependencies and integration points: forward-declares `struct intel_gt` and includes only Linux integer types. Integrates with GT initialization and any downstream code that interprets hardware configuration keys.

Risks: consumers must validate `ptr` and `size` before parsing. Ownership is implicit from the init/fini pairing, so double-free or stale-pointer bugs are possible if callers bypass fini or copy the struct blindly.

Test signals: GT probe/fini tests, missing/empty hwconfig cases, malformed blob parsing in implementation files, and memory leak checks during driver unload/reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_hwconfig.h -->
