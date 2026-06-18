# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen.h

### Purpose

`evergreen.h` is the private Radeon driver header that exposes Evergreen-family ASIC helper functions to the rest of the Radeon driver. It does not define hardware registers or structures itself; instead it forward-declares key structs and declares the cross-file API implemented mainly by `evergreen.c` and used by ASIC callback tables, reset paths, memory-controller setup, IRQ setup, power management, and RLC support.

### Important APIs, types, and functions

The header forward-declares `struct evergreen_mc_save`, `struct evergreen_power_info`, and `struct radeon_device`. Its declarations cover display hang/status helpers (`evergreen_is_display_hung()`, `evergreen_print_gpu_status_regs()`), memory-controller sequencing (`evergreen_mc_stop()`, `evergreen_mc_resume()`, `evergreen_mc_wait_for_idle()`, `evergreen_mc_program()`, `evergreen_mc_init()`), interrupt shutdown (`evergreen_irq_suspend()`), PCIe policy (`evergreen_fix_pci_max_read_req_size()`, `evergreen_pcie_gen2_enable()`, `evergreen_program_aspm()`), RLC lifecycle (`sumo_rlc_fini()`, `sumo_rlc_init()`, `evergreen_rlc_resume()`), reset/status (`evergreen_gpu_pci_config_reset()`, `evergreen_gpu_check_soft_reset()`), DRAM topology (`evergreen_get_number_of_dram_channels()`), and power-info access (`evergreen_get_pi()`).

### Control flow

The header participates in compile-time dependency control. Source files that need Evergreen routines can include this header without pulling in the full implementation or concrete private struct definitions. In runtime terms, callers use these declarations as lifecycle hooks: MC stop/resume bracket unsafe aperture updates and reset sequences, IRQ suspend disables IH/interrupt state during suspend or reset, RLC init/resume/fini wraps firmware-controlled low-power state handling, and PCIe helpers are invoked during startup.

### State and persistence behavior

No state is stored in this header. All declared functions operate on `struct radeon_device *` and mutate hardware registers or fields inside the Radeon device object. The forward declaration of `struct evergreen_mc_save` makes MC save/restore state opaque to users of this header; callers can pass the save object only if they include a definition from another internal header or source context that knows its layout.

### Dependencies

This header depends only on include guards and pre-existing kernel/Radeon type availability for `bool`, `u32`, and the forward-declared structs. It intentionally avoids including register definition headers, DRM headers, or the full `radeon.h`, keeping it lightweight for internal inclusion.

### Integration points

`evergreen.h` is included by Evergreen-related Radeon implementation files and by other generation files that share reset, RLC, PCIe, or MC helper code. The functions declared here are part of the Radeon-internal ASIC callback boundary rather than a public UAPI. The naming also shows that some routines are Sumo/Fusion-specific but still live in the Evergreen support family.

### Risks

The main risk is API drift. Because this header is the contract between Evergreen implementation and other Radeon modules, changing prototypes or removing declarations can break ASIC tables or cross-generation helpers. The opaque forward declarations reduce compile-time coupling, but they also require the actual struct definitions and function implementations to remain consistent elsewhere. Declaring Sumo-specific functions in an Evergreen header can obscure ownership and make future refactors more error-prone.

### Test signals

Build tests with Radeon enabled are the primary validation signal for this header. Runtime coverage comes indirectly from any path that calls the declared functions: init/startup, suspend/resume, reset, MC reprogramming, IRQ suspend, RLC resume/fini, PCIe gen2/ASPM setup, and display hang detection. Header-specific failures typically appear as compile errors, missing symbol/link errors, or type mismatches after refactors.
