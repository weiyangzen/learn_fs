
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio.c

## Purpose

`xe_mmio.c` maps the GPU GTTMMADR BAR, partitions MMIO register windows by tile, and provides traced typed register read/write/wait helpers for the rest of the Xe driver. It also handles SR-IOV VF register access redirection and PF-side VF MMIO view initialization.

## Important APIs, Types, and Functions

- Probe/lifecycle: `xe_mmio_probe_early()`, `xe_mmio_probe_tiles()`, `mmio_fini()`, and `tiles_fini()`.
- Initialization: `xe_mmio_init()` and multi-tile helper `mmio_multi_tile_setup()`.
- Accessors: `xe_mmio_read8()`, `xe_mmio_write8()`, `xe_mmio_read16()`, `xe_mmio_write32()`, `xe_mmio_read32()`, `xe_mmio_rmw32()`, and `xe_mmio_write32_and_verify()`.
- Utility: `xe_mmio_in_range()`, `xe_mmio_read64_2x32()`, `xe_mmio_wait32()`, and `xe_mmio_wait32_not()`.
- SR-IOV PF helper under `CONFIG_PCI_IOV`: `xe_mmio_init_vf_view()`.

## Control Flow

Early probe maps the entire GTTMMADR BAR and initializes root tile registers to the first 4 MiB. Later tile probing assigns remote tile MMIO windows at 16 MiB strides. Register access first applies `xe_mmio_adjusted_addr()`, optionally flushes pending writes for a device workaround before reads, routes non-VF registers through SR-IOV VF mediated access when running as a VF, performs raw IO access otherwise, and emits `trace_xe_reg_rw` events.

The wait helpers poll masked register values until match or mismatch, using exponential backoff with either `udelay()` or `usleep_range()` depending on atomic context. The 64-bit read helper reads upper/lower/upper 32-bit values to reduce rollover races.

## State and Persistence Behavior

`xe->mmio.regs` owns the mapped BAR pointer until devm teardown. Each `struct xe_mmio` stores a tile backpointer, register-window pointer/size, optional adjustment fields, and optional SR-IOV VF GT override. Remote tile `regs` pointers are cleared on cleanup, while the root mapping is iounmapped.

## Dependencies and Integration Points

Nearly all hardware programming code uses these helpers, including IRQ, PAT, MOCS, OA, GSC, VRAM discovery, hwmon, and workarounds. The file depends on PCI BAR resources, Linux IO accessors, DRM managed cleanup, Xe tracing, SR-IOV VF helper functions, and generated workaround predicates.

## Risks and Edge Cases

- Register address adjustment must not split 64-bit register pairs; `xe_mmio_read64_2x32()` asserts this.
- `xe_mmio_in_range()` treats ranges as inclusive after address adjustment.
- VF redirection applies only when `reg.vf` is false; register definitions must mark VF-safe direct registers correctly.
- Poll timeouts are minimum waits and may exceed the requested time in sleeping context.
- BAR partitioning assumes a 16 MiB tile stride and 4 MiB register window.

## Test Signals

Probe tests should validate BAR map failure handling and multi-tile pointer setup. Unit or fault-injection tests should cover address adjustment, wait timeout/success paths, 64-bit rollover stabilization, SR-IOV VF routing, and trace-visible register access ordering.
