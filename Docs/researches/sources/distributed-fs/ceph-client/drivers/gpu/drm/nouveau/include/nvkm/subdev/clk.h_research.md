# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/subdev/clk.h

## Purpose

This file defines the clock subdevice contract for Nouveau/NVKM. It covers clock domains, p-states, c-states, voltage coupling, read/calc/prog/tidy hooks, and per-generation clock constructors.

## Important APIs, Types, and Functions

Visible declarations include `nvbios_pll`, `nvkm_pll_vals`, `nv_clk_src`, `nvkm_cstate`, `list_head`, `nvkm_pstate`, `nvkm_pcie_speed`, `nvkm_domain`, `nvkm_clk`, `nvkm_clk_func`, `nvkm_subdev`, `work_struct`, `nvkm_device`, `nvkm_subdev_type`. Important callable entry points include `nvkm_clk_read`, `nvkm_clk_ustate`, `nvkm_clk_astate`, `nvkm_clk_dstate`, `nvkm_clk_tstate`, `nvkm_clk_pwrsrc`, `nv04_clk_new`, `nv40_clk_new`, `nv50_clk_new`, `g84_clk_new`. The file exposes the clock subdevice interface used by generation-specific Nouveau code.

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
