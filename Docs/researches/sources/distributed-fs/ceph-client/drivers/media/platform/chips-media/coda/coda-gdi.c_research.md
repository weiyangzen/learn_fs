# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda-gdi.c

`coda-gdi.c` programs CODA960 GDI address-translation registers for linear and macroblock-tiled frame maps. Its single exported API, `coda_set_gdi_regs(struct coda_ctx *ctx)`, is called before CODA960 BIT and direct JPEG picture runs.

The file is built around static translation tables: `xy2ca_zero_map`, `xy2ca_tiled_map`, and `rbc2axi_tiled_map`. The `XY2()` and `RBC()` macros encode selector/bit fields for `CODA9_GDI_XY2_*`, `CODA9_GDI_XY2_RBC_CONFIG`, and `CODA9_GDI_RBC2_AXI_*` registers.

Control flow is simple: linear map mode writes zero translation entries and disables XY2RBC conversion; tiled macroblock raster mode writes the tiled XY-to-CA map, enables tiled XY2RBC with horizontal CA increment and 16x8 geometry, clears BA/RA maps, and writes all RBC-to-AXI entries.

The file has no dynamic state beyond hardware registers. It depends on `coda_write()`, `struct coda_ctx`, `ctx->tiled_map_type`, and CODA9 register definitions. Risks are hardware-specific swizzle errors, chroma corruption if tiled mode is used with unsupported layouts, and accidental calls on non-CODA960 hardware. Test with linear and tiled NV12 paths, VDOA/YUYV conversion, context switches between tiled and linear formats, and register traces.
