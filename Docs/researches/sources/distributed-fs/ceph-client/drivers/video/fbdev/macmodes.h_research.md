## sources/distributed-fs/ceph-client/drivers/video/fbdev/macmodes.h

Purpose: `macmodes.h` defines the public contract for the MacOS video mode helper library. It provides the legacy VMODE and CMODE numeric constants used by Macintosh firmware/NVRAM and fbdev drivers, declares conversion/search helpers, and records NVRAM offsets used for default video mode and color mode.

Important APIs and types: the header declares `mac_vmode_to_var()`, `mac_var_to_vmode()`, `mac_map_monitor_sense()`, and `mac_find_mode()`. It defines VMODE values from `VMODE_NVRAM` through `VMODE_1600_1024_60`, plus `VMODE_MAX` and `VMODE_CHOOSE`. It defines CMODE sentinel values (`CMODE_NVRAM`, `CMODE_CHOOSE`) and supported color modes (`CMODE_8`, `CMODE_16`, `CMODE_32`). `NV_VMODE` and `NV_CMODE` are fixed NVRAM offsets.

Control flow: this file has no executable flow; it constrains callers to the constants and prototypes implemented in `macmodes.c`. Compile-time inclusion lets drivers build mode-selection flows without duplicating Apple numeric IDs.

State and persistence: the only persistence-related content is the NVRAM address constants. The header does not read or write NVRAM itself; that is done by users such as `matroxfb_base.c` on PowerMac builds.

Dependencies and integration points: it expects callers to include or otherwise know `struct fb_var_screeninfo` and `struct fb_info`. It is included from `matroxfb_base.h` when `CONFIG_PPC_PMAC` is set and can be consumed by other Mac framebuffer drivers.

Risks: constants must remain synchronized with Apple mode numbers and with the lookup tables in `macmodes.c`; adding a VMODE here without updating the implementation can create accepted build-time values that fail at runtime. The CMODE naming is historical: CMODE_16 is documented as actually 15 bits/pixel and CMODE_32 as actually 24 bits/pixel plus padding/alpha, which can confuse users expecting generic fbdev depth semantics.

Test signals: compile all users under `CONFIG_PPC_PMAC`, verify NVRAM-derived mode selection paths, and ensure every public VMODE intended to work has a corresponding `mac_modes[]` entry. Header-level regression checks are mostly build and ABI checks: no duplicate constants, unchanged exported prototypes, and matching `VMODE_MAX`.
