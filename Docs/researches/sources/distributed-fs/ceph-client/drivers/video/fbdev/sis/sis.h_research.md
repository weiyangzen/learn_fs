# sources/distributed-fs/ceph-client/drivers/video/fbdev/sis/sis.h

## Purpose

`sis.h` is the central Linux fbdev private header for the SiS framebuffer driver. It defines driver versioning, device IDs, accelerator IDs, capability flags, hardware register addresses, MMIO helpers, video bridge flags, LCD command enums, VRAM heap structures, the large `struct sis_video_info` driver state object, and cross-file function prototypes.

## Important APIs, Types, And Functions

- Version and debug helpers: `VER_MAJOR`, `VER_MINOR`, `VER_LEVEL`, `DPRINTK`, `TWDEBUG`, and `SISFAIL`.
- PCI and fb acceleration identifiers for SiS and XGI devices.
- Capability and resource sizing constants for cursor memory, command queues, turbo queues, and offscreen heap allocation.
- VGA/bridge register offsets and aliases such as `SISSR`, `SISCR`, `SISPART1` through `SISPART5`, and `SISDAC2*`.
- Video bridge masks `VB_*` and `VB2_*`, including bridge type groups for TMDS, LVDS, YPbPr, HiVision, LCDA, scaler, and RAMDAC capability checks.
- I/O helpers: `SiS_SetReg*`, `SiS_GetReg*`, and MMIO macros `MMIO_IN*`/`MMIO_OUT*`.
- Enums: `_SIS_LCD_TYPE` for panel classes and `_SIS_CMDTYPE` for command queue modes.
- Heap structures: `SIS_OH`, `SIS_OHALLOC`, and `SIS_HEAP`.
- Driver state: `struct sis_video_info`, the fbdev `par` object holding `SiS_Private`, fbdev state, PCI devices, memory mappings, mode/current timing state, acceleration state, bridge flags, panel/TV state, hardware cursor state, and linked-list membership.
- Prototypes for init, mode lookup, CRT2, DDC, acceleration, PCI access, and SiS-specific memory ioctls.

## Control Flow

The header itself has no runtime flow. It enables the rest of the driver to share a common state object and helper API. `sis_main.c` owns most top-level fbdev control flow and uses this header to call init, mode, bridge, acceleration, heap, and register helpers. `sis_accel.c` uses the MMIO macros and `struct sis_video_info` acceleration fields. `init.c` and `init301.c` use the same register and bridge definitions for hardware programming.

## State And Persistence

`struct sis_video_info` is the persistent per-device state for the driver. It stores mapped framebuffer/MMIO bases, BIOS pointer, memory sizes, mode geometry, current timings, command queue length and type, acceleration enablement, video bridge flags, panel and TV settings, detected devices, cursor memory, user/module parameters, and registration status. Hardware persistence is represented by VGA sequencer/CRTC registers, bridge part registers, command queues, and framebuffer memory written through the helpers.

## Dependencies And Integration Points

- Includes `<video/sisfb.h>`, `vgatypes.h`, and `vstruct.h`.
- Used by nearly every driver file, including `sis_main.c`, `sis_accel.c`, `init.c`, and `init301.c`.
- Integrates with Linux PCI, fbdev, I/O memory, spinlock, and compatibility APIs.
- Serves as the common declaration point for fbdev callbacks implemented in `sis_accel.c` and mode helpers implemented in `initextlfb.c`.

## Risks

- The `struct sis_video_info` layout is broad and highly coupled; changes can affect probe, mode setting, acceleration, cursor, heap, and ioctl paths.
- Many bit masks mirror hardware register layouts, and several `VB_*` and `VB2_*` groups overlap by design.
- MMIO helpers are thin wrappers around raw reads/writes; callers must provide valid mapped bases and offsets.
- Conditional prototypes can hide missing implementations unless all config families are built.

## Test Signals

- Full driver builds across 300 and 315 configurations, including XGI paths where available.
- Probe/remove tests that map MMIO/framebuffer, initialize `struct sis_video_info`, set fb ops, and clean up resources.
- Mode-switch, DDC, CRT2, acceleration, cursor, ypan, and ioctl tests to cover the major state fields.
