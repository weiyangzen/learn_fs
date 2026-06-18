# sources/distributed-fs/ceph-client/include/drm/drm_probe_helper.h

## Purpose
`drm_probe_helper.h` declares KMS helper functions for connector probing, hotplug detection, polling, fixed-mode connectors, TV mode enumeration, and DDC-based detection.

## Important APIs, types, and functions
Probe APIs include `drm_helper_probe_single_connector_modes` and `drm_helper_probe_detect`. Polling/hotplug APIs include `drmm_kms_helper_poll_init`, `drm_kms_helper_poll_init`, `drm_kms_helper_poll_fini`, `drm_helper_hpd_irq_event`, `drm_connector_helper_hpd_irq_event`, `drm_kms_helper_hotplug_event`, `drm_kms_helper_connector_hotplug_event`, `drm_kms_helper_poll_disable`, `drm_kms_helper_poll_enable`, `drm_kms_helper_poll_reschedule`, and `drm_kms_helper_is_poll_worker`. Fixed-mode helpers include `drm_crtc_helper_mode_valid_fixed`, `drm_connector_helper_get_modes_fixed`, `drm_connector_helper_get_modes`, `drm_connector_helper_tv_get_modes`, and `drm_connector_helper_detect_from_ddc`.

## Control flow
Drivers initialize polling, connector probes call detect and get-modes helpers, hotplug IRQs call device or connector event helpers, and polling can be disabled during sensitive modeset phases then rescheduled. Fixed-panel helpers validate and expose a fixed display mode.

## State and persistence
The header owns no state. Implementation state lives in DRM mode config polling infrastructure, connectors, and mode lists. Hotplug and polling state is runtime-only.

## Dependencies and integration points
It depends on DRM modes, connectors, CRTCs, devices, modeset acquire contexts, DDC/I2C helpers through implementations, and sysfs/uevent hotplug reporting.

## Risks and test signals
Risks include polling races with HPD IRQs, connector locks acquired through the modeset context, missing hotplug events after state changes, invalid fixed-mode filtering, and DDC failures misclassified as disconnects. Test signals include HPD IRQ storms, poll enable/disable cycles, forced detection, fixed-panel mode enumeration, TV connector modes, DDC failure injection, and KMS hotplug uevents.
