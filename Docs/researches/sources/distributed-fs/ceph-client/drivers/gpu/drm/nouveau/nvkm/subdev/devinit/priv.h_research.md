# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/priv.h

## Purpose
Defines the private devinit function-table contract and shared constructor prototypes.

## Important APIs, types, and functions
Defines `struct nvkm_devinit_func` with optional dtor/preinit/init/post/mmio/meminit/pll_set/disable hooks. Declares `r535_devinit_new()`, `nvkm_devinit_ctor()`, `nvkm_devinit_disable()`, `nv04_devinit_post()`, and `tu102_devinit_post()`.

## Control flow
No runtime flow in the header. Hook presence drives `devinit/base.c` behavior.

## State and persistence
No state is stored here; function tables describe per-generation persistent behavior.

## Dependencies and integration points
Included by all devinit implementations and by the R535 wrapper.

## Risks
Missing a mandatory hook for a generation can cause null dereferences in wrappers like `nvkm_devinit_pll_set()`, which assumes `pll_set` exists.

## Test signals
Build coverage and constructor/init/post paths for all devinit generations.
