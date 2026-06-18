# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/falcon/priv.h

## Purpose
Provides a private inline wrapper for enabling a falcon through its function table.

## Important APIs, types, and functions
`nvkm_falcon_enable()` calls `falcon->func->enable` when present and otherwise succeeds with zero.

## Control flow, state, and persistence
No persistent state is declared. The wrapper centralizes optional enable handling for reset and boot paths.

## Dependencies and integration points
Includes public `core/falcon.h`. Used by generic falcon reset and generation code.

## Risks and test signals
If a falcon requires enable logic but its function pointer is missing, this wrapper silently succeeds. Runtime firmware boot and register access are the validation signals.
