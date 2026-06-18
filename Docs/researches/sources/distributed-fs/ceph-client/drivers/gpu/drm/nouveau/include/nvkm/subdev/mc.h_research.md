# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/mc.h

## Purpose

This file defines the master control subdevice contract for Nouveau/NVKM. It covers engine enable/disable/reset/intr-mask helpers and chipset-specific master-control constructors.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_mc`, `nvkm_mc_func`, `nvkm_subdev`, `nvkm_intr`, `nvkm_device`, `nvkm_subdev_type`, `nvkm_mc_enable`, `nvkm_mc_disable`, `nvkm_mc_enabled`, `nvkm_mc_reset`, `nvkm_mc_intr_mask`, `nvkm_mc_unk260`, `nv04_mc_new`, `nv11_mc_new`. Important callable entry points include `nvkm_mc_enable`, `nvkm_mc_disable`, `nvkm_mc_enabled`, `nvkm_mc_reset`, `nvkm_mc_intr_mask`, `nvkm_mc_unk260`, `nv04_mc_new`, `nv11_mc_new`, `nv17_mc_new`, `nv44_mc_new`. The visible chip-family constructors are `nv04_mc_new, nv11_mc_new, nv17_mc_new, nv44_mc_new, nv50_mc_new, g84_mc_new`; they bind the generic master control subdevice role to generation-specific implementations selected by the device table.

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
