# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mode_config.c

## Purpose
This file owns DRM mode configuration setup, teardown, registration ordering, resource enumeration, standard property creation, global reset, cleanup, and structural validation. It initializes `dev->mode_config`, exposes the `GETRESOURCES` ioctl implementation, creates the shared atomic/legacy KMS properties, and warns about invalid encoder, CRTC, and plane topology.

## Important APIs, Types, and Functions
Registration helpers `drm_modeset_register_all()` and `drm_modeset_unregister_all()` register or unregister planes, CRTCs, encoders, and connectors in dependency order. `drm_mode_getresources()` implements user-facing resource enumeration. `drm_mode_config_reset()` calls object reset hooks for colorops, planes, CRTCs, encoders, and connectors. `drmm_mode_config_init()` initializes managed mode_config state and registers cleanup through `drmm_add_action_or_reset()`. `drm_mode_config_cleanup()` tears down KMS objects and ID allocators. `drm_mode_config_validate()` performs topology assertions.

The static `drm_mode_create_standard_properties()` builds common properties such as plane type, source and CRTC rectangles, FB/CRTC IDs, fences, damage clips, active/mode ID, VRR, color management LUTs, CTM, background color, format modifiers, async modifiers, and size hints.

## Control Flow
Registration proceeds from planes to CRTCs to encoders to connectors and unwinds in reverse on failure. `drm_mode_getresources()` first reports file-private framebuffers under `fbs_lock`, then reports min/max dimensions, leased CRTCs, all encoders, and leased connectors through the connector iterator while hiding writeback connectors from clients that did not opt in.

Initialization sets up mutexes, the modeset connection lock, object/tile IDRs, connector IDA, lists, connector free work, standard properties, and object counters. Under lockdep it also exercises modeset and DMA reservation lock acquisition to establish lock ordering. Cleanup destroys encoders, drops connector iterator references and flushes connector free work, destroys properties, colorops, planes, CRTCs, property blobs, leaked framebuffers, ID allocators, and the connection lock. Validation fixes default clone masks, checks clone symmetry and possible CRTC masks, ensures CRTCs have valid primary/cursor plane relationships, and checks the number of primary planes.

## State and Persistence Behavior
This file initializes persistent `drm_mode_config` state for a `drm_device`: object ID namespace, tile IDs, connector IDs, global properties, object lists, counters, locks, connector free queue, and optional suspend state owned by helper code elsewhere. It does not persist hardware state directly; reset and cleanup delegate to object callbacks. Resource enumeration exposes current registered KMS object IDs and file-private framebuffer IDs to userspace.

## Dependencies and Integration Points
It integrates with the DRM object model, property subsystem, framebuffer handling, connector iteration, leasing, managed resource cleanup, DMA reservation lockdep, color pipeline/colorop code, atomic properties, and every KMS object type. Userspace observes this file through `DRM_IOCTL_MODE_GETRESOURCES` and the global property IDs attached by plane/CRTC/connector setup paths.

## Risks
`drm_mode_getresources()` can race with incompletely initialized connectors if drivers register too early, as noted by the inline FIXME. Cleanup assumes single-threaded teardown; concurrent access could deadlock or use freed objects. Property creation failures during init require cleanup to tolerate partially initialized state. Topology validation uses warnings rather than hard failures, so bad possible masks can survive to runtime if drivers ignore logs. The lockdep-only acquisition sequence must stay aligned with real locking or it may miss ordering regressions.

## Test Signals
Signals include successful `drmm_mode_config_init()` followed by cleanup on failure paths, all standard properties present on `dev->mode_config`, `GETRESOURCES` returning correct counts and respecting leases/writeback capability, reset hooks firing in expected object order, teardown without leaked connectors/framebuffers, lockdep remaining quiet for modeset and reservation locks, and validation warnings for intentionally malformed encoder/plane topology in test drivers.
