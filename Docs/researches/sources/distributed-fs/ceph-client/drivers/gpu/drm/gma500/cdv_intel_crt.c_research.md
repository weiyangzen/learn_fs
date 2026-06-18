<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_crt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_crt.c

## Purpose

This file implements Cedarview analog VGA/CRT connector and encoder support for GMA500. It controls the ADPA DAC register, performs CRT hotplug detection, validates CRT modes, creates the DDC bus, and registers DRM connector/encoder callbacks.

## Important APIs, Types, And Functions

The exported function is `cdv_intel_crt_init()`. Internal callbacks include `cdv_intel_crt_dpms()`, `cdv_intel_crt_mode_valid()`, `cdv_intel_crt_mode_set()`, `cdv_intel_crt_detect_hotplug()`, `cdv_intel_crt_detect()`, `cdv_intel_crt_destroy()`, `cdv_intel_crt_get_modes()`, and a no-op property setter. Helper structs are `cdv_intel_crt_helper_funcs`, connector funcs, and connector helper funcs.

## Control Flow

Initialization allocates `gma_encoder` and `gma_connector`, creates a GPIOA DDC bus, initializes a VGA connector with DDC, creates a DAC encoder, attaches them, marks output type `INTEL_OUTPUT_ANALOG`, and installs helper callbacks. DPMS clears or sets DAC/hsync/vsync disable bits according to DRM DPMS mode. Mode set clears a DPLL multiplier used for SDVO clone paths, applies hsync/vsync polarity, and selects pipe A or B in ADPA. Detection forces CRT hotplug twice, waits up to one second for each forced detect, reads monitor status, clears generated interrupt status, and restores hotplug enable bits.

## State And Persistence

Connector/encoder objects persist in DRM mode lists until destroyed. Hardware state persists in ADPA, DPLL MD, hotplug enable/status registers, and DDC GPIO state. The DDC bus is owned by the connector and destroyed on connector cleanup.

## Dependencies And Integration Points

The file depends on DRM simple encoder and helper callbacks, GMA I2C helpers, DDC mode retrieval, Cedarview register macros, shared GMA encoder prepare/commit/destroy, and `gma_best_encoder()`.

## Risks And Test Signals

Risks include long hotplug waits in detect paths, restoring hotplug register bits after concurrent HPD changes, no EDID fallback modes when DDC fails, and mode limits hardcoded to 20-355 MHz. Test signals are VGA monitor plug/unplug, DDC EDID reads, DPMS standby/suspend/off, mode polarity correctness, pipe A/B routing, and cleanup after init failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/cdv_intel_crt.c -->
