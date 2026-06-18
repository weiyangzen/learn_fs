# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_fdi.c

Purpose: implements FDI link bandwidth calculation, atomic validation, PLL control, link training, enable-state assertions, and disable sequencing for pre-DDI PCH display links and Haswell FDI-over-DDI mode.

Important APIs/types/functions: private `struct intel_fdi_funcs` selects platform link-training hooks. Public functions include `intel_fdi_init_hook()`, `intel_fdi_link_train()`, `intel_fdi_add_affected_crtcs()`, `intel_fdi_pll_freq_update()`, `intel_fdi_link_freq()`, `ilk_fdi_compute_config()`, `intel_fdi_atomic_check_link()`, `intel_fdi_normal_train()`, `ilk_fdi_pll_enable()`, `ilk_fdi_pll_disable()`, `ilk_fdi_disable()`, `hsw_fdi_link_train()`, `hsw_fdi_disable()`, and assertion helpers for TX/RX/PLL state.

Control flow: mode computation derives required FDI lanes from adjusted dotclock, link frequency, and pipe bpp, then computes M/N values. Atomic bandwidth checks enforce lane limits: max four lanes generally, Haswell/Broadwell two lanes, and Ivy Bridge pipe B/C sharing rules, with fallback through bpp reduction and `-EAGAIN`. Training sequences program TU size, unmask lock interrupts, enable TX/RX in pattern 1, poll bit lock, switch to pattern 2, poll symbol lock, then switch to normal training. Haswell trains DDI E with PCH RX and SPLL, iterating voltage/emphasis entries. Disable paths turn off TX/RX, DDI buffers, clocks, PLLs, PCDCLK, and reset training patterns.

State and persistence: persistent fields include `display->funcs.fdi`, `display->fdi.pll_freq`, `display->fdi.rx_config`, and per-CRTC `fdi_lanes`/`fdi_m_n`. Hardware FDI TX/RX/PLL/training/bifurcation state persists in MMIO registers until reprogrammed.

Dependencies and integration: depends on intel atomic state, CRTC state, link bandwidth reduction, DP M/N helpers, DDI buffer/clock helpers, display register access, PCH type/platform checks, and register definitions in `intel_fdi_regs.h`.

Risks: FDI training is timing-sensitive and platform-specific. Shared Ivy Bridge lane bifurcation can require modesetting an otherwise unchanged pipe. Continuing after training failure may preserve state checker expectations but can leave a blank output. PLL and PCDCLK sequencing errors can hang or corrupt PCH output. Assertions differ for DDI platforms where TX state is represented through transcoder/DDI registers.

Test signals: test Ironlake, Sandy Bridge, Ivy Bridge 3-pipe sharing, Haswell/Broadwell PCH connectors, bpp fallback under high bandwidth, link training failure logs, hotplug/modeset cycles, PLL enable/disable sequencing, and state checker assertions.
