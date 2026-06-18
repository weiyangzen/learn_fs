<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_st7789v.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_st7789v.c

Purpose: supports ST7789V LCD controllers and optionally synchronizes framebuffer writes to a panel tearing-effect GPIO interrupt.

Important APIs/types/functions: `init_tearing_effect_line()` requests optional `te` GPIO and IRQ, `panel_te_handler()` completes a global completion, `init_display()` programs ST7789V power/porch/gamma-related defaults, `write_vmem()` waits for TE before dispatching to buswidth-specific FBTFT writers, `set_var()`, `set_gamma()`, and `blank()` handle runtime settings.

Control flow: init resets, sets up TE IRQ if present, exits sleep, sets RGB565, writes porch/gate/VRH/VCOM/power, enables TE output if IRQ exists, turns display on, and optionally enters invert mode. Every update enables the TE IRQ, waits up to 33 ms, disables it, then writes through the selected bus helper.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: static global `panel_te` and `irq_te` are not per-device, limiting multi-panel safety. Timeout logs but still writes. Optional TE GPIO lifetime is devm IRQ-managed after dropping the descriptor. Unsupported buswidth logs and returns success-like zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_st7789v.c -->
