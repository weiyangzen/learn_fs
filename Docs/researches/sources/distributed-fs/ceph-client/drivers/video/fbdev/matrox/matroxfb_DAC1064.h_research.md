## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_DAC1064.h

Purpose: `matroxfb_DAC1064.h` defines the internal interface and register map for MGA1064/DAC1064-compatible Matrox RAMDACs. It exposes low-level switch objects and global DAC helper functions while centralizing DAC register numbers, bit definitions, and software positions into `matrox_hw_state.DACreg`.

Important APIs and types: it declares `matrox_mystique`, `matrox_G100`, `DAC1064_global_init()`, and `DAC1064_global_restore()` behind configuration guards. Register definitions cover palette access, hardware cursor, DVI clock control, pixel/system/video PLL registers, general control, misc/output connection/power/pan mode registers, and `enum POS1064` indexes used by DAC register image arrays.

Control flow: no executable flow. The header's register constants are consumed by DAC1064, G450 PLL, I2C, and related output code when building or writing hardware state.

State and persistence: the header maps logical names to persistent hardware state in DAC registers and to cached software state positions. `POS1064_*` enum values must align with the arrays in `matroxfb_DAC1064.c`; any mismatch corrupts restore programming.

Dependencies and integration points: includes `matroxfb_base.h`, binding it to `struct matrox_fb_info`, `matrox_switch`, and common register accessors. It is an internal driver ABI for Matrox fbdev objects, not a user-visible header.

Risks: the header contains many chipset-specific bit definitions with overlapping meanings across G200/G400/G450. Wrong bit use can power down outputs, select the wrong PLL, or disable the LUT. Because several definitions share numeric registers with different names, future changes need hardware-family awareness.

Test signals: build all `CONFIG_FB_MATROX_MYSTIQUE` and `CONFIG_FB_MATROX_G` combinations. Runtime smoke tests should verify every register-image index used by `MGA1064_DAC_regs[]` maps to the expected `POS1064_*` position, and that G450/G550 DVI/secondary output paths still program `XOUTPUTCONN`, `XPWRCTRL`, and `XPANMODE` correctly.
