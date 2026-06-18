# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/panel.c

## Purpose

`panel.c` provides the common DRM panel bridge adapter. It wraps a `struct drm_panel` as a `struct drm_bridge`, optionally creates a connector, forwards mode and prepare/enable/disable/unprepare calls to the panel, propagates bus format, exposes panel debugfs, and provides managed helpers for device-managed and DRM-managed lifetimes.

## Important APIs, Types, And Functions

`struct panel_bridge` stores the bridge, connector, panel pointer, and connector type. Exported APIs include `drm_bridge_is_panel()`, `drm_panel_bridge_add()`, `drm_panel_bridge_add_typed()`, `drm_panel_bridge_remove()`, `drm_panel_bridge_set_orientation()`, `devm_drm_panel_bridge_add()`, `devm_drm_panel_bridge_add_typed()`, `drmm_panel_bridge_add()`, `drm_panel_bridge_connector()`, `devm_drm_of_get_bridge()`, and `drmm_of_get_bridge()`.

Bridge callbacks implement attach/detach, atomic pre_enable/enable/disable/post_disable, get_modes, bus-format propagation, and debugfs. Connector helpers call `drm_panel_get_modes()`.

## Control Flow

Creation allocates a `panel_bridge`, stores panel/type, sets bridge `of_node`, `DRM_BRIDGE_OP_MODES`, type, and `pre_enable_prev_first` from the panel, then calls `drm_bridge_add()`. Attach creates a connector unless `DRM_BRIDGE_ATTACH_NO_CONNECTOR` is set, sets panel orientation on the connector, attaches the encoder, and registers the connector if the DRM device is already registered.

Atomic pre_enable/enable call `drm_panel_prepare()` and `drm_panel_enable()` unless entering from self-refresh. Atomic disable/post_disable call `drm_panel_disable()` and `drm_panel_unprepare()` unless transitioning into self-refresh. OF helpers find either an existing bridge or panel and wrap panels automatically.

## State And Persistence

Panel bridge state is a thin lifetime wrapper; persistent display state belongs to the underlying `drm_panel`, connector state, and DRM bridge chain. Managed variants use devres or drmm actions to remove the bridge automatically. `detach()` cleans up the connector if it was initialized.

## Dependencies And Integration Points

This file is central to DRM bridge/panel integration and is used by many display drivers through exported symbols. It depends on DRM bridge, connector, encoder, managed cleanup, OF graph/panel lookup, debugfs, and panel APIs.

## Risks And Edge Cases

The lifetime model is historically awkward: `drm_panel_bridge_remove()` still calls `devm_drm_put_bridge()` and `detach()` has a FIXME about connector cleanup. Deprecated typed helpers remain for panels without connector types. Self-refresh checks skip panel power transitions and depend on correct CRTC state lookup. Connector registration during attach must handle devices already registered. Calling panel bridge APIs on non-panel bridges is guarded but still a caller bug.

## Test Signals

Test exported helper users, connectorless attach, connector creation/cleanup, panel orientation propagation, self-refresh transitions, managed devres and drmm cleanup, OF bridge lookup for panel versus bridge nodes, debugfs delegation, and bus-format propagation.
