
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/priv.h

Purpose: private base interface for NVKM graphics engines.

Important APIs/types/functions: defines `nvkm_gr()` container helper, declares `nvkm_gr_ctor()` and `nv04_gr_idle()`, and defines `struct nvkm_gr_func`. The function table includes lifecycle hooks (`dtor`, `oneinit`, `init`, `fini` through engine base), interrupt handling, tile updates, channel creation, unit reporting, TLB flush, class lists, and optional method handlers depending on generation.

Control flow/state: no executable logic; it defines the vtable shape consumed by `gr/base.c` and implemented by all GR generations in this subset.

Dependencies/integration: includes public `engine/gr.h` and enum helpers, forward-declares FB tiles and channels. Risks are broad because any vtable contract change affects all GR variants. Test signals are whole-driver build coverage and runtime probe of at least one chip from each GR generation.
