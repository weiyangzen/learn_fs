# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/bios/therm.h

## Purpose

This file defines the VBIOS therm table parser contract for Nouveau/NVKM. It covers the parser declarations and data structures for the Nouveau VBIOS `therm` table family. It exports parser helpers such as `nvbios_therm_sensor_parse, nvbios_therm_fan_parse`.

## Important APIs, Types, and Functions

Visible declarations include `nvbios_therm_threshold`, `nvbios_therm_sensor`, `nvbios_therm_fan_type`, `nvbios_therm_trip_point`, `nvbios_therm_fan_mode`, `nvbios_therm_fan`, `nvbios_therm_domain`, `nvkm_bios`, `nvbios_therm_sensor_parse`, `nvbios_therm_fan_parse`, `NVKM_TEMP_FAN_TRIP_MAX`. Important callable entry points include `nvbios_therm_sensor_parse`, `nvbios_therm_fan_parse`. The file exposes the VBIOS therm table parser interface used by generation-specific Nouveau code.

## Control Flow

This header has no standalone executable flow; it shapes the control flow of the implementation files that include it. Device setup selects the appropriate constructor or function table, higher layers call the declared helpers through NVKM lifecycle or user-object paths, and generation-specific code fills the hardware-specific behavior behind the common bios interface.

## State and Persistence Behavior

The file itself stores no runtime state. The declared structures and callbacks describe state owned by the corresponding NVKM object, including locks, hardware object handles, memory references, event state, or parsed firmware/BIOS data as applicable. That state usually persists from subdevice/engine construction until fini or device removal.

## Dependencies and Integration Points

It integrates with NVKM device layout, subdevice lifecycle, NVIF user objects, firmware/BIOS parsing, memory management, interrupt handling, and chip-family constructor selection. Include dependencies keep consumers tied to the relevant core, engine, or subdevice abstractions.

## Risks

The main risk is contract drift: signatures, struct fields, or constructor availability must match generation-specific implementations and device selection tables. Misinterpreting ownership, locking, or units in these declarations can produce runtime faults even though the header compiles.

## Test Signals

Build coverage across enabled GPU generations, module load/unload, constructor selection on matching chipsets, lifecycle init/fini paths, suspend/resume, and targeted tests for each declared helper are the useful signals.
