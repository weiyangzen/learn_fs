# sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/hyperv_drm_proto.c

Purpose: implements the Hyper-V synthetic video VMBus protocol: version negotiation, VRAM location, display situation updates, host cursor hiding, dirty rectangle messages, supported resolution query, feature-change handling, receive callback, and VSP connection.

Important APIs/functions: `hyperv_connect_vsp()` opens the VMBus channel, negotiates protocol based on VMBus version, gets supported resolutions for Win10 protocol, sets screen depth and MMIO size. `hyperv_update_vram_location()`, `hyperv_update_situation()`, `hyperv_hide_hw_ptr()`, and `hyperv_update_dirt()` send host messages. `hyperv_receive()` drains incoming packets and `hyperv_receive_sub()` completes synchronous waits or handles feature changes.

Control flow: probe/resume call connect; connect opens channel and negotiates the best accepted version. Synchronous requests reuse `hv->init_buf`, send a packet, then wait up to 10 seconds for receive callback to copy the response and complete. Runtime display updates use stack messages without waiting for ACK, except VRAM location/version/resolution flows.

State and persistence: protocol version, screen max/preferred sizes, `dirt_needed`, MMIO megabytes, wait completion, and buffers are stored in `hyperv_drm_device`. Host-side state is updated via VMBus messages.

Dependencies and integration points: depends on Hyper-V channel APIs, DRM logging, and modeset calls. Dirty updates are triggered by plane damage; cursor hiding is triggered by CRTC enable and feature changes.

Risks: one shared completion/init buffer assumes no concurrent synchronous protocol calls. `hyperv_sendpacket()` return is ignored by some callers. Feature-change handling hides the pointer only when dirt is needed, matching this implementation's policy. Version fallback differs by host VMBus protocol. Resolution query failure falls back only partially; Win8 defaults set max but not preferred dimensions explicitly.

Test signals: negotiated version logs, timeout handling, host resolution list parsing, dirty feature toggling, cursor disappearance after VMConnect reopen, VRAM location ACK matching, and packet receive under load.
