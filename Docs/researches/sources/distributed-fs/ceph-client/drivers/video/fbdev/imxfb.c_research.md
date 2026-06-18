
# sources/distributed-fs/ceph-client/drivers/video/fbdev/imxfb.c

Purpose: platform framebuffer driver for Freescale i.MX1/i.MX21 LCD controllers. It reads display timing from device tree, allocates DMA framebuffer memory, programs LCDC timing and pixel format registers, controls clocks/regulator-backed LCD power, and exposes basic fbdev operations.

Important APIs and types: `struct imx_fb_videomode` extends `fb_videomode` with `pcr`, `aus_mode`, and bpp. `struct imxfb_info` stores mapped registers, clocks, controller type, panel type, DMA buffer addresses, mode list, colormap behavior, LCDC register defaults, and LCD regulator state. Key functions are `imxfb_check_var()`, `imxfb_set_par()`, `imxfb_activate_var()`, `imxfb_enable_controller()`, `imxfb_disable_controller()`, DT parsing in `imxfb_of_read_mode()`, LCD ops, probe/remove, and PM suspend/resume.

Control flow: probe sets up fb_info, parses one native display phandle, computes framebuffer size, acquires clocks, briefly toggles `ipg` to reset an already-running controller, maps registers, allocates write-combined DMA memory, adds the videomode, initializes var/fix/cmap, registers an LCD device, registers framebuffer, and enables the controller. Check-var ignores arbitrary requested modes and forces the native DT mode, computes the pixel clock divider from `clk_per`, selects RGB bitfields and panel type from PCR bits, and stores `fbi->pcr`/`lauscr`. Set-par updates visual, line length, palette size, and writes LCDC timing registers.

State and persistence: runtime state is in `imxfb_info`, including `enabled`, `lcd_pwr_enabled`, cached PCR/PWMR/LSCR/DMACR/LAUSCR values, DMA address, and DT colormap flags. `fb_mode` is a file-static boot option but is reset during probe after fb_info initialization.

Dependencies and integration: uses platform/of matching, `of_get_fb_videomode`, clocks `ipg`/`ahb`/`per`, DMA API, regulator consumer API, LCD class, fbdev core, and PM helpers.

Risks: only one native DT mode is supported, so mode switching is intentionally constrained. The pixel-clock divisor warns and clamps when requested clock is too high. Power regulation is separate from controller enable; consumers may expect LCD power ops to be called. DEBUG_VAR logs invalid ranges but does not fail. The 32 bpp path advertises 24-bit fields for 18-bit hardware compatibility.

Test signals: DT parse success/failure, bpp 8/16/32 on i.MX1 vs i.MX21, PCR divider boundary conditions, static/inverse/grayscale cmap flags, regulator enable/disable, suspend/resume, blank/unblank, DMA allocation failure, and clock acquisition/enable failure paths.
