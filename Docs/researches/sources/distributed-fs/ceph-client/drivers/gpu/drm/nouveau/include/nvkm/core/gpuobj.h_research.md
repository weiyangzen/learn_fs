# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/gpuobj.h

## Purpose

This file defines the GPU object contract for Nouveau/NVKM. It covers parented GPU-resident objects with optional child heaps, memory wrappers, register-style accessors, VMM map hooks, and memcpy helpers.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_gpuobj`, `nvkm_gpuobj_func`, `nvkm_memory`, `nvkm_mm_node`, `nvkm_mm`, `nvkm_vmm`, `nvkm_vma`, `nvkm_device`, `nvkm_gpuobj_new`, `nvkm_gpuobj_del`, `nvkm_gpuobj_wrap`, `nvkm_gpuobj_memcpy_to`, `nvkm_gpuobj_memcpy_from`, `NVOBJ_FLAG_ZERO_ALLOC`. Important callable entry points include `nvkm_gpuobj_new`, `nvkm_gpuobj_del`, `nvkm_gpuobj_wrap`, `nvkm_gpuobj_memcpy_to`, `nvkm_gpuobj_memcpy_from`. The visible chip-family constructors are `nvkm_gpuobj_new`; they bind the generic GPU object role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common core interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
