<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-mmio.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-mmio.c

Purpose: Implements regmap access for memory-mapped I/O regions, including endian-specific accessors, no-increment transfers, optional relaxed MMIO, I/O port mode, and optional clock gating.

Important APIs/types/functions: `struct regmap_mmio_context` stores base address, value width, endian flag, optional clock, and selected read/write callbacks. Public APIs are `__regmap_init_mmio_clk()`, `__devm_regmap_init_mmio_clk()`, `regmap_mmio_attach_clk()`, and `regmap_mmio_detach_clk()`. Helper selection occurs in `regmap_mmio_gen_context()`.

Control flow: Context generation validates register bits, pad bits, minimum stride, and incompatible relaxed/I/O port settings. It selects read/write functions by value endian, value width, relaxed mode, and I/O port mode. Optional clocks are acquired and prepared. Normal read/write enable the clock, perform one accessor call, then disable it. No-increment operations use `reads*`/`writes*` helpers for little-endian or byte data, with explicit byte swapping for big-endian multi-byte values. Freeing unprepares and possibly puts the clock.

State and persistence behavior: Persistent runtime state is the allocated context held by the regmap. Attached clocks are marked with `attached_clk` so free does not `clk_put()` externally owned clocks. Hardware register persistence is the MMIO region itself; regmap cache behavior is handled by the core.

Dependencies and integration points: Depends on Linux I/O accessors, clock framework, endian/swab helpers, and regmap bus callbacks. Integrates with device drivers that expose `void __iomem *` register windows.

Risks: Wrong endian/width/stride settings directly corrupt register access. Relaxed MMIO is forbidden with I/O port mode. `regmap_mmio_detach_clk()` sets `ctx->clk = NULL`; later read/write checks use `IS_ERR(ctx->clk)`, so callers must avoid normal access after detach unless a new valid clock state is expected. No bounds checking is done against the mapped resource size. Big-endian no-increment paths emulate operations because native optimized helpers are unavailable.

Test signals: Validate config rejection, accessor selection, clock prepare/enable/disable/unprepare paths, big-endian no-increment byte swapping, relaxed vs ordered access, and attached clock ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-mmio.c -->
