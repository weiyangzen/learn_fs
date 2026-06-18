# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/volt.h

## Purpose

This file defines the voltage subdevice contract for Nouveau/NVKM. It covers voltage VID tables, range maps, get/set operations, speedo readings, and per-generation voltage constructors.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_volt`, `nvkm_volt_func`, `nvkm_subdev`, `nvkm_device`, `nvkm_subdev_type`, `nvkm_volt_map`, `nvkm_volt_map_min`, `nvkm_volt_get`, `nvkm_volt_set_id`, `nv40_volt_new`, `gf100_volt_new`, `gf117_volt_new`, `gk104_volt_new`, `gk20a_volt_new`. Important callable entry points include `nvkm_volt_map`, `nvkm_volt_map_min`, `nvkm_volt_get`, `nvkm_volt_set_id`, `nv40_volt_new`, `gf100_volt_new`, `gf117_volt_new`, `gk104_volt_new`, `gk20a_volt_new`, `gm20b_volt_new`. The visible chip-family constructors are `nv40_volt_new, gf100_volt_new, gf117_volt_new, gk104_volt_new, gk20a_volt_new, gm20b_volt_new`; they bind the generic voltage subdevice role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common subdevice interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
