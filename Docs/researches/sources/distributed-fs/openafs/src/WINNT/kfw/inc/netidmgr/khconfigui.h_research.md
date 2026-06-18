# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khconfigui.h

## Purpose

`khconfigui.h` declares the NetIDMgr configuration-panel tree API. It lets the core and plugins register configuration nodes, create dialog panels and subpanels, traverse and remove nodes, track modified/applied state, and exchange per-dialog initialization data with configuration dialog procedures.

## Important APIs, Types, and Functions

- `KHUI_WM_CFG_NOTIFY` is the private configuration notification message, sharing the `WM_APP + 0x101` value with the new-credentials notification channel in a different window context.
- `khui_wm_cfg_notifications` defines `WMCFG_SHOW_NODE`, `WMCFG_UPDATE_STATE`, `WMCFG_APPLY`, and `WMCFG_SYNC_NODE_LIST`.
- `khui_config_node_reg` contains internal node name, localized short and long descriptions, resource module, dialog template, dialog procedure, and static flags.
- Static node flags include `KHUI_CNFLAG_SORT_CHILDREN`, `SUBPANEL`, `PLURAL`, and internal `SYSTEM`; dynamic state flags include `MODIFIED` and `APPLIED`.
- `khui_config_node` is a `khm_handle`.
- `khui_config_init_data` supplies the context node, panel registration node, and reference parent to subpanel dialog creation.
- Node management APIs include `khui_cfg_register`, `open`, `remove`, `hold`, `release`, `get_parent`, `get_first_child`, `get_first_subpanel`, `get_next`, and `get_next_release`.
- Metadata and instance APIs include `khui_cfg_get_name`, `get_reg`, `get_hwnd_inst`, `get_param_inst`, setters for instance and node window/parameter fields, `khui_cfg_clear_params`, and `khui_cfg_set_configui_handle`.
- State/dialog helpers are `khui_cfg_set_flags`, `khui_cfg_get_flags`, `khui_cfg_init_dialog_data`, `khui_cfg_get_dialog_data`, `khui_cfg_free_dialog_data`, and `khui_cfg_set_flags_inst`.

## Control Flow

Plugins register nodes under the root or a parent node with unique sibling names. The configuration window maintains a tree and sends `KHUI_WM_CFG_NOTIFY` to dialog panels. When a node is selected, the UI shows the registered dialog template and passes `khui_config_init_data`. Panels call `khui_cfg_set_flags()` or `khui_cfg_set_flags_inst()` as values change. When the user clicks Apply or OK, the configuration window broadcasts `WMCFG_APPLY`; panels persist their settings and clear modified flags. `WMCFG_SYNC_NODE_LIST` is synchronous before a node is removed, allowing the active window to update tree state before handles disappear.

## State and Persistence Behavior

Nodes are reference-counted handles. Removal marks a node deleted and actual deletion is deferred until all holds are released. The registration structure returned by `khui_cfg_get_reg()` is a shallow copy whose string pointers remain internal and valid only while the node handle is held. Dynamic flags track UI state, not necessarily persisted configuration; actual settings persistence is performed by panels through the configuration API (`kconfig.h`) when Apply is handled. Dialog data is allocated, stored in `DWLP_USER`, and must be freed with `khui_cfg_free_dialog_data()`.

## Dependencies and Integration Points

The API depends on Win32 dialog concepts (`HMODULE`, `DLGPROC`, `HWND`, `LPARAM`, `DWLP_USER`) and NetIDMgr core definitions from `khdefs.h`. It integrates with plugin configuration providers (`KHM_PITYPE_CONFIG` in `kmm.h`), action IDs for Options panels in `khactiondef.h`, and configuration storage through `kconfig.h`. `khuidefs.h` exposes it to plugin code.

## Risks and Edge Cases

- Node names must be unique among siblings and must not collide with custom action names; registration code should enforce both.
- `KHUI_WM_CFG_NOTIFY` has the same numeric value as `KHUI_WM_NC_NOTIFY`; dispatch is safe only if handlers distinguish window class/context.
- Shallow `khui_cfg_get_reg()` data is easy to misuse after releasing a node.
- `PLURAL` and `SUBPANEL` nodes rely on correct `ctx_node`, `this_node`, and `ref_node` interpretation; wrong handles can apply settings to the wrong target.
- `get_next_release()` always releases the input handle, even on not-found; loops must not release it again.

## Test Signals

- Register duplicate names, invalid strings, root nodes, sorted children, subpanels, and plural panels.
- Traverse child and subpanel lists and verify every returned handle is released exactly once.
- Exercise Apply with modified/applied flag transitions and `WMCFG_UPDATE_STATE` notifications.
- Test dialog data allocation, retrieval, extra block zeroing, and cleanup on dialog destruction.
- Remove nodes while the configuration window is active and verify `WMCFG_SYNC_NODE_LIST` prevents stale selection.
