# sources/distributed-fs/ceph-client/drivers/video/fbdev/nvidia/nv_backlight.c

## Purpose

`nv_backlight.c` registers a raw backlight device for flat-panel NVIDIA displays and maps fbdev backlight levels to NVIDIA panel/backlight registers. The source was read as a complete 131-line file.

## Important APIs, Types, and Functions

The exported lifecycle functions are `nvidia_bl_init()` and `nvidia_bl_exit()`. The backlight operation is `nvidia_bl_update_status()` through `nvidia_bl_ops`. `nvidia_bl_get_level_brightness()` converts a fbdev brightness curve entry to a register value between `MIN_LEVEL` (`0x158`) and `MAX_LEVEL` (`0x534`) using `LEVEL_STEP`.

## Control Flow

Initialization returns immediately unless `par->FlatPanel` is true and, on PowerMac builds, the machine has the expected `"mnca"` backlight type. It registers a `backlight_device` named `nvidiabl<N>`, initializes `info->bl_curve`, sets brightness/power to maximum/on, and calls `backlight_update_status()`. Status updates read current PMC/PCRTC/PRAMDAC fields, either enable backlight and syncs with a scaled level or program a panel-off value, and write the updated registers. Exit unregisters `info->bl_dev`.

## State and Persistence Behavior

Runtime state is the fbdev `info->bl_dev`, `info->bl_curve`, and hardware register values in `PMC`, `PCRTC0`, and `PRAMDAC`. There is no file-backed persistence. The current brightness persists in hardware until changed, suspend/resume reprogramming, or driver removal.

## Dependencies and Integration Points

The file depends on the backlight subsystem, `struct nvidia_par` register mappings, `pci_get_drvdata()`, and optional PowerMac backlight detection. It is linked only with `CONFIG_FB_NVIDIA_BACKLIGHT` and called from `nvidiafb_probe()`/`nvidiafb_remove()` when the module parameter `backlight` allows it.

## Risks and Edge Cases

The register values are described as safe guesses, not fully documented limits. `nvidia_bl_exit()` unconditionally calls `backlight_device_unregister(bd)` with `info->bl_dev`; callers must avoid invoking it when no device was registered or rely on NULL-safe behavior. The update path ignores non-flat-panel devices and does not serialize with concurrent mode-setting beyond subsystem locking.

## Test Signals

Build-test with and without `CONFIG_FB_NVIDIA_BACKLIGHT`, probe a flat panel and verify `/sys/class/backlight/nvidiabl*` appears, exercise brightness 0/max/mid values, confirm CRT-only systems skip registration, and test suspend/resume or mode-set interactions that rewrite panel sync bits.
