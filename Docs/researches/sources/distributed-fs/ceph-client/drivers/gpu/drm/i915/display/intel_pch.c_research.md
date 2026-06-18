# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch.c

Purpose: detects the platform controller hub/south display compatibility type and applies PCH-specific clock-gating workarounds.

Important functions: `intel_pch_detect()` scans ISA bridge PCI devices or synthesizes fake/no-display PCH types, `intel_pch_init_clock_gating()` dispatches workarounds, `intel_pch_type()` maps masked PCI IDs to `enum intel_pch`, `intel_pch_fake_for_south_display()` handles DG1/DG2/MTL/LNL-style integrated south display, and virtualization helpers recognize QEMU/virt PCH cases.

Control flow: detection first checks fake south-display platforms; otherwise it scans Intel ISA bridges, masks device IDs, maps them to PCH types, and handles virtual/emulated bridges by estimating from GPU platform. If display is disabled, a detected PCH becomes `PCH_NOP`; if no bridge is found but running as a guest with display, it estimates a virtual PCH. Clock-gating init applies IBX/CPT/LPT/CNP register workarounds including panel power sequencer, chicken bits, FDI polarity, DP unit gating, LPT LP partition disable, and CNP PWM gating.

State and persistence: stores the result in `display->pch_type`; writes persistent hardware workaround bits in south display registers.

Dependencies/integration: uses PCI class scanning, display platform flags, VBT FDI RX polarity, display MMIO helpers, register definitions, guest detection, and the public `enum intel_pch`/macros from `intel_pch.h`.

Risks/test signals: mapping errors affect many south-display paths. Watch WARNs that platform generation does not match PCH ID, virtualization assumptions, fake PCH selection for new discrete/integrated platforms, and clock-gating bits on old LVDS/PCH systems. Test native and passthrough VMs, no-display SKUs, IBX/CPT/LPT/CNP hardware, and DG/MTL/LNL fake-PCH platforms.
