# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/habanalabs_drv.c

## Purpose
This file is the PCI/DRM entry point for the HabanaLabs accelerator driver. It declares module metadata and parameters, binds supported PCI IDs, registers the DRM accel driver, allocates per-device `struct hl_device` instances, and handles PCI probe/remove, power management, PCI error recovery, and reset notifications.

## Important APIs, Types, And Functions
`hl_device_open()` opens the compute DRM node and creates `hl_fpriv`, context-manager, and mmap-memory-manager state. `hl_device_open_ctrl()` opens the control node by resolving the global device IDR. `hl_drm_ioctls` binds info, command-buffer, command-submission, wait, memory, and debug ioctls. `get_asic_type()`, `create_hdev()`, `fixup_device_params()`, `allocate_device_id()`, `hl_pci_probe()`, `hl_pci_remove()`, `hl_init()`, and `hl_exit()` drive device/module lifetime.

## Control Flow
Module load allocates a major and registers the PCI driver. Probe allocates a DRM-backed `hl_device`, detects ASIC type, copies module params, applies defaults, reserves an IDR minor, stores PCI drvdata, and calls `hl_device_init()`. Compute open is gated by operational status, DRAM scrub, compute-context release, and single active compute-context ownership before creating a context and linking it into the device file-private list. Remove calls `hl_device_fini()`, clears drvdata, and removes the IDR entry.

## State And Persistence
Persistent state includes module parameters, the global major, global `hl_devs_idr`, per-device IDs, open counters/timestamps, reset defaults, timeout configuration, firmware-component flags, and per-open `hl_fpriv` state. ASIC-specific fixups alter timeout and reset-on-release behavior.

## Dependencies And Integration Points
The file integrates PCI, DRM accel, tracepoints, context management, debugfs, memory-manager setup, ioctl/mmap entry points, ASIC callbacks, suspend/resume, and PCI AER/reset handlers.

## Risks
Open-state gates are race-sensitive and depend on correct `fpriv_list_lock` use. Error paths must tear down partially initialized private data. PCI reset/error callbacks assume valid drvdata and ASIC callbacks. Timeout defaults differ by ASIC and can affect lockup behavior.

## Test Signals
Test module load/unload, probe/remove failure unwind, compute open during reset/scrub/active-context states, control minor lookup, suspend/resume, PCI AER paths, and `hl_device_init()` failure cleanup.
