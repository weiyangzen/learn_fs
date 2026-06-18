## sources/distributed-fs/ceph-client/drivers/video/fbdev/matrox/g450_pll.c

Purpose: `g450_pll.c` implements clock synthesis and programming for Matrox G450/G550 PLLs. It converts packed MNP values to frequencies, searches candidate divider settings for target output clocks, tests hardware lock stability, caches working settings, and programs pixel/system/video PLL registers through the DAC1064 accessors.

Important APIs and functions: exported functions are `matroxfb_g450_setclk()`, `g450_mnp2f()`, and `matroxfb_g450_setpll_cond()`. Internal helpers include `g450_firstpll()`/`g450_nextpll()` for candidate enumeration, `g450_setpll()` and `g450_cmppll()` for hardware register writes/compare, `g450_isplllocked()`/`g450_testpll()` for lock testing, `g450_findworkingpll()` for robustness scanning, and the small LRU-like cache helpers `g450_addcache()`/`g450_checkcache()`.

Control flow: `matroxfb_g450_setclk()` allocates a candidate/delta table and calls `__g450_setclk()`. The latter prepares clock source/power state based on PLL type, selects the relevant limits/cache, enumerates MNP candidates sorted by frequency delta, reuses a cached known-good setting if available, otherwise probes nearby loop-control variants and lock status, writes the selected MNP, updates `minfo->hw.DACclk` for system PLL, and returns the programmed MNP.

State and persistence: persistent driver state is stored in `minfo->cache.{pixel,system,video}` and `minfo->hw.DACclk`. Hardware state persists in DAC PLL registers and PCI option registers. The cache keys mask frequency-significant bits to allow reuse of lock-stable MNP variants across calls.

Dependencies and integration points: this file depends on `matroxfb_base.h` for `matrox_fb_info`, PLL limits/features, PCI/MMIO helpers, and lock macros; it depends on `matroxfb_DAC1064.h` for DAC register constants and DAC I/O. DAC1064/G450 output code calls it when computing clocks for CRTC1/CRTC2, video PLL, legacy VGA clocks, and system memory clocks.

Risks: PLL programming can blank displays or lock hardware if sequencing is wrong. Candidate enumeration assumes table size 64 is larger than all possible M/P combinations. Several register writes are chipset-specific and comments note PC breakage for one DVI clock register. Lock testing is polling-heavy and can add latency. Incorrect PLL limits from BIOS/PINS parsing can produce unstable clocks.

Test signals: validate by setting a range of CRTC1 and CRTC2 modes on G450/G550, checking no PLL lock timeout, stable display, and accurate `g450_mnp2f()` frequency reporting. Exercise cache hits by switching between modes repeatedly. Regression tests should include system/video PLL setup during cold initialization and DVI/panel-link scenarios near `max_pixel_clock_panellink`.
