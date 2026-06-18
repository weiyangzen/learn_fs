# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp.h

## Purpose

`intel_hdcp.h` is the public display-local HDCP interface used by HDMI, DP, atomic modeset, IRQ, debugfs, and driver lifecycle code. It hides the implementation in `intel_hdcp.c` behind a small set of initialization, state transition, cleanup, and reporting functions.

## Important APIs, Types, And Functions

The header forward declares DRM and i915 display types rather than including large internal headers. Its key constant is `HDCP_ENCRYPT_STATUS_CHANGE_TIMEOUT_MS`, shared by encryption enable/disable wait paths. The API surface includes `intel_hdcp_init()`, `intel_hdcp_enable()`, `intel_hdcp_disable()`, `intel_hdcp_update_pipe()`, `intel_hdcp_atomic_check()`, `intel_hdcp_cancel_works()`, `intel_hdcp_cleanup()`, `intel_hdcp_handle_cp_irq()`, `is_hdcp_supported()`, `intel_hdcp_component_init()`, `intel_hdcp_component_fini()`, `intel_hdcp_info()`, and `intel_hdcp_connector_debugfs_add()`.

## Control Flow

Connector setup calls `intel_hdcp_init()` after selecting a bus-specific shim. Atomic check and commit paths call `intel_hdcp_atomic_check()`, `intel_hdcp_enable()`, and `intel_hdcp_update_pipe()` to convert DRM content protection property changes into protocol enable/disable work. Hotplug/teardown paths call cancel and cleanup helpers. Driver/component setup calls the component init/fini functions to prepare firmware-backed HDCP 2.2 services. DP CP IRQ handling calls `intel_hdcp_handle_cp_irq()`.

## State And Persistence Behavior

The header itself stores no state. It defines the contract for functions that mutate `struct intel_connector`, `struct intel_digital_port`, and `struct intel_display` HDCP fields. Callers must respect connector and display lifecycle ordering: initialize before exposing HDCP properties, cancel work before teardown, and do not use the API after cleanup has cleared the shim.

## Dependencies And Integration Points

The header integrates with DRM connector state, i915 atomic state, encoder/CRTC state, the shim abstraction, debugfs `seq_file`, and display port identifiers. It is included by `intel_hdcp.c`, HDMI/DP connector code, and other display lifecycle files.

## Risks And Edge Cases

Because this is a narrow declaration header, risks come from API misuse: calling enable without an initialized shim, failing to cancel delayed work before connector destruction, or exposing HDCP support on unsupported ports. Signature changes here affect multiple display subsystems.

## Test Signals

Build coverage is the primary signal for this header. Runtime signals are successful connector initialization with content protection properties, clean unload without pending work warnings, and correct CP IRQ handling for DP/HDMI paths that include this API.
