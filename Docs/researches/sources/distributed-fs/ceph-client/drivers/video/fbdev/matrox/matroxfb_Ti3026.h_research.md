## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/matroxfb_Ti3026.h

Purpose: `matroxfb_Ti3026.h` is the minimal internal header for the Millennium TVP3026 low-level driver. It declares the `matrox_millennium` switch when Millennium support is enabled.

Important APIs: `extern struct matrox_switch matrox_millennium` is the sole public symbol declaration, guarded by `CONFIG_FB_MATROX_MILLENIUM`. The switch supplies `preinit`, `reset`, `init`, and `restore` callbacks to the base driver.

Control flow: no runtime flow. Inclusion lets `matroxfb_base.c` reference the Millennium switch in board tables when the configuration includes Millennium support.

State and persistence: no state is owned by the header. All state is carried through `struct matrox_fb_info` and programmed by `matroxfb_Ti3026.c`.

Dependencies and integration points: includes `matroxfb_base.h`, so the switch type and shared device state are available. It is part of the internal Matrox fbdev object linkage selected by Kbuild.

Risks: if the config guard or object list changes inconsistently, Millennium board-table entries can fail to compile or link. The header intentionally does not expose TVP3026 register constants; consumers should not bypass the switch abstraction.

Test signals: build with and without `CONFIG_FB_MATROX_MILLENIUM`; confirm `matroxfb_base.c` device tables resolve `matrox_millennium` only when expected. Runtime signals are covered by the C file through successful Millennium probe and mode restore.
