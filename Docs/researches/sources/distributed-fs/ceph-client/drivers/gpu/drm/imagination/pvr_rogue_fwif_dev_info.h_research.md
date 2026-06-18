# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_dev_info.h

Purpose: This header enumerates firmware-visible device capability indices for BRNs, ERNs, and hardware features. It is an index contract rather than a value store: arrays or bitsets elsewhere use these enum values to report whether a workaround, enhancement, or feature exists.

Important APIs/types/functions: The BRN enum includes entries such as 44079, 47217, 48492, 48545, 49927, 50767, 51764, 62269, 63142, 63553, 66011, and 71242, ending with `PVR_FW_HAS_BRN_MAX`. The ERN enum includes 35421, 38020, 38748, 42064, 42290, 42606, 47025, and 57596, ending with `PVR_FW_HAS_ERN_MAX`. The feature enum covers major HW capabilities: AXI ACE-lite, CDM control stream format, cluster grouping, compute, FBCDC variants, GPU multicore/virtualization, IRQ per OS, ISP/ZLS/tile parameters, META/MIPS/RISC-V FW processors, number of clusters/OSIDs/raster pipes, SLC sizing/cache line, SOC timer, tessellation, TLA, TPU globals/filtering, USC output registers, VDM features, watchdog, workgroup protection, XE architecture/memory, XPU limits, and more, ending with `PVR_FW_HAS_FEATURE_MAX`.

Control flow: None. Consumer code indexes capability tables with these values.

State and persistence behavior: No state. The enum order is persistent ABI for feature bitmaps passed between host and firmware.

Dependencies and integration points: No includes. It integrates with device info extraction, feature tables, command stream generation, BRN/ERN extension streams, and firmware compatibility checks.

Risks: Reordering or deleting enum entries changes every downstream bit/index interpretation. New capabilities must be appended carefully and paired with table-size updates. Misreported feature bits cause command packing to include missing registers or omit required workaround data.

Test signals: Feature table bounds tests against `*_MAX`, BVNC compatibility tests, command-stream generation on multiple GPU feature sets, and BRN/ERN-specific regression tests.
