## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/ce/priv.h

### Purpose
`priv.h` is the internal CE engine header that shares constructors, interrupt helpers, context class binders, Ampere callbacks, and Blackwell helpers among CE implementation files.

### Important APIs, types, and functions
It declares `r535_ce_new()`, `gt215_ce_intr()`, `gk104_ce_intr()`, `gp100_ce_intr()`, external `gv100_ce_cclass`, `ga100_ce_oneinit()`, `ga100_ce_init()`, `ga100_ce_fini()`, `ga100_ce_nonstall()`, and `gb202_ce_grce_mask()`.

### Control flow
The header has no executable flow. It allows generation-specific C files to reuse shared implementation pieces without exporting them through the public `engine/ce.h` API.

### State and persistence behavior
It owns no state. The declarations refer to state managed by CE engines, subdevices, interrupt handles, and GPU objects.

### Dependencies
It includes `engine/ce.h`, which exposes public CE constructors and Falcon engine definitions.

### Integration points
All CE implementation C files include this header. It is the private link between GT215/GF100 Falcon helpers, Kepler/Pascal interrupt handlers, Volta context binding, Ampere interrupt lifecycle, R535/GSP-managed paths, and Blackwell hardware helpers.

### Risks
Prototype drift causes build failures or subtle ABI mismatches within the CE directory. Adding declarations here without corresponding Kbuild entries can still leave unresolved symbols.

### Test signals
Compile coverage of every CE object, link checks for shared symbols, and cross-generation CE probe tests validate this header.
