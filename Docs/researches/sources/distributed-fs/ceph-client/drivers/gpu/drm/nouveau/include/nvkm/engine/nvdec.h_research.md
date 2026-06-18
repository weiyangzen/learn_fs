# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/engine/nvdec.h

## Purpose

This file defines the NVDEC video decoder contract for Nouveau/NVKM. It covers NVDEC video decoder engine declarations with per-instance engine objects, optional Falcon-backed firmware state, and constructors for supported GPU generations.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_nvdec`, `nvkm_nvdec_func`, `nvkm_engine`, `nvkm_falcon`, `nvkm_device`, `nvkm_subdev_type`, `gm107_nvdec_new`, `tu102_nvdec_new`, `ga102_nvdec_new`. Important callable entry points include `gm107_nvdec_new`, `tu102_nvdec_new`, `ga102_nvdec_new`. The visible chip-family constructors are `gm107_nvdec_new, tu102_nvdec_new, ga102_nvdec_new`; they bind the generic NVDEC video decoder role to generation-specific implementations selected by the device table.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common engine interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
