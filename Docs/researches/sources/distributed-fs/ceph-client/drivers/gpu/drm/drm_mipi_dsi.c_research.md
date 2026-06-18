# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_mipi_dsi.c

## Purpose
This file implements the DRM MIPI DSI bus core and a large set of MIPI DSI and MIPI DCS helper commands. It registers the `mipi-dsi` Linux bus, creates DSI peripheral devices from board data or Device Tree child nodes, tracks DSI hosts, wires DSI drivers into the driver core, and provides common packet/message wrappers used by panel, bridge, and host drivers.

## Important APIs, Types, and Functions
The bus-facing API is `mipi_dsi_bus_type`, `mipi_dsi_driver_register_full()`, and `mipi_dsi_driver_unregister()`. Device creation and lifetime APIs include `mipi_dsi_device_register_full()`, `devm_mipi_dsi_device_register_full()`, `mipi_dsi_device_unregister()`, and `of_find_mipi_dsi_device_by_node()`. Host APIs include `mipi_dsi_host_register()`, `mipi_dsi_host_unregister()`, and `of_find_mipi_dsi_host_by_node()`, with global `host_list` protected by `host_lock`.

Attachment and transport are centered on `mipi_dsi_attach()`, `mipi_dsi_detach()`, `devm_mipi_dsi_attach()`, and the internal `mipi_dsi_device_transfer()`, which calls the host `transfer` callback and adds `MIPI_DSI_MSG_USE_LPM` when the device mode flags request low-power mode. Packet helpers `mipi_dsi_packet_format_is_short()`, `mipi_dsi_packet_format_is_long()`, and `mipi_dsi_create_packet()` classify and encode DSI headers.

Protocol helpers cover generic writes/reads, DCS writes/reads, DSC enable and PPS transfer, peripheral shutdown/turn-on, maximum return packet size, input bus format mapping, DCS NOP/reset/sleep/display/tear/pixel-format/address/brightness commands, and "multi" wrappers around many commands using `struct mipi_dsi_multi_context`.

## Control Flow
At postcore init, `mipi_dsi_bus_init()` registers the bus. Device matching first tries OF matching and then compares the DSI device name with the driver name. Uevents prefer OF modaliases and fall back to `MIPI_DSI_MODULE_PREFIX` plus the device name.

Host registration scans available child nodes under the host's OF node; children with `reg` become DSI devices via `of_mipi_dsi_device_add()`, which derives the modalias, reads the virtual channel, grabs the node reference, and calls `mipi_dsi_device_register_full()`. The host is then linked into `host_list`. Unregistration iterates host children, detaches attached devices, unregisters them, and removes the host from the global list.

Transfers are simple wrappers: command helpers build a `struct mipi_dsi_msg`, choose the correct packet type from payload length or command kind, and call `mipi_dsi_device_transfer()`. Multi helpers short-circuit once `ctx->accum_err` is set, allowing panel init sequences to be written linearly while preserving the first error. Driver registration installs shim probe/remove/shutdown functions only when the `mipi_dsi_driver` provides those callbacks.

## State and Persistence Behavior
Persistent in-kernel state is the bus registration, each `struct mipi_dsi_device`, the host-owned child device tree, and the global host list. Device state includes host pointer, channel, name, fwnode/OF node reference, mode flags, and `attached`. Managed devm helpers persist cleanup actions until the owning device unbinds. The DSI command helpers do not cache display state; they transmit commands and rely on the panel/peripheral hardware and host driver to persist effects such as sleep state, pixel format, DSC mode, address window, and brightness.

## Dependencies and Integration Points
This code depends on the Linux device model, OF graph helpers, runtime PM generic callbacks, DRM display compression definitions, DRM MIPI DSI public headers, media bus formats, and `video/mipi_display.h` command constants. It is used by DSI host controller drivers, DSI panel drivers, bridge drivers, and OF helper code such as `drm_of_get_dsi_bus()`. The packet and command helpers are a shared protocol layer above host-specific transfer implementations.

## Risks
The virtual channel is limited to 0..3; bad `reg` properties or unchecked board data fail registration. `mipi_dsi_device_register_full()` frees the DSI object directly on `device_add()` failure after `device_initialize()`, which matches this implementation but is a lifetime area to treat carefully if changed. Host registration ignores errors from individual OF child device creation, so a malformed child can be logged and skipped while the host still registers. `mipi_dsi_detach()` clears `attached` before calling host detach, so detach failures leave software state saying detached. DCS brightness helpers differ in byte order between the legacy and large variants; mixing panel expectations can produce wrong brightness values. Multi helpers depend on callers checking `accum_err`.

## Test Signals
Useful signals include module/bus registration, OF-created DSI devices with correct modaliases and virtual channels, host lookup by OF node, successful attach/detach through host callbacks, correct low-power message flag propagation, packet creation for short and long packet types, panel init sequences stopping on the first multi-context error, successful generic and DCS reads/writes on real DSI hardware, DSC PPS/compression commands accepted by panels, and clean host unregistration without leaked child devices.
