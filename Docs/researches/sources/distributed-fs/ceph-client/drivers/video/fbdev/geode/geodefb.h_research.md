# sources/distributed-fs/ceph-client/drivers/video/fbdev/geode/geodefb.h

## Purpose
`geodefb.h` defines the common private interface between Geode framebuffer core, display-controller, and video-output modules.

## APIs And Control Flow
`struct geode_dc_ops` provides `set_mode()` and `set_palette_reg()` hooks. `struct geode_vid_ops` provides `set_dclk()`, `configure_display()`, and `blank_display()` hooks. `struct geodefb_par` stores CRT/panel settings, display/video MMIO bases, and selected operation tables.

## State, Dependencies, Integration, Risks
There is no logic in the header; `geodefb_par` persists as `fb_info->par`. Display modules consume it during mode set and palette updates, while video modules handle clocks/output/blanking. Risks are null ops or uninitialized MMIO bases. Tests should cover probe initialization, panel dimensions, mode/palette callbacks, and blanking through `vid_ops`.
