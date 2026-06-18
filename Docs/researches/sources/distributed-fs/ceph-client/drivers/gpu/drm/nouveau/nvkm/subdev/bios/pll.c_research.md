<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/pll.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/pll.c

### Purpose

Parser for PLL limit tables and legacy PLL register mappings. It translates PLL type or register into frequency, divider, input, and post-divider constraints.

### Important APIs, types, and functions

`nvbios_pll_parse()` is the public API. Internal helpers include `pll_limits_table()`, legacy mapping arrays for NV04/NV40/NV50/G84, `pll_map_reg()`, and `pll_map_type()`.

### Control flow

The parser first locates BIT `C` PLL limits or BMP fallback data, then either matches by register or logical PLL type. Versions 0x10 through newer layouts decode VCO min/max, input limits, M/N bounds, post-divider limits, bias, and reference clocks with version-specific offsets.

### State and persistence behavior

No persistent state. Returned `struct nvbios_pll` constrains later PLL programming but the file itself only reads firmware data.

### Dependencies and integration points

Depends on BIT/BMP helpers, device card type/chipset, VGA/devinit PLL programming consumers, and generic BIOS reads.

### Risks

Incorrect limits can produce invalid PLL programming and display/core/memory instability. Legacy fallback maps are chipset-specific and easy to regress.

### Test signals

Source read size: 440 lines, 12113 bytes. PLL parser fixtures, clock programming tests, display pixel-clock tests, reclocking under load, and comparison against known PLL limits from VBIOS dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/pll.c -->
