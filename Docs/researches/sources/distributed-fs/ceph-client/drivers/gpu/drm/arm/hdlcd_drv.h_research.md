# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/hdlcd_drv.h

## Purpose

`hdlcd_drv.h` defines the private state and local helper API shared by the ARM HDLCD driver files. It is a small internal header rather than a hardware register catalog.

## Important APIs, Types, And Functions

The central type is `struct hdlcd_drm_private`, embedding `struct drm_device base` and carrying MMIO base, pixel clock, CRTC, primary plane pointer, IRQ number, and debugfs-only interrupt counters. The helper macros `drm_to_hdlcd_priv()` and `crtc_to_hdlcd_priv()` convert DRM objects back to the private structure. Inline MMIO helpers `hdlcd_write()` and `hdlcd_read()` wrap `writel()` and `readl()` against `hdlcd->mmio + reg`. The header declares `hdlcd_setup_crtc()` and `hdlcd_set_scanout()`.

## Control Flow

This header has no standalone control flow. It supports the bind/load path in `hdlcd_drv.c`, which allocates `struct hdlcd_drm_private`, and the CRTC/plane helpers in `hdlcd_crtc.c`, which repeatedly use the conversion macros and MMIO helpers while programming modes, scanout, and interrupts.

## State And Persistence Behavior

The structure owns process-lifetime driver state for one HDLCD device. Its `base` member ensures the private object is allocated and freed as the DRM device. `mmio`, `clk`, `irq`, `crtc`, and `plane` identify resources used for hardware programming. Debug counters are volatile runtime diagnostics and do not persist across unload or reprobe. Register writes through `hdlcd_write()` persist in hardware until overwritten or reset.

## Dependencies And Integration Points

The header assumes Linux DRM, clock, atomic, and MMIO types are visible through including C files. It integrates the top-level driver and CRTC implementation by providing the shared private type and accessors. `hdlcd_set_scanout()` is declared but not implemented in the listed files, so it is either historical/API residue or implemented outside this subset in another tree version.

## Risks And Edge Cases

MMIO helpers perform no NULL or PM-state checks, so callers must ensure MMIO is mapped and clocks/power are suitable. The embedded DRM-device pattern means incorrect container conversions can corrupt unrelated memory. Any change to `struct hdlcd_drm_private` can affect all call sites using container macros. Conditional debug fields mean code must keep `CONFIG_DEBUG_FS` guards aligned.

## Test Signals

Compile coverage with and without `CONFIG_DEBUG_FS`, sparse or Coccinelle checks for MMIO accessors, probe tests that exercise conversion macros through CRTC and IRQ paths, and header dependency checks are the main signals. A symbol check can confirm whether `hdlcd_set_scanout()` is still needed.
