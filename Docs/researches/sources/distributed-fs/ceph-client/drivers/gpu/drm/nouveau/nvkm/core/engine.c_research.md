# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/engine.c

## Purpose
This file provides the common NVKM engine wrapper around subdevice lifecycle, interrupts, reset, tile updates, and references.

## Important APIs, Types, and Functions
Public functions include `nvkm_engine_ctor`, `nvkm_engine_new_`, `nvkm_engine_ref`, `nvkm_engine_unref`, `nvkm_engine_reset`, `nvkm_engine_tile`, and `nvkm_engine_chsw_load`. It exposes `const struct nvkm_subdev_func nvkm_engine`.

## Control Flow
Engine construction initializes the embedded subdevice, sets the use refcount to zero, honors config options that can disable the engine, and initializes the lock. Subdevice callbacks delegate preinit/oneinit/init/fini/intr/info/dtor to engine-specific function pointers. Init also reapplies framebuffer tile regions. Reset calls engine reset if present or power-cycles the subdevice.

## State and Persistence Behavior
State includes the engine function table, embedded subdev, lock, and subdev use refcount. Tile state comes from framebuffer subdev and is programmed into engines.

## Dependencies and Integration Points
It depends on NVKM subdev, device option parsing, framebuffer tiling, and engine-specific implementations. Ioctl class creation may take engine references.

## Risks
Config-disabled engines return `-ENODEV`. Fallback reset can disrupt state if engine-specific reset is required. Tile replay assumes framebuffer tile data is initialized.

## Test Signals
Signals include engine init/fini/reset, config option disablement, interrupt delegation, tile updates, ref/unref behavior, and engine-specific oneinit failures.
