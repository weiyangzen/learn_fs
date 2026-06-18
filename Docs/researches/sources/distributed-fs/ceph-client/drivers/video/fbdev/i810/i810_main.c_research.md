
# sources/distributed-fs/ceph-client/drivers/video/fbdev/i810/i810_main.c

Purpose: main PCI fbdev driver for Intel 810/815 integrated graphics. It probes PCI devices, allocates AGP aperture-backed framebuffer/ring/cursor memory, validates modes, programs VGA and i810 display registers, exposes fb_ops, handles color maps, panning, cursor, blanking, suspend/resume, and cleanup.

Important APIs and functions: PCI binding uses `i810fb_pci_tbl` and `i810fb_driver`. Hardware programming is split across `i810_load_pll()`, `i810_load_vga()`, `i810_load_vgax()`, `i810_load_2d()`, `i810_load_color()`, `i810_load_pitch()`, and `i810_load_regs()`. Save/restore paths mirror this through `i810_save_vga_state()` and `i810_restore_vga_state()`. Mode logic uses `i810_round_off()`, `i810_check_params()`, `decode_var()`, `encode_fix()`, and timing helpers from `i810_dvt.c` or `i810_gtf.c`. fb_ops include open/release, check/set var, setcolreg, blank, pan, accel callbacks, cursor, sync, and mmap/read/write defaults.

Control flow: probe removes conflicting apertures, allocates `fb_info`, maps PCI aperture/MMIO, initializes defaults from module parameters, allocates AGP memory, initializes hardware, discovers EDID/modelist when I2C is enabled, validates an initial mode, initializes the ring buffer, registers the framebuffer, and stores PCI drvdata. Set-par decodes var into `par`, loads registers, initializes cursor, updates fixed info, and enables hardware acceleration flags if allowed. Open saves VGA state on first user; release restores it on last close. Suspend blanks and unbinds AGP memory; resume re-enables PCI, rebinds AGP memory, and reprograms mode.

State and persistence: `struct i810fb_par` carries mapped resources, AGP allocations, saved VGA state, mode registers, pitch/depth, cursor memory, pseudo palette, open count under `open_lock`, power state, EDID, and resource flags. Module parameters persist requested defaults such as `vram`, `voffset`, `bpp`, sync ranges, acceleration, MTRR, direct color, and DDC bus selection.

Dependencies and integration: integrates with PCI, fbdev core, AGP backend, aperture arbitration, VGA save/restore helpers, I2C/DDC helpers when configured, architecture write-combining, and acceleration/timing files. It includes `i810_regs.h`, `i810.h`, and `i810_main.h`.

Risks: error unwinding depends on `res_flags` and partially initialized allocations; AGP bind failures can leak unless all paths are maintained carefully. Mode validation mutates user vars and can shrink virtual resolution. Register programming temporarily disables DRAM refresh, so ordering is safety critical. Cursor memory is AGP physical memory and has alignment assumptions. Open/release VGA restore can race with console/power transitions if locking assumptions change.

Test signals: PCI probe/remove fault injection, mode changes for 8/16/24/32 bpp, EDID and no-EDID boot, DVT vs GTF builds, acceleration lockup fallback, blanking states, pan offsets, hardware cursor updates, suspend/resume with AGP rebind, and resource cleanup under each probe failure label.
