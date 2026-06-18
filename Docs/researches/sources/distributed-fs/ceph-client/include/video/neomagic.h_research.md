# sources/distributed-fs/ceph-client/include/video/neomagic.h

## Purpose
`neomagic.h` defines NeoMagic framebuffer acceleration, cursor, VGA-extension, PCI ID, MMIO, and private-state metadata for the NeoMagic fbdev driver.

## Important APIs, Types, and Functions
Macros cover blitter status/control bits, mode depth/resolution bits, cursor register offsets and flags, sync-suppression bits, debug logging, PCI chip IDs, MMIO size, and extended CRTC/graphics register limits. `Neo2200` maps blitter/MMIO registers such as status, control, colors, pitch, clip, source/destination, extent, and page registers. `struct neofb_par` stores VGA state, register images for VGA and panel registers, clock programming fields, write-combine cookie, MMIO base, cursor state, Neo2200 MMIO pointer, panel dimensions, clock limit, display routing flags, quirks, and pseudo-palette. `biosMode` maps a resolution to a BIOS mode number.

## Control Flow
The driver saves VGA/panel registers into `neofb_par`, programs mode and clock fields, uses MMIO blitter registers for accelerated operations, updates cursor registers relative to `cursorOff`, and restores cached register state during mode switches or suspend/resume.

## State and Persistence Behavior
`neofb_par` is the runtime state carrier and register-image cache. Hardware state includes VGA registers, panel centering, blitter registers, cursor memory, and palette. The software cache persists for the framebuffer lifetime and is not stored across reboot.

## Dependencies and Integration Points
The kernel-only part depends on VGA state handling, PCI IDs, MMIO mapping, fbdev console/palette paths, and write-combining setup. It integrates laptop internal/external panel routing, legacy VGA registers, and Neo2200 acceleration.

## Risks and Test Signals
Risks include register image drift, chip-ID-specific behavior, cursor memory lifetime (`cursorPad` comment marks a weak area), blitter FIFO/busy synchronization, and panel stretch/internal/external output quirks. Test signals include mode-set and restore across supported chips, accelerated fill/copy, cursor enable/move, palette updates, suspend/resume, internal/external display toggles, and debug builds with `NEOFB_DEBUG`.
