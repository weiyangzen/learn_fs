<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9325.c -->
# sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9325.c

Purpose: supports ILI9325 240x320 LCDs with module parameters for power/voltage tuning.

Important APIs/types/functions: `bt`, `vc`, `vrh`, `vdv`, and `vcm` module parameters are masked in `init_display()`. `set_addr_win()`, `set_var()`, and `set_gamma()` mirror the ILI9320-style GRAM path.

Control flow: initialization writes internal timing, power sequencing with delays, GRAM area, gate scan, panel controls, and display-on. Runtime rotation changes entry mode and cursor addressing.

Dependencies and integration: depends on `fbtft.h`, the FBTFT core registration macros, SPI/platform device binding, `write_reg()`/`fbtftops`, framebuffer deferred I/O, GPIO reset/DC/backlight helpers where used, and controller-specific register semantics. State is mostly runtime panel state held in controller GRAM and `struct fbtft_par`; module parameters and gamma sysfs values affect initialization but no durable storage is written by the driver. Test signals: build as module and built-in, bind through SPI and platform aliases/compatible strings, verify reset/init, rotation, BGR/RGB order, address-window updates, blanking where present, gamma/contrast boundaries, and full-frame/partial framebuffer updates on real panel hardware or bus traces.

Risks: power parameters can produce unsupported panel voltages if changed poorly; the source documents one safe 3.3V configuration but does not validate electrical limits. Gamma register mappings are manual and error-prone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/fbtft/fb_ili9325.c -->
