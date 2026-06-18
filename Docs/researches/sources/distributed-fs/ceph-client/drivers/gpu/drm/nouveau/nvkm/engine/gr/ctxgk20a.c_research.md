# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/ctxgk20a.c

`ctxgk20a.c` implements the Tegra GK20A graphics context main sequence. Unlike desktop Kepler files, it does not provide static hub/GPC/TPC packs; it defines a custom `main` callback for the SoC path and exports a compact `gk20a_grctx` function table.

The main function is `gk20a_grctx_generate_main()`, and the exported object is `const struct gf100_grctx_func gk20a_grctx`. The callback table reuses GK104 bundle/pagepool generation, GF117 attributes, GF100 SM/TPC helpers, GF117 ROP mapping, and GK104 alpha/beta tables.

`gk20a_grctx_generate_main()` writes the software MMIO context, waits for idle, temporarily clears idle timeout register `0x404154`, emits attribute buffer and attribute layout, applies unknown MMIO setup, floorsweeps, clears the eight distribution skip registers, writes `0x405b00` from `tpc_total` and `gpc_nr`, sets bit `0x08000000` in `0x5044b0`, restores idle timeout, loads method and ICMD streams, and finally patches pagepool and bundle buffers. The table sets bundle size `0x1800`, FIFO depth `0x62`, token limit `0x100`, and GK20A-specific attribute sizes.

The file depends on `ctxgf100.h`, `gf100.h`, and `subdev/mc.h`. It integrates with Tegra GK20A GR initialization where firmware/device behavior differs enough to need a custom main sequence but still uses GF100-family context patch helpers.

Risks include idle-timeout handling, missing static packs that desktop chips rely on, SoC-specific register `0x5044b0`, and attribute sizing. Test signals are GK20A/Tegra boot, channel creation, graphics workloads under runtime PM, and logs around idle waits or context-load failures.
