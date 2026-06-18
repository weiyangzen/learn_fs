# sources/distributed-fs/ceph-client/include/drm/drm_bridge.h

## Purpose
This header defines DRM bridge objects and bridge-chain operations for display pipeline components between encoders and connectors/panels. It covers attach/detach, mode validation, atomic enable/disable ordering, bus-format negotiation, HPD, EDID/mode discovery, HDMI infoframes, HDMI/DP audio hooks, CEC hooks, panel bridge helpers, reference management, and debugfs support.

## Important APIs, types, and functions
Key types are `enum drm_bridge_attach_flags`, `struct drm_bridge_funcs`, `struct drm_bridge_timings`, `enum drm_bridge_ops`, and `struct drm_bridge`. Important APIs allocate/add/remove/attach bridges, find OF bridges, get/put bridge refs, walk bridge chains, get current atomic bridge state, validate and mode-set chains, run atomic bridge check/disable/post-disable/pre-enable/enable, propagate bus formats, detect, read EDID, get modes, enable HPD, notify HPD, wrap panels as bridges, and expose debugfs parameters.

## Control Flow
Bridge chains attach to an encoder in order. During atomic check, the chain validates modes and usually checks bridges from sink toward source while negotiating output and input bus formats. During commit, disable/post-disable and pre-enable/enable callbacks run in direction-sensitive order, with `pre_enable_prev_first` allowing DSI-style ordering where upstream initialization precedes peripheral initialization. HPD callbacks are registered through bridge HPD helpers and later notify connectors.

## State and Persistence
`struct drm_bridge` is refcounted, globally listed, optionally backed by device-managed allocation, and may hold a next-bridge reference for safe hot-unplug behavior. Atomic bridges embed a `drm_private_obj` and own `drm_bridge_state` with input/output bus configuration. Persistent bridge metadata includes supported ops, connector type, interlace/YUV420 support, HDCP support, DDC adapter, HDMI vendor/product, audio/CEC devices, and HPD callback data protected by `hpd_mutex`.

## Dependencies and Integration Points
It depends on DRM atomic/private objects, encoders, connectors, modes, EDID, panels, OF graph discovery, I2C DDC, HDMI codec parameters, CEC, and debugfs. It integrates with `drm_bridge_connector`, panel bridge support, connector HDMI/audio infrastructure, and atomic helper commit sequencing.

## Risks and Test Signals
Risks include incorrect callback ordering, mixing deprecated and atomic hooks, missing mandatory callbacks for advertised ops, bus-format negotiation failure or leaked kmalloc arrays, HPD callback races, bridge hot-unplug use-after-free, and only-one-bridge assumptions for HDMI/audio ops. Tests should cover multi-bridge chains, atomic and legacy callback mixtures, DSI `pre_enable_prev_first`, EDID versus fixed-mode bridges, HPD enable/disable/notify races, panel bridge teardown, OF lookup failures, HDMI infoframe/audio/CEC ops validation, and bridge-state locking assertions.
