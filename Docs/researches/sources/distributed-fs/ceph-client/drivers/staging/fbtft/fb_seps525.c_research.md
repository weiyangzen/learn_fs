<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_seps525.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_seps525.c

Purpose: drives a 160x128 SEPS525 OLED controller such as Newhaven NHD-1.69 modules.

Important APIs/types/functions: `init_display()` programs oscillator, current/precharge, display mode, RGB interface, memory write mode, duty, display-on, and soft reset. `set_addr_win()` sets pointer/window registers. `set_var()` supports only 0 and 180 degree rotation and BGR swap.

Control flow: init resets and configures OLED current and memory mode, then enters data-access port. Address updates set optional window bounds and current X/Y pointer. Unsupported 90/270 rotation returns `-EINVAL`.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: `seps525_use_window` is compile-time zero, so window bounds are not currently used. Only two rotations work. OLED current constants are fixed and may not suit all panels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_seps525.c -->
