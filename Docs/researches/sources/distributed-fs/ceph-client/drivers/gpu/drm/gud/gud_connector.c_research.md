
# sources/distributed-fs/ceph-client/drivers/gpu/drm/gud/gud_connector.c

## Purpose
`gud_connector.c` implements dynamic connector discovery and connector-side behavior for the Generic USB Display driver. It translates USB protocol connector descriptors, statuses, EDID, display modes, TV/backlight properties, and connector state into DRM connector and encoder objects.

## Important APIs, Types, And Functions
`struct gud_connector` embeds a `drm_connector`, a simple `drm_encoder`, optional `backlight_device`, a backlight work item, a supported-property list, initial TV state, and initial brightness. Public internal functions are `gud_connector_fill_properties()` and `gud_get_connectors()`.

Key helpers include `gud_connector_detect()`, `gud_connector_get_modes()`, `gud_connector_atomic_check()`, `gud_connector_reset()`, `gud_connector_add_tv_mode()`, `gud_connector_property_lookup()`, `gud_connector_tv_state_val()`, `gud_connector_add_properties()`, `gud_connector_create()`, and the backlight work/update/register callbacks.

## Control Flow
`gud_get_connectors()` requests `GUD_REQ_GET_CONNECTORS`, validates that the response is a non-empty array of connector descriptors, and creates each connector in order. Creation maps GUD connector type values to DRM connector types, initializes connector helpers and funcs, verifies the DRM-assigned connector index matches the protocol index, applies polling/interlace/doublescan flags, requests supported connector properties, creates a simple encoder for the single GUD CRTC, and attaches it.

Detection optionally sends `GUD_REQ_SET_CONNECTOR_FORCE_DETECT`, reads `GUD_REQ_GET_CONNECTOR_STATUS`, maps connected/disconnected/unknown status to DRM, and increments the epoch counter when the device reports status change. Mode discovery first tries a protocol EDID blob via `GUD_REQ_GET_CONNECTOR_EDID`; if valid and not an override, it uses DRM EDID modes, otherwise it requests protocol display modes with `GUD_REQ_GET_CONNECTOR_MODES` and converts them with `gud_to_display_mode()`.

Property setup reads `GUD_REQ_GET_CONNECTOR_PROPERTIES`, creates matching DRM TV margin/mode/legacy TV properties, records initial values, and treats backlight brightness as a backlight property rather than a DRM property. During atomic check, TV property changes mark `connectors_changed` so `gud_pipe.c` can send a new device state. Backlight updates are queued on `system_long_wq`, build an atomic state that writes brightness into `connector_state->tv.brightness`, and commit outside the backlight lock.

## State And Persistence
Each connector persists its supported property IDs, initial TV state, initial brightness, current DRM connector state, optional backlight device, and encoder attachment. Runtime state changes are persisted in the DRM atomic state and later serialized into GUD property requests by `gud_connector_fill_properties()`. Device-side connector state is read or updated over USB control requests.

## Dependencies And Integration Points
The file depends on USB helpers from `gud_drv.c`, GUD protocol constants in `<drm/gud.h>`, mode conversion helpers in `gud_internal.h`, DRM connector/encoder/EDID/property helpers, backlight core, and `gud_pipe.c` atomic checking, which consumes property serialization.

## Risks
The protocol assumes connector indexes match DRM connector indexes; a mismatch returns `-EINVAL`. Invalid EDID sizes and malformed mode/property arrays are rejected, but unknown future properties are skipped, which can reduce functionality without failing probe. TV mode enum names are shared globally, so multiple connectors using TV mode must expose compatible names. Backlight updates perform asynchronous atomic commits and can fail after the backlight core has accepted a brightness change.

## Test Signals
Signals include correct connector count and type mapping from gadget descriptors, force-detect requests on forced probes, epoch increments on status changes, valid EDID and fallback mode enumeration, successful creation and reset of TV/backlight properties, `connectors_changed` on TV property updates, backlight sysfs updates resulting in GUD state commits, and clean connector destroy/early-unregister with no pending work.
