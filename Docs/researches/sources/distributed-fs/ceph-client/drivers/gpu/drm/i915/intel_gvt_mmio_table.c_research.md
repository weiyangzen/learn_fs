# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_gvt_mmio_table.c

Purpose: defines the MMIO register ranges that GVT must snapshot or track for virtual GPU emulation.

Important APIs/functions: exports `intel_gvt_iterate_mmio_table()`. Internal iterator functions cover generic registers, BDW-only registers, BDW-plus gen8 registers, pre-SKL PCH/AUX ranges, SKL-plus display/GT/power registers, and BXT-specific DPIO/PHY/PLL/ring ranges. Macros `MMIO_F`, `MMIO_D`, and `MMIO_RING_*` centralize callback invocation by register offset and size.

Control flow: the exported function always iterates the generic table, then dispatches by platform: Broadwell gets BDW-only, BDW-plus, and pre-SKL ranges; Skylake/Kaby/Coffee/Comet get BDW-plus and SKL-plus; Broxton gets BDW-plus, SKL-plus, and BXT ranges. Any callback error aborts iteration and propagates.

State and persistence: this file stores no runtime state. It drives caller-owned state through `iter->handle_mmio_cb`, commonly a snapshot buffer or GVT tracking table.

Dependencies and integration: includes many display, GT, pcode, MCHBAR, PV info, and GVT register headers. `intel_gvt.c` uses it to capture initial hardware state; the GVT module can use the same iterator for MMIO emulation metadata.

Risks: this is a large hand-maintained register inventory; omissions or wrong sizes can produce incomplete virtual device state. Platform guards must match GVT-supported hardware. Callback alignment assumptions are enforced only through the callback used by snapshot code.

Test signals: GVT host initialization, vGPU boot/display workloads, suspend/resume state restoration, and platform-specific register access fault testing.
