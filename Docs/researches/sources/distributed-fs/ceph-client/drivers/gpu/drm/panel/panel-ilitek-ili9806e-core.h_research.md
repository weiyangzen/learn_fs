# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-ilitek-ili9806e-core.h

## Purpose

This header declares the shared ILI9806E core interface used by bus-specific DSI and SPI panel drivers.

## Important APIs, Types, And Functions

It declares `ili9806e_get_transport()` for recovering bus-specific state from a `drm_panel`, `ili9806e_power_on()` and `ili9806e_power_off()` for shared regulator/reset sequencing, `ili9806e_probe()` for common panel creation, and `ili9806e_remove()` for panel removal.

## Control Flow

Transport drivers include this header, allocate their own state, call `ili9806e_probe()` with their transport pointer and panel funcs, and then use `ili9806e_get_transport()` inside those funcs to recover their state. Power helpers are called from transport prepare/unprepare paths.

## State And Persistence

The header stores no state. Its contract implies that core state is stored as device driver data and that the transport pointer remains valid for the panel lifetime.

## Dependencies And Integration Points

The declarations depend on `struct drm_panel`, `struct device`, and `struct drm_panel_funcs` being visible from including source files. It is a local integration point between the core, DSI, and SPI files.

## Risks

Because the transport handle is `void *`, type safety is enforced only by convention. The header does not document ownership or lifetime rules, so transport drivers must preserve the transport allocation for at least as long as the DRM panel is registered.

## Test Signals

Build tests should confirm all prototypes match the exported definitions. Runtime validation is indirect through DSI and SPI transport probe, prepare, unprepare, and remove paths.
