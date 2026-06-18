# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/pmu.h

## Purpose

This file defines the PMU subdevice contract for Nouveau/NVKM. It covers Falcon-backed power-management controller messaging, fan/power-gating hooks, and memory-script command construction.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_pmu`, `nvkm_pmu_func`, `nvkm_subdev`, `nvkm_falcon`, `nvkm_falcon_qmgr`, `nvkm_falcon_cmdq`, `nvkm_falcon_msgq`, `completion`, `mutex`, `work_struct`, `nvkm_device`, `nvkm_subdev_type`, `nvkm_memx`, `nvkm_pmu_send`. Important callable entry points include `nvkm_pmu_send`, `nvkm_pmu_pgob`, `nvkm_pmu_fan_controlled`, `gt215_pmu_new`, `gf100_pmu_new`, `gf119_pmu_new`, `gk104_pmu_new`, `gk110_pmu_new`, `gk208_pmu_new`, `gk20a_pmu_new`. The visible chip-family constructors are `gt215_pmu_new, gf100_pmu_new`; they bind the generic PMU subdevice role to generation-specific implementations selected by the device table.

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
