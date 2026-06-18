## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/g450_pll.h

Purpose: `g450_pll.h` exposes the G450/G550 PLL helper interface to other Matrox fbdev modules. It is intentionally small: include the base driver state definition and declare the three public PLL helpers implemented in `g450_pll.c`.

Important APIs: `matroxfb_g450_setclk()` computes, tests, caches, and programs a target clock for a selected PLL. `g450_mnp2f()` converts a packed MNP register value to an output frequency using `minfo->features.pll.ref_freq`. `matroxfb_g450_setpll_cond()` writes a packed MNP only when the target PLL does not already contain it.

Control flow: no executable flow in the header. It provides compile-time declarations for DAC1064/G450 code paths to call during preinit, mode computation, and output restore.

State and persistence: the header itself owns no state. Its functions operate on `struct matrox_fb_info`, so callers must have initialized PLL feature limits, caches, DAC locks, and PCI/MMIO mappings before use.

Dependencies and integration points: it includes `matroxfb_base.h`, which makes it part of the same internal Matrox driver ABI. It is used by `matroxfb_DAC1064.c` and likely G450-specific support objects selected by the Makefile.

Risks: callers can request invalid PLL IDs or use uninitialized `matrox_fb_info` fields; implementation returns errors for invalid IDs but hardware sequencing still relies on correct caller context. Because the header is not a stable external API, symbol or signature changes require coordinated updates in all Matrox objects.

Test signals: build all `CONFIG_FB_MATROX_G` configurations and load/use G450/G550 modes. Static checks should ensure prototypes match exported symbols and no non-G configs include this header without required object linkage.
