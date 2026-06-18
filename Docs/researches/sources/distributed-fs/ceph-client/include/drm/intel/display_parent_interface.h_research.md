# sources/distributed-fs/ceph-client/include/drm/intel/display_parent_interface.h

Purpose: defines the service table that an Intel parent/core graphics driver provides to the shared display driver. It decouples display code from i915/xe internals by grouping callbacks for buffer objects, DPT, DSB, frontbuffer, HDCP GSC, initial planes, IRQs, overlay, panic scanout, PC8, pcode, runtime PM, RPS, stolen memory, and VMAs.

Important APIs/types/functions: `struct intel_display_parent_interface` is the aggregate. Subinterfaces include `intel_display_bo_interface` for GEM/FB/mmapping/key/read/describe hooks, `intel_display_dpt_interface`, `intel_display_dsb_interface`, `intel_display_frontbuffer_interface`, `intel_display_hdcp_interface`, `intel_display_initial_plane_interface`, `intel_display_irq_interface`, `intel_display_overlay_interface`, `intel_display_panic_interface`, `intel_display_pc8_interface`, `intel_display_pcode_interface`, `intel_display_rpm_interface`, `intel_display_rps_interface`, `intel_display_stolen_interface`, and `intel_display_vma_interface`.

Control flow: display probe receives this table, then calls parent callbacks at display lifecycle points: framebuffer lookup/init/fini, DSB buffer creation and writes, HDCP GSC messaging, initial plane allocation/setup, IRQ synchronization, runtime-PM wakeref acquire/release, pcode mailbox requests, stolen memory node allocation, and overlay transitions. Non-optional callbacks must be callable without NULL checks.

State and persistence: no state is stored in the header, but callback ownership covers persistent parent state such as GEM objects, stolen allocations, RPM wakerefs, DSB buffers, HDCP GSC contexts, and frontbuffer references. Lifetime and locking are delegated to the parent.

Dependencies and integration: forward declares DRM, GEM, fence, seq_file, VM, Intel display, VMA, DPT, DSB, HDCP, panic, stolen, and ref-tracker types. It is a central integration boundary between shared Intel display code and concrete parent drivers.

Risks and test signals: risks include incomplete tables, incorrect optional/non-optional assumptions, lifetime mismatches, RPM leaks, stale stolen node ownership, and ABI expansion without updating all parents. Test through display probe on every parent, framebuffer mmap/init, modeset paths, runtime suspend/resume, HDCP, panic scanout, and pcode error injection.
