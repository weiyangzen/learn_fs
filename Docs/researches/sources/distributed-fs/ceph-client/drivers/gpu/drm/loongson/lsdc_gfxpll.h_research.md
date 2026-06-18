# sources/distributed-fs/ceph-client/drivers/gpu/drm/loongson/lsdc_gfxpll.h

Purpose: declares Loongson shared GFX PLL parameters, operation table, object state, and creation helper.

Important APIs/types/functions: `struct loongson_gfxpll_parms`, `struct loongson_gfxpll_funcs`, `struct loongson_gfxpll`, and `loongson_gfxpll_create`.

Control flow: no executable flow; the function table abstracts init/update/rate/print operations.

State and persistence: PLL object stores DRM device, MMIO, register location, funcs, and cached divider parameters.

Dependencies and integration points: included by `lsdc_drv.h`, used by core creation and debugfs.

Risks and test signals: future chip variants may need different funcs. Test descriptor offsets and debugfs reporting.
