# sources/distributed-fs/ceph-client/drivers/media/platform/arm/mali-c55/mali-c55-resizer.c

Purpose: Implements full-resolution and downscale Mali-C55 resizer subdevices, including routing between processed and bypass paths, crop/compose scaling, media-bus code negotiation, coefficient programming, and subdev registration.

Important APIs/functions: Exports `mali_c55_register_resizers()` and unregister helpers. Internal code includes coefficient tables, bank selection, crop/scaler programming, active-route detection, bypass mbus downshift, routing validation, format/frame-size enumeration, format and selection setters, and stream enable/disable.

Control flow: Init state sets the normal processed route active, with FR also exposing a bypass route. Source formats derive from the active sink: processed RGB can output RGB121212 or YUV10, while bypass shifts supported 20-bit formats to 16-bit raw outputs. Setting crop/compose clamps to hardware limits; compose cannot change while streaming. Enabling streams either sets raw bypass for FR bypass route or disables bypass and programs crop/scaler registers plus coefficient banks.

State and persistence: Each resizer stores id, pads, route count, owning `mali_c55`, and associated capture device. Crop/compose/routes/formats live in V4L2 subdev state; programmed registers persist in the context shadow until rewritten.

Dependencies and integration: Uses V4L2 subdev streams/routing, media entities, common ISP format helpers, capture-device register writes, and core context helpers.

Risks: `mali_c55_rsz_shift_mbus_code()` returns `-EINVAL` as `u32`, and some callers test falsy rather than `IS_ERR_VALUE`. Coefficient programming writes many global registers at stream enable. FR scaler may be absent and compose rejects scaling only in that case; DS existence is capability-gated elsewhere.

Test signals: Route switching, bypass raw capture, RGB/YUV source format enumeration, crop/compose limits including streaming `-EBUSY`, 1:8 scaling limit, scaler-absent behavior, coefficient bank selection, and DS capability gating.
