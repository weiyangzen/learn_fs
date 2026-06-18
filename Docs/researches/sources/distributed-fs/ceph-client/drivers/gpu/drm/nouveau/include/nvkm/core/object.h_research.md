# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/object.h

## Purpose

This file defines the NVKM object model contract for Nouveau/NVKM. It covers base object lifetime, init/fini/method/notify/map/bind hooks, object insertion/removal, and client handle lookup.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_event`, `nvkm_gpuobj`, `nvkm_uevent`, `nvkm_object`, `nvkm_object_func`, `nvkm_client`, `nvkm_engine`, `list_head`, `rb_node`, `nvkm_object_map`, `nvkm_suspend_state`, `nvkm_oclass`, `nvkm_object_ctor`, `nvkm_object_new_`. Important callable entry points include `nvkm_object_ctor`, `nvkm_object_new_`, `nvkm_object_new`, `nvkm_object_del`, `nvkm_object_init`, `nvkm_object_fini`, `nvkm_object_mthd`, `nvkm_object_ntfy`, `nvkm_object_map`, `nvkm_object_unmap`. The visible chip-family constructors are `nvkm_object_new_, nvkm_object_new`; they bind the generic NVKM object model role to generation-specific implementations selected by the device table.

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
