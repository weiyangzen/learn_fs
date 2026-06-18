<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/Kbuild -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/Kbuild

### Purpose

Build manifest for NVKM clock subdevice implementations and PLL helpers.

### Important APIs, types, and functions

Adds clock core and generation files (`base`, `nv04`, `nv40`, `nv50`, `g84`, `gt215`, `mcp77`, `gf100`, `gk104`, `gk20a`, `gm20b`, `gp10b`), optional `gk20a_devfreq.o`, and PLL helper objects `pllnv04.o` and `pllgt215.o`.

### Control flow

No runtime flow; Kbuild composes the clock subsystem objects selected by config.

### State and persistence behavior

No runtime state. Build composition determines which chipset clock constructors and PLL helpers are linked.

### Dependencies and integration points

Depends on parent Nouveau Kbuild and `CONFIG_PM_DEVFREQ` for Tegra GK20A devfreq support. Clock device-selection code relies on these objects.

### Risks

Missing entries break chipset support or optional devfreq integration. Stale entries cause build failures.

### Test signals

Source read size: 17 lines, 568 bytes. Nouveau build, allmodconfig with and without `CONFIG_PM_DEVFREQ`, and link checks for clock constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/Kbuild -->
