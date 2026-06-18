# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/i2c.h

## Purpose

This file defines the I2C subdevice contract for Nouveau/NVKM. It covers I2C bus and AUX pad/port descriptors, DCB integration, transfer hooks, and per-generation constructors.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_i2c_bus_probe`, `i2c_board_info`, `nvkm_i2c_bus`, `nvkm_i2c_bus_func`, `nvkm_i2c_pad`, `mutex`, `list_head`, `i2c_adapter`, `nvkm_i2c_aux`, `nvkm_i2c_aux_func`, `nvkm_i2c`, `nvkm_i2c_func`, `nvkm_subdev`, `nvkm_event`. Important callable entry points include `nvkm_i2c_bus_acquire`, `nvkm_i2c_bus_release`, `nvkm_i2c_bus_probe`, `nvkm_i2c_aux_monitor`, `nvkm_i2c_aux_acquire`, `nvkm_i2c_aux_release`, `nvkm_i2c_aux_xfer`, `nvkm_i2c_aux_lnk_ctl`, `nv04_i2c_new`, `nv4e_i2c_new`. The file exposes the I2C subdevice interface used by generation-specific Nouveau code.

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
