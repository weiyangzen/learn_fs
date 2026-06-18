# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/simple-bridge.c

Purpose: implements a transparent DRM bridge for simple display-adapter parts that mostly need graph attachment, optional power enable, and connector exposure. It covers VGA DACs, HDMI level shifters/converters, composite adapters, and TI/ADI DAC timing variants through OF match data rather than chip-specific register programming.

Important APIs/types/functions: `struct simple_bridge_info` carries optional `drm_bridge_timings` and connector type; `struct simple_bridge` embeds the DRM bridge and connector plus optional `vdd` regulator and `enable` GPIO. `simple_bridge_probe()` allocates the bridge, resolves the output endpoint at port 1 to the next bridge, obtains optional resources, assigns timings, and registers with `devm_drm_bridge_add()`. `simple_bridge_attach()` attaches the next bridge and creates a connector unless `DRM_BRIDGE_ATTACH_NO_CONNECTOR` is requested. Connector callbacks provide EDID-based modes or no-EDID XGA fallback, and detect through the downstream bridge. Enable/disable toggle regulator and GPIO.

Control flow: probe is devicetree graph driven: find remote node, find downstream bridge, defer if unavailable, then register this bridge. Attach always attaches the downstream bridge with no connector first; when this bridge owns the connector, it initializes a DDC-aware connector using the downstream bridge's DDC adapter and attaches it to the encoder. Runtime enable powers `vdd` before asserting `enable`; disable reverses that order.

State and persistence: there is no persistent configuration beyond devm-managed resources and match data. Hardware state is only the regulator/GPIO output level. EDID state is managed by DRM connector helpers and refreshed during mode probing.

Dependencies and integration: depends on DRM bridge/connector helpers, OF graph bindings for two-port bridges, optional regulator/GPIO consumer APIs, EDID helpers, and downstream bridge EDID/detect/DDC support. OF compatibles map connector types and timings for `dumb-vga-dac`, `adi,adv7123`, several HDMI adapters, `ti,opa362`, and TI THS813x DACs.

Risks: `bridge.next_bridge` is required and a missing graph endpoint fails probe. `simple_bridge_enable()` logs regulator enable failure but still asserts GPIO, so boards with mandatory power rails can attempt to drive an unpowered adapter. Fallback modes may expose unusable modes when DDC is broken. New compatibles must choose connector type and bus timings carefully because there is no register-level correction later.

Test signals: boot/probe with valid and missing port-1 graph endpoints, deferred downstream bridge probing, EDID and no-EDID mode enumeration, HPD/detect through downstream bridge, regulator/GPIO sequencing during atomic enable/disable, and connector type correctness in userspace.
