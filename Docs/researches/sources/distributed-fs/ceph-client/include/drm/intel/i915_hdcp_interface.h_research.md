# sources/distributed-fs/ceph-client/include/drm/intel/i915_hdcp_interface.h

Purpose: defines Intel's HDCP 2.x service interface and the packed HECI/GSC firmware command ABI used by i915, MEI HDCP, and GSC HDCP implementations.

Important APIs/types/functions: enumerations define port type, wired protocol, DDI identifiers, transcoder identifiers, firmware status codes, and HDCP command IDs. `struct hdcp_port_data` carries port/transcoder/protocol, stream count, sequence number, and MST stream list. `struct i915_hdcp_ops` exposes the full authentication flow: initiate session, verify receiver cert and H', store pairing, locality check, session key, repeater topology, M', enable authentication, and close session. `struct i915_hdcp_arbiter` binds device, ops, and mutex. Packed command structs model every HECI request/response, including headers, port IDs, AKE, LC, SKE, repeater, and stream-management payloads.

Control flow: display HDCP code maps connector state into `hdcp_port_data`, calls ops in HDCP protocol order, and the provider serializes firmware commands using the packed structures and buffer-length constants. Repeater/MST paths update `seq_num_m` and stream arrays.

State and persistence: persistent runtime state lives in the arbiter and service device binding. HDCP sessions are firmware-side per port; pairing info and authentication state are established and closed by commands.

Dependencies and integration: depends on mutex/device/module support and DRM HDCP protocol structures. Integrated by Intel display, MEI, GSC, DP/HDMI HDCP, and MST stream management.

Risks and test signals: command packing, endian fields, buffer sizes, status translation, module lifetime, and mutex coverage are critical. Test with HDCP 2.2 HDMI/DP, repeater topology, MST streams, firmware error statuses, session close on disconnect, and ABI size checks for packed messages.
