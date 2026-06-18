# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_dispc.h

## Purpose

`tidss_dispc.h` is the public contract between the TIDSS DRM/KMS code and the DISPC hardware layer. It defines feature-description types, SoC subrevision identifiers, VP bus types, errata/scaling capabilities, exported feature tables, and the DISPC operations used by CRTC, plane, IRQ, OLDI, and driver lifecycle code.

## Important APIs, Types, and Functions

- `enum tidss_gamma_type`, `struct tidss_vp_feat`, and `struct tidss_plane_feat` describe color-management and plane feature metadata.
- `struct dispc_features_scaling` captures scaling limits used by `dispc_vid_calc_scaling()`.
- `struct dispc_vid_info` maps logical TIDSS plane slots to hardware resource names, hardware IDs, and lite/non-lite capabilities.
- `enum dispc_vp_bus_type` distinguishes DPI, AM65x OLDI, internal, and tied-off VPs.
- `enum dispc_dss_subrevision` identifies supported DISPC generations.
- `struct dispc_features` aggregates resource names, register map pointer, VP/plane counts, bus types, plane order, and color/scaling features for a compatible device.
- Exported functions cover OLDI configuration, pixel-clock comparison, IRQ mask/status access, overlay programming, VP setup/clock/mode validation, runtime PM, plane check/setup/enable, format discovery, and DISPC init/remove.

## Control Flow

Platform matching in `tidss_drv.c` picks one of the exported `dispc_*_feats` objects and stores it in `tidss->feat`. `dispc_init()` then consumes that structure to map resources and initialize hardware. KMS setup asks `dispc_plane_formats()` for the filtered format list, `tidss_crtc` calls VP functions during modeset and flush, `tidss_plane` calls plane functions from atomic helpers, and `tidss_irq` calls the IRQ functions from its handler and vblank enable/disable paths.

## State and Persistence Behavior

The header keeps `struct dispc_device` opaque to most of the driver, so persistent state is owned by `tidss_dispc.c` while callers retain only a pointer in `struct tidss_device`. Feature-table objects are static constants and should not be mutated. The API assumes callers pass valid hardware VP and plane indices derived from the same feature table.

## Dependencies and Integration Points

The header includes DRM color-management definitions and `tidss_drv.h` for `struct tidss_device`, limits, and `dispc_irq_t`. It is included by nearly every TIDSS module and therefore acts as the cross-file ABI for DISPC programming.

## Risks and Edge Cases

- Feature arrays are fixed at `TIDSS_MAX_PORTS` and `TIDSS_MAX_PLANES`; adding hardware with more resources requires updating driver-wide limits.
- `struct tidss_plane_feat` is defined but not heavily consumed in the reviewed files, so feature declarations can drift from actual enforcement.
- Several APIs accept raw `u32` hardware indices with no type distinction between logical and hardware IDs.
- Opaque `struct dispc_device` prevents accidental mutation, but it also means callers depend on runtime checks and `WARN_ON()`s rather than compile-time shape validation.

## Test Signals

Build coverage should catch signature drift across all TIDSS modules. Runtime tests should ensure feature-table values match DT resource names, supported formats, VP clock names, bus types, and plane ordering for each compatible. API tests should exercise all public functions through atomic modesets, vblank toggles, suspend/resume, and OLDI setup.
