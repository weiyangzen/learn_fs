# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/devinit/base.c

## Purpose
Implements the common NVKM devinit subdevice wrapper for VBIOS post execution, PLL setting, memory init, MMIO address filtering, power-disable hooks, and VGA register lock handling.

## Important APIs, types, and functions
Exports `nvkm_devinit_mmio()`, `nvkm_devinit_pll_set()`, `nvkm_devinit_meminit()`, `nvkm_devinit_disable()`, `nvkm_devinit_post()`, and `nvkm_devinit_ctor()`. Subdevice hooks are `preinit`, `init`, `fini`, and `dtor`.

## Control flow
Preinit runs generation-specific preinit, applies one-shot `NvForcePost`, and unlocks extended VGA CRTC registers. Post calls the generation post callback with the current `post` flag, then disables engines not initialized by firmware. Fini forces full reinit on non-poweroff suspend. Dtor calls generation dtor and re-locks CRTC registers.

## State and persistence
`struct nvkm_devinit` stores the function table, `post`, and `force_post`. Hardware state includes VGA lock state, init-script effects, disabled engine state, and any generation-specific PLL/memory programming.

## Dependencies and integration points
Depends on `nvkm_subdev`, config option parsing, VGA helpers, and generation-specific function tables.

## Risks
The post flag controls whether VBIOS scripts execute; wrong detection can skip needed initialization or rerun scripts unnecessarily. `nvkm_devinit_disable()` always returns zero, so callers do not learn disable failures.

## Test signals
Boot with and without `NvForcePost`, suspend/resume, VGA CRTC lock/unlock behavior, VBIOS post logs, and engine disable state after init.
