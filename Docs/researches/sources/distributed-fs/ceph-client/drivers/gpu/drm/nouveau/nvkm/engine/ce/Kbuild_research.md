## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/Kbuild

### Purpose
This Kbuild fragment builds the copy engine implementations across Nouveau-supported generations from GT215 through GB202 helper support.

### Important APIs, types, and functions
It adds object files for `gt215`, `gf100`, `gk104`, `gm107`, `gm200`, `gp100`, `gp102`, `gv100`, `tu102`, `ga100`, `ga102`, and `gb202` CE sources.

### Control flow
There is no runtime flow. The build list ensures each generation-specific constructor and shared interrupt/helper symbol is available.

### State and persistence behavior
The file affects build composition only. Runtime state is in compiled CE engine instances selected by `device/base.c`.

### Dependencies
It depends on `engine/Kbuild`, the CE sources, generated firmware headers for GT215/GF100, and shared engine/falcon infrastructure.

### Integration points
The chipset table references these constructors with per-chip instance masks. `priv.h` shares helpers among CE implementation files, so all listed objects must be linked together.

### Risks
Forgetting a new object here creates unresolved symbols or missing support for a chipset entry. Removing an older object can break legacy copy engines even if newer platforms still build.

### Test signals
Allmodconfig or Nouveau-enabled kernel builds, link checks for constructor symbols, and device probe across CE generations verify this fragment.
