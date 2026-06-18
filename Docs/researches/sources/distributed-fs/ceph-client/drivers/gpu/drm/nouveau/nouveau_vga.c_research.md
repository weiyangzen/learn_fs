# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_vga.c

## Purpose
This file integrates Nouveau with VGA arbitration and vga_switcheroo. It controls legacy VGA decode registers, handles hybrid-GPU power switching, and wires hotplug reprobe behavior.

## Important APIs, Types, and Functions
Main entry points are `nouveau_vga_init` and `nouveau_vga_fini`. Internal switcheroo callbacks are `nouveau_switcheroo_set_state`, `nouveau_switcheroo_reprobe`, `nouveau_switcheroo_can_switch`, and `nouveau_vga_set_decode`.

## Control Flow
Initialization exits for non-PCI devices, registers the VGA client decode callback, skips switcheroo for Thunderbolt eGPUs, registers switcheroo callbacks, and optionally installs DSM runtime PM domain ops. Decode writes chipset-family-specific registers and reports which VGA resources remain decoded. Switcheroo ON resumes the PCI device and marks DRM switch state; OFF may skip Optimus/v1 DSM cases or call DSM and suspend.

## State and Persistence Behavior
State lives in PCI driver data, `dev->switch_power_state`, VGA arbiter registration, switcheroo client registration, and optional `drm->vga_pm_domain`. No file-local persistent state exists.

## Dependencies and Integration Points
It depends on Linux VGA arbiter, vga_switcheroo, DRM client hotplug, Nouveau ACPI DSM helpers, runtime PM ops, PCI detection, and NVIF MMIO writes.

## Risks
`can_switch` uses a racy `open_count` check by design. Wrong decode register selection can leave legacy VGA ranges exposed or disabled. Switcheroo state transitions must not fight Optimus DSM runtime PM behavior.

## Test Signals
Hybrid laptop switcheroo tests, runtime PM suspend/resume, VGA arbitration handoff, Thunderbolt eGPU probing, and display hotplug reprobe verify behavior.
