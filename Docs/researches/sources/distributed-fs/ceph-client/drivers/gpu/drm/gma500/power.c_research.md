# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/power.c

## Purpose
This file centralizes GMA500 display power management. It initializes runtime PM, saves/restores display and PCI state during suspend/resume, rebuilds GTT/GEM mappings after resume, installs/uninstalls IRQs around suspend, and provides `gma_power_begin()`/`gma_power_end()` wrappers for hardware register access.

## Important APIs, Types, and Functions
Public APIs are `gma_power_init()`, `gma_power_uninit()`, `gma_power_suspend()`, `gma_power_resume()`, `gma_power_begin()`, and `gma_power_end()`. Internal helpers are `gma_suspend_display()`, `gma_resume_display()`, `gma_suspend_pci()`, and `gma_resume_pci()`.

## Control Flow
Init computes APM/OSPM I/O bases, calls optional chip PM init, takes a runtime PM reference to keep the device awake, and marks PM initialized. System suspend uninstalls IRQs, calls chip save/power-down hooks, saves PCI state plus BSM/VBT config values, disables the PCI device, and enters D3hot. Resume restores PCI power/config, powers up the display island, restores page table/GTT control, rebuilds GTT/GEM memory manager state, calls chip restore hooks, and reinstalls IRQs.

## State and Persistence Behavior
Saved PCI config values are stored in `dev_priv->regs.saveBSM` and `saveVBT`; display state is delegated to chip-specific save hooks. Runtime PM references are held/released by init/uninit and begin/end. `pm_initialized` gates uninit.

## Dependencies and Integration Points
It depends on chip ops (`init_pm`, `save_regs`, `restore_regs`, `power_down`, `power_up`), PCI PM, runtime PM, IRQ helpers, GTT/GEM resume, and register definitions for page table and GMCH control. All display register users should wrap access with `gma_power_begin()`.

## Risks
The comment states runtime PM support is broken and keeps the device permanently referenced, so power saving is limited. `gma_power_begin(false)` fails if the device is suspended; callers must handle cache-only paths. `gma_resume_pci()` return is ignored by `gma_power_resume()`. Suspend/resume order is hardware-sensitive.

## Test Signals
Signals include successful system suspend/resume with restored modes, IRQs reinstalled, GTT/GEM mappings rebuilt, no register access while power is off, balanced runtime PM references, and stable behavior for callers using forced and opportunistic `gma_power_begin()` modes.
