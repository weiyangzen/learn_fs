<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu.h

## Purpose
`amdgpu.h` is the central private header for the amdgpu kernel driver. It aggregates subsystem headers, declares global module parameters, defines central structures such as `struct amdgpu_device`, exposes ASIC callback contracts, declares core device/KMS/reset/ACPI APIs, and provides the register-access macros used by much of the driver.

Because almost every amdgpu subsystem includes or is included by this header, it acts as an internal integration contract for memory management, display, rings, firmware, interrupts, power management, virtualization, RAS/ACA/CPER, KFD, reset, ACPI, and user queue support.

## Important APIs, types, and functions
- Global module parameters include memory limits, scheduling controls, VM settings, display/DC options, power/RAS flags, reset method, MES, SmartShift, partitioning, WBRF, and KFD-related knobs.
- `struct amdgpu_device` is the driver-wide state object. It embeds PCI/DRM devices, ASIC identity, BIOS state, MMIO and doorbell state, GMC/GART/VM managers, memory manager/writeback, display, rings and schedulers, IRQ, powerplay/PM, IP block structs, firmware, PSP, UMC/DF/SMUIO/MCA/ACA/CPER, reset state, suspend/runtime PM state, RAS/debug flags, isolation state, UID/UMA state, and the trailing `struct amdgpu_kfd_dev`.
- `struct amdgpu_asic_funcs` defines ASIC-specific operations for BIOS access, register reads, VGA state, resets, clocks, PCIe lanes/usage, HDP cache management, BACO, stable pstate, video codec query, extended SMN addressing, and register-state export.
- Reset-related types include `enum amd_reset_method`, reset masks, init levels, `struct amdgpu_pcie_reset_ctx`, and reset helper prototypes.
- Memory and scheduling types include `struct amdgpu_sa_manager`, `struct amdgpu_wb`, `struct amdgpu_fpriv`, `struct amdgpu_mqd_prop`, `struct amdgpu_mqd`, and UMA carveout structures.
- Register macros include `RREG32`, `WREG32`, KIQ/no-KIQ variants, PCIe/SMC/UVD/DIDT/GC_CAC/audio endpoint accessors, field helpers, BIOS byte readers, and ASIC callback wrappers.
- Public internal prototypes cover device init/fini, reset/recovery, VRAM/MMIO access, KMS driver hooks, ACPI helpers, GPU instance registration, PCI error recovery, clock/power gating, bus-status checking, and UID access.

## Control flow
The header itself has compile-time flow: include guards, configuration-dependent declarations or stubs, and inline helpers. Runtime flow is defined by its contracts. Device load code populates `struct amdgpu_device`, assigns `asic_funcs`, initializes IP blocks, then calls functions declared here for hardware init, KMS, ACPI, reset, and power management.

Register access macros route through lower-level functions such as `amdgpu_device_rreg()`, `amdgpu_device_wreg()`, KIQ register accessors, PCIe register functions, and ASIC callbacks. ASIC wrapper macros call through `adev->asic_funcs`, sometimes with null checks for optional callbacks.

Configuration sections define behavior when optional features are absent. For example, without `CONFIG_ACPI`, ACPI functions are inline stubs returning harmless defaults or `-EINVAL`; without `CONFIG_VGA_SWITCHEROO`, ATPX helpers are no-ops; suspend-specific helpers default to false without suspend support.

## State and persistence behavior
`struct amdgpu_device` is the authoritative runtime state for a GPU instance. It persists for the life of the DRM device and owns or references almost all subsystem state: VM hubs, IP blocks, firmware, PSP context, display manager, reset domain, ACPI notifier, RAS lists, PCI saved state, work items, locks, xarrays, counters, and KFD state.

Persistent hardware/firmware data appears as loaded BIOS bytes, saved PCI state, firmware descriptors, RAS/CPER-related runtime accounting, and module parameter choices, but the header does not itself perform persistence. Its atomic counters track reset count, VRAM loss, bytes moved, evictions, page faults, and memory pinning across runtime operations.

## Dependencies and integration points
The header integrates the Linux kernel, DRM, TTM, KFD, AMD shared, display, memory, firmware, interrupt, RAS, CPER, and IP-block layers. Its include list is intentionally broad because `struct amdgpu_device` embeds many subsystem structs by value.

Major integration points are the DRM/KMS driver entry points, TTM/GEM BO management, SOC/IP register helpers, reset framework, ACPI ATIF/ATCS support, VGA switcheroo/ATPX, KFD HSA bridge, MES/user queues, RAS/ACA/CPER error handling, and power-management interfaces.

## Risks and edge cases
This header has high blast radius. Adding includes, fields, or macros can affect build times, circular dependencies, structure layout, and configuration-specific builds. The trailing `struct amdgpu_kfd_dev kfd` is explicitly noted as last because it contains a flexible-array-member-like `dev_pagemap`; moving it can break layout assumptions.

Register macros assume an `adev` variable exists in scope, which is convenient but fragile. ASIC wrapper macros dereference callback pointers, and only some wrappers check for optional callbacks. Call sites must ensure `adev->asic_funcs` is populated and the specific operation is supported.

State ordering matters in `struct amdgpu_device`: locks protect specific members, reset and suspend flags interact with workqueues and PCI error recovery, and many embedded subsystem structs are initialized in staged IP-block order. Configuration stubs must preserve behavior expected by callers on non-ACPI, non-HSA, or non-suspend builds.

## Test signals
Strong test signals are full amdgpu builds across multiple Kconfig combinations, successful probe/remove on discrete and APU devices, reset recovery, suspend/resume and runtime PM, KMS open/close/ioctls, TTM memory pressure, KFD initialization, RAS/ACA query paths, and register read/write smoke tests. Static signals include no circular include regressions, no missing stubs for disabled configs, and no warnings around macro callback access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu.h -->
