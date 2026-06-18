# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_hdcp_gsc_message.c

## Purpose

`intel_hdcp_gsc_message.c` implements the HDCP 2.2 firmware arbiter for platforms that use the Graphics Security Controller instead of the legacy MEI HDCP component. It translates the generic `i915_hdcp_ops` callbacks used by `intel_hdcp.c` into wired GSC command messages, sends them through `intel_parent_hdcp_gsc_msg_send()`, validates firmware status, and copies firmware outputs back into DRM HDCP protocol message structs.

## Important APIs, Types, And Functions

The exported lifecycle functions are `intel_hdcp_gsc_init()` and `intel_hdcp_gsc_fini()`. Initialization allocates an `i915_hdcp_arbiter`, obtains an `intel_hdcp_gsc_context`, assigns `gsc_hdcp_ops`, and stores both on `display->hdcp`. Fini frees the context and arbiter and clears display pointers.

The static callback set `gsc_hdcp_ops` implements every operation needed by the HDCP 2.2 core: initiating sessions, verifying receiver certificates, verifying H prime and L prime, storing pairing info, initiating locality checks, getting session keys, verifying repeater topology, verifying stream management M prime, enabling authentication, and closing sessions.

## Control Flow

`intel_hdcp_component_init()` in the HDCP core calls `intel_hdcp_gsc_init()` on display version 14 and newer. Once initialized, the generic HDCP 2.2 authentication flow calls `display->hdcp.arbiter->ops`. For each stage, this file validates input pointers, derives `struct intel_display` from the provided device, reads the stored GSC context, populates port fields from `hdcp_port_data`, sends the GSC command, checks transport return value and firmware status, and maps output data into the next HDCP protocol message.

The AKE flow starts with `intel_hdcp_gsc_initiate_session()`, which returns AKE_INIT data. `intel_hdcp_gsc_verify_receiver_cert_prepare_km()` consumes the receiver certificate and returns either stored-Km or no-stored-Km message data plus the actual message size. Locality and session-key callbacks produce LC_INIT and SKE_SEND_EKS data. Repeater callbacks verify receiver ID lists and stream-ready M prime. `intel_hdcp_gsc_enable_authentication()` asks firmware to enable authenticated port state, while `intel_hdcp_gsc_close_session()` closes firmware session state.

## State And Persistence Behavior

The file stores only display-lifetime pointers: `display->hdcp.gsc_context` and `display->hdcp.arbiter`. Per-authentication state lives in firmware and in the caller's `hdcp_port_data`. Pairing material is handed to firmware with `intel_hdcp_gsc_store_pairing_info()` rather than persisted by the driver. Variable-sized stream-management verification allocates a request sized by `data->k` and frees it immediately after sending.

## Dependencies And Integration Points

The file depends on `drm/intel/i915_hdcp_interface.h` for command and protocol structs, `intel_parent_hdcp_gsc_context_alloc/free()` and `intel_parent_hdcp_gsc_msg_send()` for transport, and `intel_display_types.h` for display HDCP storage. It plugs into `intel_hdcp.c` through the generic `i915_hdcp_arbiter` interface, allowing the same authentication core to use either GSC or MEI.

## Risks And Edge Cases

The main risks are ABI mismatch with firmware command layouts, incorrect buffer lengths, missing or stale GSC contexts, and incomplete error propagation. Each command treats non-success firmware status as `-EIO`, which is useful but collapses detailed firmware reasons unless logs are inspected. `intel_hdcp_gsc_verify_mprime()` must size the flexible request correctly with `struct_size()` and `array_size()` because `data->k` comes from active stream management. Fini assumes no concurrent authentication users; lifecycle ordering must ensure HDCP work is stopped before context free.

## Test Signals

Strong signals include successful HDCP 2.2 authentication on GSC platforms, command failure logs with command IDs on injected firmware errors, clean init/fini across driver unload, repeater and MST stream-management authentication, Type 0/Type 1 content negotiation, and suspend/resume with GSC reinitialization. Memory instrumentation should cover the variable-size M prime request path.
