# sources/distributed-fs/ceph-client/drivers/video/fbdev/atafb.c

## Purpose
`atafb.c` is the Atari built-in framebuffer driver. It supports ST/STe, TT, Falcon VIDEL, and external framebuffer adapters through one fbdev front end and a hardware switch table. It translates `fb_var_screeninfo` requests into Atari shifter or VIDEL register programming, allocates or maps video memory, handles palette updates, panning, blanking, and dispatches drawing operations to Atari-specific planar helpers.

## Important APIs, types, and functions
The central private state is `struct atafb_par`, which stores `screen_base`, `yres_virtual`, `next_line`, and a hardware-specific union for TT, ST, and Falcon register state. `struct fb_hwswitch` abstracts hardware operations: `detect`, `encode_fix`, `decode_var`, `encode_var`, `get_par`, `set_par`, `set_screen_base`, `blank`, and `pan_display`.

Backend families are implemented by `tt_*`, `falcon_*`, `stste_*`, and `ext_*` functions. The public fbdev surface is `atafb_ops`, with `fb_check_var`, `fb_set_par`, `fb_blank`, `fb_pan_display`, `fb_fillrect`, `fb_copyarea`, `fb_imageblit`, `fb_ioctl`, default I/O memory read/write, and mmap helpers. `atafb_probe()` selects the backend, allocates or maps framebuffer memory, initializes `fb_info`, chooses a default mode, and registers the framebuffer. `atafb_init()` registers a simple platform device and probes the platform driver on Atari systems.

## Control flow
Boot setup starts with `fb_get_options("atafb", ...)` and `atafb_setup()`, which parses built-in modes, external framebuffer specs, internal overscan geometry, Falcon external clocks, monitor capabilities, `keep`, and user modes. `atafb_probe()` then chooses `ext_switch`, `tt_switch`, `falcon_switch`, or `st_switch` based on explicit external address and `ATARIHW_PRESENT()` probes. It calls the selected `detect()` routine, validates a default mode through `check_default_par()`, allocates ST-RAM or maps external memory, initializes `fb_info.var/fix`, registers the mode list and colormap, then calls `register_framebuffer()`.

Mode validation flows through `atafb_check_var()` to the active backend's `decode_var()`, then back through `encode_var()` so users see rounded and supported geometry. Real mode setting uses `atafb_set_par()`: decode `info->var`, regenerate fixed info under `mm_lock`, and call `ata_set_par()`. Falcon changes are deferred to `falcon_vbl_switcher()` on vertical blank to avoid visible mode-switch glitches.

Drawing clips at the fbdev layer, then dispatches by depth. 1 bpp goes to `atafb_mfb_*`, 2/4/8 bpp interleaved planar modes go to `atafb_iplan2p{2,4,8}_*`, and Falcon 16 bpp truecolor falls back to generic `cfb_*` helpers. Non-1-bit image blits use `c2p_iplan2()`.

## State and persistence behavior
Persistent runtime state is global and driver-lifetime scoped: `fb_info`, `current_par`, `screen_base`, `phys_screen_base`, `screen_len`, monitor flags, setup options, Falcon pending mode state, and external framebuffer configuration. There is no on-disk persistence. Hardware state persists in Atari MMIO/shifter registers until reprogrammed. `current_par_valid` gates whether cached state or hardware state is used. Falcon has asynchronous state transfer through `f_new_mode`, `f_change_mode`, and `f_pan_display` serviced by the VBL IRQ.

## Dependencies and integration points
The driver depends on Atari architecture headers and hardware globals (`asm/atarihw.h`, `asm/atariints.h`, `asm/atari_stram.h`, shifter/VIDEL/MFP/ACIA/YM registers), fbdev core APIs, ST-RAM allocation, interrupt registration, kernel cache mode control, and the local Atari blit helpers declared in `atafb.h`. External framebuffer support uses `ioremap_wt()` and optional VGA DAC I/O mapping. Falcon mode switching integrates with `IRQ_AUTO_4`.

## Risks and edge cases
The driver is hardware-specific and uses global mutable state, raw MMIO/register writes, and panic paths for missing default modes or screen memory. Many mode calculations rely on historic timing constraints and comments call out known limitations for Falcon SM124/TV modes. `atafb_copyarea()` computes clipped widths as unsigned values after destination clipping; bad caller inputs could produce underflow if clipping assumptions are violated. External framebuffer setup trusts boot parameters for physical addresses and lengths. Falcon deferred mode state is shared with an interrupt handler and relies on simple flags. The driver comments note it cannot be unloaded.

## Test signals
Useful validation includes booting on Atari ST/STe, TT, Falcon, and configured external adapter paths; checking `register_framebuffer()` success and reported geometry; running fbdev mode tests for each predefined and user mode; exercising panning and hardware scroll boundaries; palette tests for TT, ST/STE, Falcon, VGA, and MV300 mappings; fbcon text rendering for 1/2/4/8 bpp and Falcon 16 bpp; blank/unblank and kexec shutdown unblank; and stress tests for overlapping copyarea and clipped fill/imageblit.
