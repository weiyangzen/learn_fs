# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_connectors.h

Purpose: this header is the public contract for the legacy amdgpu connector implementation. It exposes connector hotplug handling, monitor bpc selection, DP bridge/capability helpers, and connector creation to the rest of the amdgpu display stack.

Important APIs/types: it declares `amdgpu_connector_hotplug()`, `amdgpu_connector_get_monitor_bpc()`, `amdgpu_connector_encoder_get_dp_bridge_encoder_id()`, `amdgpu_connector_is_dp12_capable()`, and `amdgpu_connector_add()`. The declarations depend on externally defined DRM and amdgpu types such as `struct drm_connector`, `struct amdgpu_device`, `struct amdgpu_i2c_bus_rec`, `struct amdgpu_hpd`, and `struct amdgpu_router`.

Control flow and integration: callers use `amdgpu_connector_add()` during display object discovery to register DRM connectors for supported device bits and then use the smaller helpers in hotplug, encoder, and modeset code. The header intentionally does not expose connector internals such as detection helpers or funcs tables; those remain private to `amdgpu_connectors.c`.

State and persistence: the header itself has no state. It defines interfaces that mutate DRM connector state, amdgpu connector private state, and BIOS scratch state in the implementation.

Dependencies: it must be included after the core amdgpu and DRM type definitions or in translation units where those forward declarations are already available. It is tied to the legacy ATOMBIOS connector stack rather than the DC display manager path.

Risks: the function set is small but carries wide side effects. Any signature change affects display initialization and hotplug users. Because the header does not declare the involved structs itself, include-order mistakes can surface as build failures in new users.

Test signals: build coverage from display discovery and hotplug files is the primary signal. Runtime coverage comes from exercising connector creation and DP helper calls through KMS connector enumeration and HPD events.
