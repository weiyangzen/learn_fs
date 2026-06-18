# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_pixpll.h

Purpose: declares Loongson pixel PLL parameters, function table, object state, and initialization helper.

Important APIs/types/functions: `struct lsdc_pixpll_parms`, `struct lsdc_pixpll_funcs`, `struct lsdc_pixpll`, and `lsdc_pixpll_init`.

Control flow: no executable flow; CRTC code calls function table methods through initialized `lsdc_pixpll`.

State and persistence: pixel PLL object stores DRM device, register address/size, MMIO pointer, funcs, and private parameter storage.

Dependencies and integration points: included by `lsdc_drv.h`; implemented by `lsdc_pixpll.c`; consumed by CRTC private state.

Risks and test signals: future chips with different PLL layout need alternate funcs. Test both current chip descriptors and PLL cleanup.
