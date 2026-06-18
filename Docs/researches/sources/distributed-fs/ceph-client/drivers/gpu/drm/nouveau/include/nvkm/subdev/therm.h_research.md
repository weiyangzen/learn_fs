# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/therm.h

## Purpose

This file defines the thermal subdevice contract for Nouveau/NVKM. It covers thermal thresholds, fan modes, sensor attributes, clock-gating packs, fan PWM/Tach operations, and thermal constructors.

## Important APIs, Types, and Functions

Visible declarations include `nvkm_therm_thrs_direction`, `nvkm_therm_thrs_state`, `nvkm_therm_thrs`, `nvkm_therm_fan_mode`, `nvkm_therm_attr_type`, `nvkm_therm_clkgate_init`, `nvkm_therm_clkgate_pack`, `nvkm_therm`, `nvkm_therm_func`, `nvkm_subdev`, `nvkm_alarm`, `nvbios_therm_trip_point`, `nvbios_therm_sensor`, `nvkm_fan`. Important callable entry points include `nvkm_therm_temp_get`, `nvkm_therm_fan_sense`, `nvkm_therm_cstate`, `nvkm_therm_clkgate_init`, `nvkm_therm_clkgate_enable`, `nvkm_therm_clkgate_fini`, `nv40_therm_new`, `nv50_therm_new`, `g84_therm_new`, `gt215_therm_new`. The file exposes the thermal subdevice interface used by generation-specific Nouveau code.

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
