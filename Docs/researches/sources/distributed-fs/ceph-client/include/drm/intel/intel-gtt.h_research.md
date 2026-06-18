# sources/distributed-fs/ceph-client/include/drm/intel/intel-gtt.h

Purpose: provides the shared intel-gtt/i915 interface for GMCH GTT probing, aperture discovery, entry insertion, flushing, and removal on older Intel integrated graphics.

Important APIs/types/functions: functions include `intel_gmch_gtt_get()`, `intel_gmch_probe()`, `intel_gmch_remove()`, `intel_gmch_enable_gtt()`, `intel_gmch_gtt_flush()`, page and SG insertion, range clearing, and entry reading. Constants define AGP memory types and a GFDT cached user-memory flag.

Control flow: probe initializes GMCH GTT using bridge/GPU PCI devices and AGP bridge data. Drivers query total/mappable aperture, enable GTT, insert DMA pages or scatterlist entries at page indices, flush hardware, clear ranges, and read entries for diagnostics.

State and persistence: GTT tables are persistent hardware state for the device lifetime. This header owns no memory itself but exposes operations that mutate the aperture translation table.

Dependencies and integration: depends on PCI, AGP bridge, scatter-gather, DMA, and resource types. Used by `intel-gtt.ko`, i915, and legacy AGP/GEM memory paths.

Risks and test signals: off-by-one page indices, missing flushes, wrong flags, and stale entries can corrupt GPU memory access. Test probe/remove, aperture size reporting, SG insertion, clear/readback consistency, and suspend/resume GTT restoration on legacy platforms.
