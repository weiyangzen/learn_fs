# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_drv.h

## Purpose

`tidss_drv.h` defines the shared TIDSS device state and driver-wide limits used by all TIDSS modules. It is the main internal header for cross-module access to the DRM device, platform device, DISPC pointer, feature table, KMS object arrays, OLDI bridges, and IRQ state.

## Important APIs, Types, and Definitions

- `TIDSS_MAX_PORTS`, `TIDSS_MAX_PLANES`, and `TIDSS_MAX_OLDI_TXES` bound array sizes across the driver.
- `typedef u32 dispc_irq_t` standardizes packed DISPC IRQ masks.
- `struct tidss_device` embeds `struct drm_device`, stores `struct device *dev`, selected `struct dispc_features *feat`, opaque `struct dispc_device *dispc`, external VP clock flags, CRTC/plane/OLDI arrays and counts, IRQ number, IRQ spinlock, and current IRQ mask.
- `to_tidss()` converts from `struct drm_device` to `struct tidss_device`.
- `tidss_runtime_get()` and `tidss_runtime_put()` are exported runtime PM helpers.

## Control Flow

`tidss_drv.c` allocates and populates `struct tidss_device`. `tidss_kms.c` appends CRTC and plane pointers during modeset initialization. `tidss_oldi.c` appends OLDI bridges and marks `is_ext_vp_clk[parent_vp]`. `tidss_irq.c` uses `irq_lock` and `irq_mask`; `tidss_dispc.c` reads features and external-clock flags; plane/CRTC helpers retrieve private state through `to_tidss()`.

## State and Persistence Behavior

This structure persists for the DRM device lifetime and is shared without deep encapsulation. KMS object counts only grow during initialization and are read afterward. IRQ state is protected by `irq_lock`. Runtime PM is not stored here directly but is controlled through `dev`.

## Dependencies and Integration Points

It includes Linux spinlocks and DRM device definitions, and forward declares `struct tidss_oldi`. It depends on `struct dispc_features` and `struct dispc_device` being visible or forward-declared by including order in users.

## Risks and Edge Cases

- Fixed-size arrays require feature-table counts to stay within limits.
- Public mutable fields increase risk of cross-module ordering bugs.
- `is_ext_vp_clk` changes DISPC pixel-clock validation semantics; OLDI init/deinit must keep it accurate.
- `dispc_irq_t` is 32-bit, so increasing packed IRQ layout beyond current VP/plane limits would require widening.

## Test Signals

Build tests should cover all TIDSS modules including this header. Runtime assertions should validate counts never exceed limits, IRQ mask updates happen under `irq_lock`, and OLDI deinit clears external clock flags. Suspend/resume and hot-unbind tests should watch for stale `dispc`, CRTC, plane, or OLDI pointers.
