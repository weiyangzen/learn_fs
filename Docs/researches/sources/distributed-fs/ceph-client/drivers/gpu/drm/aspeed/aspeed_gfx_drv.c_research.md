## sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/aspeed_gfx_drv.c

Purpose: platform driver for the ASPEED BMC GFX display controller. It owns compatible matching, MMIO/resource setup, reserved memory and DMA setup, reset/clock enable, IRQ registration, DRM device registration, sysfs controls, and shutdown/remove.

Important pieces are `struct aspeed_gfx_config`, AST2400/2500/2600 config tables, `aspeed_gfx_match`, `aspeed_gfx_setup_mode_config`, `aspeed_gfx_irq_handler`, `aspeed_gfx_load`, `aspeed_gfx_unload`, sysfs attributes `dac_mux` and `vga_pw`, `aspeed_gfx_probe`, `aspeed_gfx_remove`, and `aspeed_gfx_shutdown`. The DRM driver uses DMA GEM/fbdev helper ops.

Control flow: probe allocates a managed DRM device, maps MMIO, selects SoC config, finds SCU regmap by phandle or fallback compatible, initializes reserved memory and 32-bit DMA mask, deasserts reset, enables clock, clears control registers, initializes mode config/vblank/output/pipe/IRQ, creates sysfs, registers DRM, and starts generic clients. IRQ handler checks vertical interrupt status, calls `drm_crtc_handle_vblank`, and writes the configured clear register.

State persists in hardware registers, sysfs-visible SCU fields, clocks/resets, reserved memory assignment, DRM mode config, and platform drvdata. Dependencies are OF, syscon/regmap, reset/clk, reserved-memory, DRM DMA helpers, and the pipe/output files. Risks include no error unwinding for enabled clock/reset on mid-load failures, `dac_mux_store` returning `0` on regmap update failure, fallback SCU compatible being AST2500-specific, and a hard max mode of 800x600. Test signals are probe/remove cycles, sysfs read/write behavior, vblank IRQs, reserved memory/DMA mask success, and shutdown disabling scanout via atomic helper.
