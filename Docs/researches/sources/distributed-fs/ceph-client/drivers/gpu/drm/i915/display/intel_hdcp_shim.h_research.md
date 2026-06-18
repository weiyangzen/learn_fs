# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp_shim.h

## Purpose

`intel_hdcp_shim.h` defines the transport abstraction between generic HDCP logic and bus-specific receiver access. HDMI uses DDC register offsets and message mailboxes; DP uses AUX and different register naming/semantics. The shim lets `intel_hdcp.c` run the same HDCP 1.4 and HDCP 2.2 state machines over both.

## Important APIs, Types, And Functions

`enum check_link_response` defines link-check outcomes: protected, topology change, integrity failure, and reauth request. `struct intel_hdcp_shim` is the central type. HDCP 1.4 callbacks cover An/Aksv write, BKSV/BSTATUS/repeater/Ri/KSV FIFO/V prime reads, signalling enable, MST stream encryption, link checks, optional sink capability, and protocol identity.

HDCP 2.2 callbacks cover sink capability, message write/read, DP stream type configuration, MST stream encryption, link integrity checks, and optional remote HDCP capability for MST hubs. The `protocol` field maps the bus to `enum hdcp_wired_protocol` for firmware.

## Control Flow

Connector initialization passes a concrete shim to `intel_hdcp_init()`. The HDCP core stores it in `connector->hdcp.shim` and calls only through this table during authentication and link checks. HDMI populates the table in `intel_hdmi.c`; DP code provides its own implementation outside this subset.

## State And Persistence Behavior

The shim itself is static function-pointer configuration. Runtime state lives in the connector, digital port, sink, hardware registers, and firmware. Optional callbacks are checked by the core before use, allowing HDMI and DP to differ in capability detection, stream encryption, and stream-type configuration.

## Dependencies And Integration Points

The header depends on Linux integer types and `drm/intel/i915_hdcp_interface.h` for the wired protocol enum. It forward declares Intel display connector and port types and is included by both the generic HDCP core and transport implementations.

## Risks And Edge Cases

The primary risk is an incomplete or semantically mismatched shim. For example, a transport that reports capability but cannot reliably read/write protocol messages will fail mid-authentication. Optional callbacks must be genuinely optional in the core. MST-specific stream callbacks also require shared port accounting to avoid disabling encryption for other streams.

## Test Signals

Test each concrete shim with HDCP 1.4, HDCP 2.2, repeater topologies, link checks, capability queries, and disable paths. Compile-time coverage catches signature drift; runtime coverage catches offset, timing, and transport-specific behavior.
