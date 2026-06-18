# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/gr/Kbuild

Purpose: declares the Nouveau graphics engine object files that build into `nvkm-y`. It includes the base GR engine, generation-specific GR engines from NV04 through GA102, and context-generation files from NV40 through GA102.

Important APIs and data: entries append `nvkm/engine/gr/*.o` files to `nvkm-y`. The first block lists engine implementations such as `base.o`, `gf100.o`, `gk104.o`, `gm200.o`, `gv100.o`, `tu102.o`, and `ga102.o`; the second block lists context generators such as `ctxgf100.o`, `ctxgf104.o`, `ctxgk104.o`, `ctxgm200.o`, `ctxgv100.o`, `ctxtu102.o`, and `ctxga102.o`.

Control flow: no runtime control flow. Kbuild uses these entries to compile and link the GR implementation into the kernel module/built-in driver.

State and persistence: no runtime state. Build configuration state is the ordered object list.

Dependencies and integration: integrates the GR subtree into the larger Nouveau NVKM build. FIFO engine-object enumeration and context binding depend on these GR objects being linked.

Risks: missing an object file causes unresolved symbols or unsupported GPU generations; stale entries can break builds if files are removed; build order can matter when archives resolve symbols.

Test signals: kernel/module build success, no unresolved GR context symbols, and probe coverage for listed generations.
