# sources/distributed-fs/ceph-client/drivers/video/fbdev/acornfb.c

## Purpose
`acornfb.c` is a platform framebuffer driver for Acorn ARM video hardware, primarily VIDC20 on Risc PC style systems. It registers one fbdev instance, allocates or uses display memory, validates monitor/video timings, programs VIDC/IOMD or MEMC display registers, manages the VIDC palette, and supports vertical panning/ywrap.

## Important APIs, Types, and Functions
Global driver state is split between static `struct fb_info fb_info`, `struct acornfb_par current_par`, and `struct vidc_timing current_vidc`. `current_par` records monitor type, DRAM/VRAM choice, palette cache, pseudo-palette, screen end address, and DPMS flag. The fb operation table uses `FB_DEFAULT_IOMEM_OPS`, `acornfb_check_var`, `acornfb_set_par`, `acornfb_setcolreg`, and `acornfb_pan_display`.

VIDC20 timing and palette programming are handled by `acornfb_set_timing()` and `acornfb_setcolreg()`. Timing validation and normalization are done by `acornfb_adjust_timing()`, `acornfb_validate_timing()`, and `acornfb_check_var()`. Boot/module options are parsed by `acornfb_setup()` with handlers for `mon:`, `montype:`, and `dram:`. Initialization runs through `acornfb_init_fbinfo()` and `acornfb_probe()`.

## Control Flow
`module_init()` registers a platform driver named `acornfb`. Probe reads `fb_get_options("acornfb")`, initializes the static fb_info once, resolves monitor specs from explicit options or default monitor detection, chooses a default mode from `modedb` that matches monitor ranges, and selects VRAM or allocated write-combining DRAM. It then calls `fb_find_mode()` with the local mode database and fallback paths, prints selected monitor/display settings, applies the variable mode with `fb_set_var()`, and registers the framebuffer.

Mode setting flows from fbdev into `acornfb_check_var()` then `acornfb_set_par()`. `check_var` validates bpp, pixel clock, adjusted memory geometry, and monitor sync ranges. `set_par` chooses palette size and visual type, computes line length, programs DMA start/end/control registers, updates the display DMA address, and writes VIDC timings. Panning only updates the hardware start address after checking ywrap/ypan bounds.

## State and Persistence
State is process-wide and effectively singleton. Palette values are cached in `current_par.palette`; current timing is cached in `current_vidc` to avoid rewriting unchanged VIDC timing registers. Framebuffer memory is either physical VRAM advertised by setup code through `vram_size` or DMA-allocated write-combining DRAM. Hardware state persists in VIDC/IOMD/MEMC registers until mode change or reset; there is no disk persistence.

## Dependencies and Integration Points
The driver depends on Acorn architecture headers, `mach/acornfb.h` helpers such as `acornfb_default_control()`, `acornfb_default_econtrol()`, `acornfb_valid_pixrate()`, and `acornfb_vidc20_find_rates()`, plus hardware accessors `vidc_writel()`, `iomd_writel()`, and `memc_write()` depending on platform defines. It integrates with the platform bus, fbdev core, fb mode helpers, DMA allocation, and `/dev/fb*`.

## Risks and Edge Cases
The driver uses static global state and has no remove path, matching old built-in platform assumptions but limiting hotplug/lifetime robustness. Probe leaks allocated DRAM if later `fb_find_mode()` or `register_framebuffer()` fails on VIDC20 paths. Monitor detection currently assumes SVGA, so unsafe monitor timings are possible if the user does not supply correct `mon:` or `montype:` options. `acornfb_parse_montype()` allows `montype == NR_MONTYPES`, which later falls back to SVGA because probe checks `> NR_MONTYPES`; this off-by-one-style boundary deserves care. The 16bpp VIDC20 palette path rewrites all 256 hardware palette entries on each logical palette update and must be tested for flicker/performance.

## Test Signals
Validation should cover boot with no options, explicit `montype:vga`, `montype:svga,dpms`, custom `mon:hmin-hmax:vmin-vmax`, `dram:` overrides, VRAM and DRAM framebuffer paths, all supported bpp modes, and ywrap/ypan bounds. Hardware signals include correct VIDC timing writes, `IOMD_VID*` or MEMC DMA register updates, palette changes in pseudocolor and directcolor modes, and successful fb console operation at the selected default mode.
