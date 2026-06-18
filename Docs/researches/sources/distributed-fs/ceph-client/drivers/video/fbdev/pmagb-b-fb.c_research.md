## sources/distributed-fs/ceph-client/drivers/video/fbdev/pmagb-b-fb.c

Purpose: this TurboChannel fbdev driver supports DEC PMAGB-B Smart Frame Buffer cards. It maps SFB control registers, Bt459 DAC registers, and framebuffer memory; reads hardware timing registers to populate fbdev geometry; estimates oscillator frequencies; exposes an 8-bpp pseudocolor framebuffer; programs palette entries; and disables the hardware cursor.

Important APIs/types/functions: `struct pmagbbfb_par` stores MMIO, framebuffer, SFB, DAC pointers, detected oscillator frequencies, and slot. `pmagbbfb_defined`/`pmagbbfb_fix` define base fbdev state and resource sizes. `sfb_write()`/`sfb_read()`, `dac_write()`/`dac_read()`, and `gp0_write()` access device registers. `pmagbbfb_setcolreg()` writes Bt459 cmap entries. `pmagbbfb_screen_setup()` decodes horizontal/vertical timing registers into `fb_var_screeninfo` and line length. `pmagbbfb_osc_setup()` measures oscillator counts against TC bus speed and sets `pixclock`.

Control flow: init registers a TC driver unless boot options disable it. Probe allocates `fb_info`, allocates cmap, sets fbops/fix/var, reserves the TC resource, maps MMIO, derives SFB and DAC pointers, maps framebuffer memory, reads `SFB_REG_VID_BASE` and offsets `screen_base` into the active video buffer, disables cursor, reads screen timing, measures oscillators, registers fbdev, grabs a device reference, and logs oscillator data. Remove unregisters, unmaps framebuffer/MMIO, releases resources, frees cmap, and releases `fb_info`.

State and persistence behavior: geometry and pixclock are derived from hardware registers at probe and then stored in `info->var`. Palette state lives in the Bt459. Oscillator readings are cached in `par->osc0`/`osc1`. No persistent storage exists. The active framebuffer base can be offset within SRAM depending on `VID_BASE`.

Dependencies and integration points: depends on TurboChannel bus speed APIs, fbdev default IOMEM ops, Linux delay/resource/ioremap APIs, and `<video/pmagb-b-fb.h>` register constants. Matching uses TC strings `DEC` and `PMAGB-BA`.

Risks: oscillator measurement uses polling loops and timing assumptions; inaccurate TC speed or stuck counters can skew pixclock. `screen_size` subtracts twice the `vid_base` offset, so unusual hardware values could underflow or reduce usable memory unexpectedly. The driver does not expose acceleration despite SFB hardware. Fixed 8-bpp pseudocolor operation limits mode flexibility. As with PMAG-BA, palette writes use old fbdev return conventions.

Test signals: probe on PMAGB-B hardware with different oscillator selections, verify decoded resolution/timings from SFB registers, colormap writes, framebuffer base offset handling, cursor disabled state, boot-option disable path, failure-path resource cleanup, and remove after active console use.
