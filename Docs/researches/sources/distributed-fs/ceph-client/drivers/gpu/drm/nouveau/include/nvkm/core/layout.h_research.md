# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/layout.h

## Purpose

This file defines the device layout contract for Nouveau/NVKM. It covers the macro-expanded map from subdevice/engine type to field name and struct type inside the generated NVKM device layout.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_fsp`, `nvkm_gsp`, `nvkm_top`, `nvkm_vfn`, `nvkm_pci`, `nvkm_bios`, `nvkm_devinit`, `nvkm_subdev`, `nvkm_gpio`, `nvkm_i2c`, `nvkm_fuse`, `nvkm_mc`, `nvkm_bus`, `nvkm_timer`. Important callable entry points include constructor/function declarations selected by including modules. The file exposes the device layout interface used by generation-specific Nouveau code.

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
