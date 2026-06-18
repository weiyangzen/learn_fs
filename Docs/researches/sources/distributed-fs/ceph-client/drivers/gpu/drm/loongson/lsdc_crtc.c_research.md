# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_crtc.c

Purpose: implements Loongson CRTC hardware operations, DRM CRTC funcs/helpers, pixel PLL atomic state, mode validation/programming, vblank handling, debugfs register views, and LS7A1000/LS7A2000 CRTC initialization.

Important APIs/types/functions: `ls7a1000_crtc_init`, `ls7a2000_crtc_init`, `lsdc_crtc_hw_ops`, reset/enable/disable/vblank/flip/clone/mode functions, `lsdc_pixpll_atomic_check`, `lsdc_crtc_mode_set_nofb`, and scanout-position helpers.

Control flow: reset allocates private CRTC state and writes minimal CFG reset values for S3 recovery. Atomic check computes pixel PLL parameters for enabled modes. Mode validation enforces chip max width/height, max pixel clock, and pitch alignment. Mode set updates PLL, optional DMA step, and timing registers. Atomic enable turns vblank on and enables output; disable turns vblank off, disables output, and sends pending events. Atomic flush arms or sends vblank events. Debugfs late registration exposes regs, pixclk, scan position, vblank count, and manual operations.

State and persistence: private CRTC state stores PLL parameters across atomic check to commit. Hardware CFG, timing, vblank counter, scan position, and PLL registers persist. `struct lsdc_crtc` stores chip ops, pixpll, debugfs metadata, and vblank capability.

Dependencies and integration points: depends on DRM atomic/vblank helpers, pixel PLL, register map macros, descriptor limits, planes supplied by `lsdc_plane.c`, and IRQ handlers delivering vblanks.

Risks and test signals: PLL computation failure rejects modes; pitch alignment differs by chip; LS7A1000 lacks working vblank counter. Test suspend/resume, mode switches across common clocks, page flips, vblank timestamps, debugfs manual ops, and odd-width DMA-step selection on LS7A2000.
