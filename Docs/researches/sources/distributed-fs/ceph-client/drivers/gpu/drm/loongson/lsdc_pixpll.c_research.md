# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_pixpll.c

Purpose: implements per-pipe Loongson pixel PLL setup, parameter lookup/computation, register programming, frequency reading, and printing.

Important APIs/types/functions: static known-clock table, `lsdc_pixel_pll_setup`, `lsdc_pixpll_find`, `lsdc_pixel_pll_compute`, low-level register read/write, power/bypass/parameter ops, `lsdc_pixpll_update`, `lsdc_pixpll_get_freq`, `lsdc_pixpll_print`, and `lsdc_pixpll_init`.

Control flow: init maps the chip-specific PLL register and allocates cached parameter storage. Atomic CRTC check calls compute; it first tries the static table, then brute-forces divider combinations under PLL constraints and tolerance. Commit calls update, which bypasses/off/powers down PLL, toggles parameter update, writes dividers, powers up, waits for lock, enables output, and unbypasses.

State and persistence: `lsdc_pixpll` stores MMIO register, descriptor-derived address, funcs, and private parameter cache. Hardware PLL state persists until next modeset or reset.

Dependencies and integration points: used by `lsdc_crtc.c` for mode validation/commit and debugfs clock reporting. Register locations come from `loongson_gfx_desc`.

Risks and test signals: compute can fail modes outside tolerance; update does not return lock failure. Divider arithmetic uses integer truncation. Test common VESA/CEA modes, table hits and misses, lock polling, suspend/resume, and debugfs frequency diff.
