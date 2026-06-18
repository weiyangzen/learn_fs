# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgm20b.c

`ctxgm20b.c` implements the Tegra GM20B graphics context main sequence. It mirrors the SoC-specific GK20A flow but uses Maxwell/GM107 buffer and attribute generation plus GM200 SMID configuration.

The main function is `gm20b_grctx_generate_main()`, and the exported object is `const struct gf100_grctx_func gm20b_grctx`. The table uses `gm107_grctx_generate_bundle()`, `gm107_grctx_generate_pagepool()`, `gm107_grctx_generate_attrib_cb()`, `gm107_grctx_generate_attrib()`, `gm107_grctx_generate_sm_id()`, and `gf117_grctx_generate_rop_mapping()`.

`gm20b_grctx_generate_main()` writes SW context MMIO, waits idle, temporarily clears idle timeout `0x404154`, emits attribute buffer and layout, applies unknown MMIO setup, floorsweeps, clears `0x4064d0` skip registers, writes GPC/TPC count to `0x405b00`, derives `0x408908` from `0x410108 | 0x80000000`, builds and writes a packed TPC mask to `0x4041c4`, emits GM200 SMID config, restores idle timeout, and emits method, ICMD, pagepool, and bundle state. The function table uses bundle size `0x1800`, token limit `0x1c0`, and GM20B-specific attribute counts.

The file depends on `ctxgf100.h` and GM107/GM200 helpers. It integrates with Tegra GM20B GR initialization where the SoC path needs a custom main sequence and smaller resource limits than desktop Maxwell.

Risks include SoC-specific register ordering, idle wait failures, TPC mask packing, and SMID map generation. Test signals are GM20B/Tegra boot, runtime-PM transitions, graphics workloads with multiple channels, and absence of context-load or idle-timeout messages.
