# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_bridge.c

## Purpose
`drm_bridge.c` implements the DRM bridge core: registration, dynamic lifetime, encoder-chain attachment, atomic bridge private state, bridge-chain modeset sequencing, bus-format negotiation, connector-facing helper calls, OF lookup, HPD callbacks, unplug protection, and debugfs inspection. A bridge models non-userspace-visible display hardware between an encoder and a sink or another bridge.

## Important APIs, Types, And Functions
Global state includes `bridge_lock`, `bridge_list`, `bridge_lingering_list`, and `drm_bridge_unplug_srcu`. Lifetime APIs are `drm_bridge_get()`, `drm_bridge_put()`, `drm_bridge_clear_and_put()`, `__devm_drm_bridge_alloc()`, `drm_bridge_add()`, `devm_drm_bridge_add()`, `drm_bridge_remove()`, and `devm_drm_put_bridge()`. Chain and modeset APIs include `drm_bridge_attach()`, `drm_bridge_detach()`, `drm_bridge_chain_mode_valid()`, `drm_bridge_chain_mode_set()`, the atomic pre-enable/enable/disable/post-disable helpers, and `drm_atomic_bridge_chain_check()`. Connector helpers include `drm_bridge_detect()`, `drm_bridge_get_modes()`, `drm_bridge_edid_read()`, and HPD enable/disable/notify.

## Control Flow
Managed allocation embeds `struct drm_bridge` in a driver container, initializes lists/refcount/function table, and registers a devm put action. `drm_bridge_add()` takes a registration reference and appends the bridge to the global list; `drm_bridge_remove()` moves it to a lingering list and drops that reference. Attachment validates the encoder and previous bridge, links into the encoder chain, invokes the driver attach callback, and initializes atomic private state when supported.

Modeset helpers walk the chain in phase-specific order: validation and mode-set encoder-to-sink, disable sink-to-encoder, enable encoder-to-sink. `pre_enable_prev_first` changes pre-enable/post-disable ordering for DSI dependencies. Atomic check first negotiates bus formats from the sink side backward via `atomic_get_output_bus_fmts()` and `atomic_get_input_bus_fmts()`, propagates bus flags, then runs each bridge's `atomic_check()` or `mode_fixup()`.

## State And Persistence
State is in-memory: global bridge lists, krefs, chain nodes, `bridge->dev`, `bridge->encoder`, optional private atomic state, HPD callback/data, and `unplugged`. SRCU protects callers that opt into `drm_bridge_enter()/exit()`. There is no disk persistence.

## Dependencies And Integration Points
The file integrates with DRM encoders/connectors/atomic state, OF device-tree lookup, debugfs, SRCU, kref, device-managed actions, EDID helpers, media-bus formats, and bridge/panel drivers.

## Risks And Edge Cases
Risk centers on lifetime and ordering. Deprecated `of_drm_find_bridge()` returns an unrefcounted pointer. Bus negotiation depends on correct driver array ownership and `-ENOTSUPP` semantics. DSI ordering through `pre_enable_prev_first` is subtle. HPD enable/disable must be paired and not used after removal. Unplug protection only works for callers that use the enter/exit API.

## Test Signals
Exercise attach/detach across multi-bridge chains, DSI order permutations, bus-format fallback to `MEDIA_BUS_FMT_FIXED`, refcount/add/remove/unplug paths, HPD callback registration and notification, OF lookup reference balance, and debugfs bridge output.
