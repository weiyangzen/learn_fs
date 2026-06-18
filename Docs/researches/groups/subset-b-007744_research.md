# subset-b-007744 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khactiondef.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khactiondef.h

## Purpose

`khactiondef.h` reserves the standard command identifier space used by the NetIDMgr user interface. It is not an implementation header; it is the ABI map that lets menus, toolbar buttons, context menus, keyboard accelerators, pseudo navigation events, and dynamically allocated user actions speak the same integer command language.

## Important APIs, Types, and Functions

- `KHUI_ACTION_BASE` starts the standard action ID bank at `50000`.
- `KHUI_ACTION_*` constants cover built-in commands such as properties, exit, default/search identity selection, password change, new credentials, refresh, layout controls, options panels, help, destroy/renew/import credentials, application open/close, menu activation, and layout reload.
- `KHUI_PACTION_*` constants are pseudo actions for generic UI events: menu, directional movement, enter/escape/OK/cancel/close/delete, extend/toggle selection, paging, selection-all, yes/no variants, remove/keep/discard.
- `KHUI_MENU_*` constants name stock menus and context menus, including main, file, credential, view, options, help, layout, toolbars, identity/token context menus, icon context menus, credential-window header context menu, and columns menu.
- `KHUI_TOOLBAR_STANDARD` identifies the stock toolbar.
- `KHUI_USERACTION_BASE` marks the allocator range for custom actions and `IS_USERACTION(cmd)` tests membership in that range.

## Control Flow

There is no runtime control flow in this header. The control-flow contract is indirect: UI code translates Windows menu and accelerator command IDs into these constants, then dispatches the ID through the action subsystem and message queue. Pseudo actions carry abstract navigation or dialog decisions rather than direct operations, so callers interpret them according to the focused control, active dialog, menu state, or alert response.

## State and Persistence Behavior

The constants are compile-time state. They must remain stable across modules that include `khactiondef.h`, resource scripts that embed command IDs, and any persisted UI configuration that stores command identifiers. Dynamic actions are expected to be allocated at or above `KHUI_USERACTION_BASE`; callers should not assume an upper bound beyond the action manager's own limits.

## Dependencies and Integration Points

This header is pulled into the public UI aggregation header `khuidefs.h` through `khaction.h`. It integrates with alert buttons in `khalerts.h`, action-context based operations in `khnewcred.h` and `khprops.h`, KMQ action messages (`KMSG_ACT_*`) in `khmsgtypes.h`, and menu/toolbar resources in the NetIDMgr executable and plugins.

## Risks and Edge Cases

- IDs are hand-assigned with gaps. Reusing a retired gap can collide with older binaries, resources, or plugin assumptions.
- `IS_USERACTION(cmd)` is a lower-bound test only. A malformed very large command ID will be considered user allocated.
- Pseudo actions do not encode source context. Handlers must validate focus, selection, and mode before treating them as concrete operations.
- The comment "Next menu: 14" is stale relative to later menu constants ending at `KHUI_MENU_COLUMNS`; future edits should rely on the actual definitions.

## Test Signals

- Build resource and accelerator tables against the header to catch command drift.
- Exercise each stock menu/toolbar command and confirm it routes to the intended KMQ or UI operation.
- Create custom actions and confirm every returned ID satisfies `IS_USERACTION`.
- Verify pseudo actions in dialogs, list views, and menus do not trigger destructive commands without context validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khactiondef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khalerts.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khalerts.h

## Purpose

`khalerts.h` defines NetIDMgr's alert object and the public API for displaying user-visible notifications, modal alerts, queued alerts, and alerts backed by the error-reporting subsystem. Alerts bridge plugin/core errors to UI windows or notification balloons and carry action command IDs for user responses.

## Important APIs, Types, and Functions

- `khui_alert` stores alert magic, severity, up to `KHUI_MAX_ALERT_COMMANDS` action IDs, title/message/suggestion strings, optional target point on Windows, flags, associated `kherr_context` and `kherr_event`, response command, refcount, and list links.
- Size limits are `KHUI_MAXCCH_TITLE` 256, `KHUI_MAXCCH_MESSAGE` 1024, and `KHUI_MAXCCH_SUGGESTION` 1024 wide characters.
- `khui_alert_create_empty()` and `khui_alert_create_simple()` allocate held alert objects.
- Setter APIs manage owned strings and validation: `khui_alert_set_title`, `khui_alert_set_message`, `khui_alert_set_suggestion`, `khui_alert_set_severity`, and `khui_alert_set_flags`.
- Command APIs are `khui_alert_clear_commands()` and `khui_alert_add_command()`.
- Display APIs are `khui_alert_show()`, `khui_alert_show_modal()`, `khui_alert_queue()`, and `khui_alert_show_simple()`.
- Lifetime and synchronization APIs are `khui_alert_hold()`, `khui_alert_release()`, `khui_alert_lock()`, and `khui_alert_unlock()`.
- Flag groups distinguish internal ownership (`FREE_STRUCT`, `FREE_TITLE`, `FREE_MESSAGE`, `FREE_SUGGEST`), caller-settable behavior (`DEFACTION`, `REQUEST_WINDOW`, `REQUEST_BALLOON`), targeting/error validity, display state, and modal state.

## Control Flow

Callers construct an alert, set severity and localized text, optionally add action IDs, optionally associate `kherr` context or event data, then choose immediate show, modal show, or queue. `khui_alert_show()` chooses a balloon when NetIDMgr is minimized/backgrounded or when a balloon is requested; otherwise it shows an alert window. Long text, suggestions, or custom commands force a placeholder balloon that opens the full alert window unless `KHUI_ALERT_FLAG_DEFACTION` is set. Modal alerts always use a window and must run on the UI thread. Queued alerts are stored until the user activates pending-alert UI.

## State and Persistence Behavior

Alert objects are reference-counted and also linked into a global alert list managed by the UI library. Text ownership is controlled by internal flags, not by direct field mutation. The `response` field is set after a user chooses a command. The alert lock is documented as global, so locking one alert serializes access to all alerts. Alert state is transient UI state; persistence is limited to any externally retained `kherr_context` or application logs that describe the same event.

## Dependencies and Integration Points

The header depends on `kherr.h` for severity, contexts, and events; `khlist.h` for list fields; `khactiondef.h` for command IDs used as buttons; Windows `POINT` for alert targeting; and KMQ alert message types in `khmsgtypes.h` (`KMSG_ALERT_SHOW`, `QUEUE`, `SHOW_QUEUED`, `CHECK_QUEUE`, `SHOW_MODAL`). `khuidefs.h` includes this header for plugins and UI consumers.

## Risks and Edge Cases

- Direct field mutation can bypass allocation flags and global synchronization, leading to leaks, double frees, or UI races.
- Only four custom command buttons are supported; extra commands should be rejected or ignored by implementation.
- Balloon title/message truncation is part of the contract; callers should avoid assuming all text appears in the balloon path.
- `KHUI_ALERT_FLAG_DEFACTION` is invalid without commands or with `REQUEST_WINDOW`; callers need to validate these combinations.
- Error context/event pointers are not self-owned by the header. Implementations must hold/release them correctly to avoid dangling references.

## Test Signals

- Create simple and empty alerts, set each string at boundary sizes, and confirm setters enforce wide-character limits.
- Show window, balloon, modal, and queued paths with and without suggestions and commands.
- Verify command ordering and default response assignment.
- Exercise error-context and error-event display integration with `kherr_evaluate_event()`.
- Run concurrent hold/release and lock/unlock tests to catch refcount and global-lock regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khalerts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khconfigui.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khconfigui.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khdefs.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khdefs.h

## Purpose

`khdefs.h` is the core portability and ABI definition header for NetIDMgr. It defines fixed-width integer aliases, generic handles, booleans, size types, calling/export conventions, common permission and creation flags, pointer/math macros, and version records used by every other public NetIDMgr header.

## Important APIs, Types, and Functions

- Integer aliases: `khm_octet`, `khm_int16`, `khm_ui_2`, `khm_int32`, `khm_ui_4`, `khm_int64`, and `khm_ui_8`.
- Numeric limits: `KHM_UINT32_MAX`, `KHM_INT32_MAX`, `KHM_INT32_MIN`, `KHM_UINT16_MAX`, `KHM_INT16_MAX`, `KHM_INT16_MIN`.
- `khm_handle` is an opaque `void *`; `KHM_INVALID_HANDLE` is `NULL`.
- `khm_boolean` is `khm_int32`, `khm_size` is `size_t`, and `khm_ssize` is a Windows-width signed size.
- `khm_wparm` and `khm_lparm` mirror Windows parameter widths, with `_WIN64` and `_WIN32` branches.
- `KHMAPI` is `__stdcall`; `KHMEXP`, `KHMEXP_EXP`, and `KHMEXP_IMP` select DLL export/import decoration.
- Generic flags include `KHM_PERM_READ`, `KHM_PERM_WRITE`, and `KHM_FLAG_CREATE`.
- Utility macros include `UBOUND32`, `BYTEOFFSET`, `IS_POW2`, `UBOUNDSS`, and `ARRAYLENGTH`.
- `khm_version` carries four 16-bit fields: major, minor, patch, and auxiliary/build.

## Control Flow

There is no executable control flow. The header controls compile-time ABI shape and calling convention. Any exported API declared with `KHMEXP khm_int32 KHMAPI` uses the same stdcall/dll decoration defined here, which is essential because plugin callbacks and import libraries are shared across binaries.

## State and Persistence Behavior

The values are compile-time contracts. `khm_handle` values represent runtime-owned objects in other subsystems but this header intentionally hides structure layout. `khm_version` is used for compatibility checks, including `khm_get_lib_version()` in `khuidefs.h` and plugin/module compatibility in `kmm.h`/`kplugin.h`.

## Dependencies and Integration Points

`khdefs.h` includes standard C headers `<stddef.h>`, `<limits.h>`, and `<wchar.h>`. Every listed header directly or indirectly depends on it. It assumes Microsoft C integer spelling (`__int32`, `_W64`, `__declspec`) and Windows build macros; non-Windows builds trigger an error for parameter-width types.

## Risks and Edge Cases

- `KHM_UINT32_MAX` lacks an unsigned suffix; comparisons in strict code should avoid signed conversion surprises.
- `IS_POW2(d)` treats zero as true by design; callers looking for positive powers must add their own nonzero check.
- `UBOUND32(d)` is documented only for positive integers and underflows for `d == 0`.
- `KHMEXP` is always `dllexport` in this snapshot; consumers may need a separate import build define or import library conventions.
- `khm_lparm` is defined as 64-bit even on `_WIN32`, which may be intentional for data transport but differs from Win32 `LPARAM` width.

## Test Signals

- Compile representative plugin and core headers for x86 and x64 to catch calling-convention and typedef drift.
- Assert fixed-width typedef sizes and `khm_version` layout in ABI tests.
- Exercise utility macros with boundary values, including zero and already aligned inputs.
- Validate exported symbols in import libraries match `KHMAPI` name decoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khdefs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kherr.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kherr.h

## Purpose

`kherr.h` defines NetIDMgr's structured error-reporting subsystem. It lets code build thread-local hierarchical error contexts, report localized and formatted events, attach facilities, suggestions, progress, and resources, notify context handlers, and later expose those events through alerts or error viewers.

## Important APIs, Types, and Functions

- Parameter types `KEPT_*` and `kherr_param` describe values used to expand formatted event strings.
- Severity levels run from `KHERR_FATAL`, `ERROR`, `WARNING`, `INFO` through debug levels to `KHERR_NONE`; smaller values are more severe.
- Suggestion IDs include none, abort, retry, ignore, interact, and other.
- `kherr_event` stores magic, reporting thread, short/facility/location/long/suggestion strings, severity, facility ID, suggestion ID, resource/free flags, four parameters, tick and FILETIME timestamps, optional module handle, and list links.
- Event flags distinguish constant/resource/message/free strings for short, long, and suggestion fields, plus resolved, folded, inert, and committed states.
- `kherr_context` stores magic, unique serial, aggregate severity, flags, refcount, descriptor event, significant error event, progress meter, tree links, and event queue.
- Context flags include dirty, own-progress, unbound, transitive, and an initial mask.
- Handler APIs are `kherr_add_ctx_handler()` and `kherr_remove_ctx_handler()`.
- Reporting APIs include `kherr_report()`, `kherr_reportf_ex()`, `kherr_reportf()`, `kherr_dup_string()`, inline `kherr_val()`, and helper macros such as `_int32`, `_cstr`, `_dupstr`, `_report_cs*`, `_report_sr*`, `_report_mr*`, and `_report_ts*`.
- Last-event mutation APIs include `kherr_suggest()`, `kherr_location()`, `kherr_facility()`, `kherr_set_desc_event()`, and `kherr_del_last_event()`.
- Context lifecycle/traversal APIs include create/hold/release, push/pop/peek, error clear/check, progress set/get, event iteration, child-context iteration, descriptor/error event access, and event evaluation.

## Control Flow

Typical code calls `kherr_push_new_context()` or pushes an unbound context, reports one or more events with `kherr_report()` or macros, optionally mutates the last event with suggestion/location/facility/descriptor calls, and pops the context. Contexts form a hierarchy independent of each thread's stack; an unbound context becomes attached when pushed. Events can remain unresolved until a UI or caller asks for strings, at which point `kherr_evaluate_event()` loads resources, expands inserts, frees transient string ownership, and marks resolved state. Context handlers run synchronously in the thread that caused a begin, describe, error, end, or event-commit transition.

## State and Persistence Behavior

Error state is thread-local plus globally discoverable through context trees. Contexts are refcounted and assigned serial numbers because context objects can be reused. Event lists are valid only while the owning context is held, and the last event may still be active until committed by a later event or context closure. The subsystem itself is transient; persistence is normally achieved by UI reporting, debug output, or external logs. Transitive contexts propagate across message handling for threads processing messages caused by the originating context.

## Dependencies and Integration Points

`kherr.h` depends on `khdefs.h` and `khlist.h`, plus Win32 types such as `DWORD`, `FILETIME`, `HMODULE`, `MAKEINTRESOURCE`, and `DWORD_PTR` when used on Windows. `khalerts.h` embeds `kherr_context` and `kherr_event` pointers. `kmq.h` stores a `kherr_context` on each `kmq_message` so async work can carry error state. Facility IDs include KMM, KCDB, UI, KRB5, KRB4, AFS, and user banks.

## Risks and Edge Cases

- Most functions are deliberately lightweight and often return no error; failure to record an error can be silent after the original failure.
- Constant string pointers are not copied. Callers must use `_dupstr`/`KEPT_STRINGT` or free flags for transient buffers.
- Handler callbacks must be reentrant and fast because they run inside the reporting thread.
- Context/event pointers from traversal become invalid after releasing the context.
- `_report_sr*` and `_report_mr*` macros require `KHERR_HMODULE` for resource resolution; missing module setup causes compile failures or null module behavior.
- There is a declaration typo in `kherr_report()` parameter name `long_desC`; harmless for ABI but a signal that callers should rely on types, not parameter spelling.

## Test Signals

- Report events with constant, duplicated, free, string-resource, and message-resource strings, then force evaluation and verify cleanup.
- Push/pop nested and unbound contexts across multiple threads and verify serial uniqueness and hierarchy.
- Register handlers for each event kind and ensure no deadlocks when handlers inspect but do not hold closed contexts.
- Validate severity aggregation, dirty recalculation, descriptor removal from event queues, and error clearing.
- Carry a context through KMQ message dispatch and show it through `khalerts.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kherr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kherror.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kherror.h

## Purpose

`kherror.h` defines the common NetIDMgr integer error-code space and success/failure predicates. It is the lightweight return-code companion to the richer contextual reporting in `kherr.h`.

## Important APIs, Types, and Functions

- `KHM_ERROR_BASE` is `0x40000000L`; NetIDMgr-specific failures occupy `KHM_ERROR_BASE` through `KHM_ERROR_BASE + KHM_ERROR_RANGE`.
- `KHM_ERROR_RANGE` is 256.
- `KHM_ERROR_NONE` and `KHM_ERROR_SUCCESS` are both zero.
- Defined errors cover invalid name, too long/insufficient buffer, invalid parameter, duplicate, not found, not ready, no resources, type mismatch, already exists, timeout, exit, unknown/general, out of bounds, deleted, invalid operation, invalid signature, not implemented, equivalent, no provider, partial success, and incompatible.
- `KHM_SUCCEEDED(rv)` tests equality with success, and `KHM_FAILED(rv)` tests nonzero.

## Control Flow

APIs throughout NetIDMgr return `khm_int32` values from this space. A zero return continues normal flow. Nonzero values are treated as failures, with `KHM_ERROR_PARTIAL` representing a completed operation with some subscriber or component errors. `KHM_ERROR_EXIT` is also used by KMQ dispatch loops to signal thread quit messages.

## State and Persistence Behavior

The header has no runtime state. Error codes can be persisted in configuration or failure-count records, such as KMM module/plugin failure reasons. They are also often paired with a `kherr` context for user-visible diagnostics.

## Dependencies and Integration Points

It is included directly by `kplugin.h` and indirectly by `khuidefs.h`. It is referenced broadly by `kconfig.h`, `kcreddb.h`, `kmq.h`, `kmm.h`, `khconfigui.h`, and plugin callbacks as the common return-code vocabulary.

## Risks and Edge Cases

- Success is exactly zero; any warning-like nonzero value is a failure to `KHM_FAILED()`.
- The range is small and manually allocated. New error codes must not collide or exceed the documented range without auditing callers.
- `KHM_ERROR_PARTIAL` is nonzero, so callers that only check `KHM_FAILED()` will treat partial success as hard failure.
- The values are not HRESULTs even though the high bit pattern resembles Windows-style codes; callers should not pass them to HRESULT-only APIs without conversion.

## Test Signals

- Compile all public headers and assert each documented code is unique.
- Unit-test APIs that intentionally return `KHM_ERROR_TOO_LONG` with required-size out parameters.
- Verify KMQ synchronous calls return `KHM_ERROR_PARTIAL` when any subscriber fails.
- Confirm module/plugin failure records store and display these codes correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kherror.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khhtlink.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khhtlink.h

## Purpose

`khhtlink.h` defines the data payload passed when a user clicks a link inside a NetIDMgr hypertext window. It gives consumers rectangle, identifier, and parameter slices without forcing null-terminated strings.

## Important APIs, Types, and Functions

- `khui_htwnd_link` contains a Win32 `RECT`, an `id` pointer plus `id_len`, and a `param` pointer plus `param_len`.
- `KHUI_MAXCCH_HTLINK_FIELD` limits link ID or parameter fields to 256 wide characters.
- `KHUI_MAXCB_HTLINK_FIELD` is the corresponding byte count.

## Control Flow

The hypertext control parses markup, tracks link rectangles, and sends this structure to a window or panel when a link is activated. Consumers inspect the non-null-terminated `id` and optional `param` slices and then dispatch an action, such as switching a new-credentials panel through `CTLINKID_SWITCH_PANEL` in `khnewcred.h`.

## State and Persistence Behavior

The structure is an event payload, not an owner. The `id` and `param` pointers reference parser/control buffers and must be copied if needed after the notification returns. The rectangle is useful for hit testing, invalidation, or context positioning during the current UI event.

## Dependencies and Integration Points

The header depends on Win32 `RECT` and wide strings. It is included by `khuidefs.h` and integrates with new-credentials credtext links (`WMNC_CREDTEXT_LINK`) and any alert/config text controls that embed clickable spans.

## Risks and Edge Cases

- The fields are not null-terminated. Treating them as C strings can read past the slice.
- Lengths are `int`; callers should validate nonnegative lengths before copying.
- Pointers are mutable `wchar_t *` but should be treated as read-only unless the owning control explicitly allows mutation.
- Field limits are per field, not per rendered line or complete markup.

## Test Signals

- Click links with ID only, ID plus parameter, maximum-length fields, and adjacent links.
- Verify consumers compare by length-aware functions, not `wcscmp`.
- Test panel switching links in new-credentials credtext and ensure out-of-range ordinals are rejected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khhtlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khlist.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khlist.h

## Purpose

`khlist.h` provides small intrusive list, queue, and tree macros used internally by NetIDMgr headers and implementations. It is explicitly "not exported" and warns that most macros are unsafe.

## Important APIs, Types, and Functions

- LIFO macros: `LDCL`, `LINIT`, `LPUSH`, `LPOP`, `LDELETE`, `LEMPTY`, `LNEXT`, and `LPREV`.
- Tree-with-LIFO-children macros: `TDCL`, `TINIT`, `TADDCHILD`, `TFIRSTCHILD`, `TPOPCHILD`, `TDELCHILD`, and `TPARENT`.
- FIFO queue macros: `QDCL`, `QINIT`, `QPUT`, `QGET`, `QDEL`, `QGETT`, `QTOP`, `QBOTTOM`, `QNEXT`, and `QPREV`.
- Tree-with-FIFO-children macros: `TQDCL`, `TQINIT`, `TQADDCHILD`, `TQFIRSTCHILD`, and `TQPARENT`.

## Control Flow

These macros splice intrusive `next`/`prev` fields directly into caller-provided structures. Queue insertion uses `LPUSH` on the tail and queue removal walks through the reverse links from head to tail. Tree macros combine list or queue children with a parent pointer, allowing context trees (`kherr_context`) and message/event lists (`kmq_message`, `khui_alert`, `khui_property_page`) to share minimal linkage logic.

## State and Persistence Behavior

The macros mutate embedded pointers in-place and do not allocate, free, validate, lock, or track ownership. Persistent state is entirely owned by the enclosing subsystem. A node can only be in one list/tree that uses the same embedded linkage fields at a time.

## Dependencies and Integration Points

`kherr.h` uses `LDCL`, `TDCL`, and `QDCL` for events and contexts. `kmq.h` uses list and queue declarations for responses, messages, queues, subscriptions, and message types. `khalerts.h` uses list links for alert objects. `khprops.h` uses `QDCL` and `LDCL` for property pages.

## Risks and Edge Cases

- Macro arguments are evaluated multiple times in some cases and have no type safety.
- `TINIT` initializes children and parent but does not call `LINIT`; callers must initialize list links separately when needed.
- Deleting or popping a node not currently in the target list can corrupt unrelated lists.
- No synchronization is provided; callers must hold subsystem locks.
- Queue direction is non-obvious: `QNEXT(pe)` maps to `prev` and `QPREV(pe)` maps to `next`.

## Test Signals

- Exercise push/pop/delete on empty, single-node, and multi-node lists.
- Verify FIFO order for `QPUT` plus `QGET` and LIFO order for `QGETT`.
- Add and remove child nodes in both LIFO and FIFO tree variants.
- Run debug builds with assertions in wrapper code to detect double insertion or deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khlist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khmsgtypes.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khmsgtypes.h

## Purpose

`khmsgtypes.h` defines the standard NetIDMgr KMQ message type IDs and subtypes. It is the protocol map for system lifecycle events, credential database notifications, module manager coordination, credential acquisition, action updates, alert delivery, and identity-provider requests.

## Important APIs, Types, and Functions

- Global message types: `KMSG_SYSTEM`, `ADHOC`, `KCDB`, `KMM`, `CRED`, `ACT`, `ALERT`, `IDENT`, and user-defined types at `KMSGBASE_USER`.
- System subtypes: init, exit, and completion.
- KCDB subtypes: identity, credential type, attribute, type, and credential request.
- KMM subtypes: internal register and done.
- Action subtypes: enable, check, refresh, new, delete, activate, and command-line/config-sync internals.
- Credential subtypes: root delta, refresh, password, new, renew, dialog setup/prestart/start, identity/options changes, process, end, import, destroy, property-page lifecycle, and address-change.
- `IS_CRED_ACQ_MSG(msg)` checks whether a credential subtype is in the acquisition/dialog range 16..31.
- Alert subtypes map to showing, queueing, showing queued, checking queue, and modal display.
- Identity subtypes drive provider lifecycle, name validation/canonicalization/comparison, default/searchable flags, info, enumeration, update, UI callback lookup, and creation notification.

## Control Flow

KMQ publishers use these constants with `kmq_post_message`, `kmq_send_message`, or subscription-specific send/post functions. Credential acquisition is a multi-stage sequence: providers respond to password/new/renew by adding `khui_new_creds_by_type` participants, then UI drives setup, prestart, start, process, and end messages. Identity-provider messages are often sent to a specific subscription rather than broadcast. Alert messages carry held `khui_alert` pointers and are consumed by the notifier/UI. Property-sheet messages let credential providers add pages before and after the sheet is displayed.

## State and Persistence Behavior

The header is a static protocol contract. Runtime state lives in KMQ queues (`kmq.h`), credential blobs (`khnewcred.h`), property sheets (`khprops.h`), alert objects (`khalerts.h`), and KCDB identity/credential objects (`kcreddb.h`). Message values must remain stable because plugins and import libraries compiled against this header use them as ABI.

## Dependencies and Integration Points

This header is included by `khuidefs.h` and referenced by KMQ, KMM, KCDB, UI actions, alerts, new credentials, property sheets, and identity providers. The OpenAFS NetIDMgr plugin under `src/WINNT/netidmgr_plugin` uses these protocol values through the public headers to participate in AFS credential acquisition and configuration.

## Risks and Edge Cases

- Typographical documentation errors do not affect ABI but can mislead plugin authors; message parameter names must be checked against structures.
- `IS_CRED_ACQ_MSG` includes `KMSG_CRED_PROCESS` and `KMSG_CRED_END` even though they are not strictly dialog-only.
- Some messages are explicitly not for broadcast, especially plugin-originated dialog identity/options messages.
- Held-pointer ownership is message-specific; alert messages release held alert objects at completion/queue display.
- Numeric ranges are manually allocated, so new subtypes must avoid collisions with internal blocks.

## Test Signals

- Run message-sequence tests for credential acquisition from initial request through end, including dependency ordering.
- Verify identity-provider messages are routed to the intended subscription and not broadcast accidentally.
- Send action state changes and confirm menus/toolbars update through `KMSG_ACT_*`.
- Queue and display alerts through `KMSG_ALERT_*`.
- Confirm KMQ completion handlers clean up message payloads for each standard message class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khmsgtypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khnewcred.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khnewcred.h

## Purpose

`khnewcred.h` declares the data model and helper API for NetIDMgr credential acquisition dialogs. It coordinates core UI, identity providers, and credential provider plugins during password change, new credential, and renewal workflows.

## Important APIs, Types, and Functions

- `KHUI_WM_NC_NOTIFY` is the notification message sent to new-credentials windows and panels.
- Control ID range `KHUI_CW_ID_MIN` through `KHUI_CW_ID_MAX` reserves up to eight controls for identity-provider UI.
- `khui_wm_nc_notifications` defines dialog expansion, setup, activation, movement, panel switching, credtext updates/link clicks, identity change, prompt clearing/setting, preprocess/process/completion, type state, and internal control-row addition.
- Identity callback `khui_ident_new_creds_cb` receives `WMNC_IDENT_INIT`, `WMNC_IDENT_WMSG`, and `WMNC_IDENT_EXIT`.
- `khui_new_creds` stores request subtype, critical section, default-identity flag, identity list, launch action context, UI mode, window handle, participating credential types and subscriptions, result, response, password, prompt/banner fields, identity callback, window title, and provider auxiliary data.
- `khui_new_creds_by_type` describes a participating credential type: dependencies, ordinal, localized name/icon/tooltip, dialog resource/proc, panel handle, credtext, and plugin aux field.
- Response flags describe exit/no-exit, success/failure/pending/completed/processing.
- `khui_new_creds_prompt` describes custom prompts with type, prompt/default/value strings, hidden/stock flags, and associated controls.
- Public helpers create/destroy blobs, lock/unlock, add/delete/find/enable types, set primary/additional identities, manage prompts, get prompt values, set type response, query dependency success, and add identity-provider control rows.

## Control Flow

The UI creates a `khui_new_creds` blob and sends a credential message such as `KMSG_CRED_NEW_CREDS`, `PASSWORD`, or `RENEW_CREDS`. Interested credential providers add `khui_new_creds_by_type` structures with `khui_cw_add_type()` and list dependencies. The UI creates panels during dialog setup, activates the identity provider callback, then sends dialog-stage messages. When processing begins, plugins inspect identities and prompt values, obtain or renew credentials, and call `khui_cw_set_response()` for their type. Pending/no-exit responses keep the dialog alive and can install custom prompts. Completion and `KMSG_CRED_END` allow providers to remove by-type structures and clean plugin-owned memory.

## State and Persistence Behavior

The credential blob is mutable shared state protected by a `CRITICAL_SECTION`. Plugin-supplied `khui_new_creds_by_type` blocks are not copied; they must survive until removed or until the blob is destroyed. Identities are handles owned by the operation list. Prompt values are periodically synchronized from controls and must be refreshed with `khui_cw_sync_prompt_values()` before reading. Actual credential persistence occurs in provider implementations and credential stores; this header only models the UI transaction and responses.

## Dependencies and Integration Points

The header depends on Windows UI types, `khui_action_context` from `khaction.h`, KCDB identity and credential type handles from `kcreddb.h`, KMQ credential messages from `khmsgtypes.h`, and link payloads from `khhtlink.h`. The OpenAFS NetIDMgr plugin files (`afsnewcreds.c`, `afscred.h`, and related config files) use this contract to add AFS credential UI and process AFS token acquisition.

## Risks and Edge Cases

- By-type structures are stored by reference. Stack allocation or early free by a plugin causes dangling UI pointers.
- Dependency handling relies on providers declaring dependencies before processing; otherwise `khui_cw_type_succeeded()` can be queried before a dependency ran.
- Prompt begin/add is all-or-nothing: fewer added prompts than requested means no prompts are displayed.
- Password and prompt buffers have fixed wide-character limits; providers must handle truncation and size errors.
- `KHUI_WM_NC_NOTIFY` shares its numeric value with `KHUI_WM_CFG_NOTIFY`; dialog class/context must disambiguate.
- Identity callback runs in the UI thread and must not block.

## Test Signals

- Simulate new, renew, and password-change flows with multiple provider types and dependencies.
- Verify type add/delete reference lifetime and duplicate type rejection.
- Exercise pending prompt loops, hidden password prompts, sync before read, and boundary-sized prompt values.
- Change primary identity and confirm additional identities are cleared plus panels receive `WMNC_IDENTITY_CHANGE`.
- Test dependency failure propagation and response masks for exit/no-exit, pending, failed, and completed states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khnewcred.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khprops.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khprops.h

## Purpose

`khprops.h` declares NetIDMgr property-sheet support for identities, credential types, and individual credentials. It wraps Win32 `PROPSHEETHEADER`/`PROPSHEETPAGE` with action context and credential metadata so the core and plugins can contribute pages.

## Important APIs, Types, and Functions

- `khui_property_sheet` contains a `PROPSHEETHEADER`, status, sheet and active-page HWNDs, launch `khui_action_context`, optional identity, credential type, credential handle, page count, and a queue of pages.
- Sheet statuses are `NONE`, `RUNNING`, `DONE`, and `DESTROY`.
- `KHUI_PS_MAX_PSP` caps sheets at 16 pages.
- `khui_property_page` stores the Win32 page handle, caller-supplied page template pointer, page window handle, owning credential type, ordinal, and list links.
- Pseudo credential types `KHUI_PPCT_IDENTITY` and `KHUI_PPCT_CREDENTIAL` represent built-in identity and credential pages.
- APIs create a sheet, add/find pages, show/check/destroy the sheet, and associate a property-window record with `khui_property_wnd_set_record()`.

## Control Flow

The NetIDMgr application creates a sheet for a selected action context, then sends property-page KMQ messages so plugins can add pages before the sheet is visible. `khui_ps_add_page()` orders pages by ordinal and credential type metadata before `khui_ps_show_sheet()` creates the Win32 sheet. While running, the message loop passes messages to `khui_ps_check_message()` so modeless property-sheet accelerators and notifications are handled. After completion, the application destroys the sheet and page records.

## State and Persistence Behavior

The sheet owns page records but not necessarily caller-supplied `LPPROPSHEETPAGE` memory until creation; the header states that `ppage` must exist until status becomes `RUNNING`. Sheet status and HWND fields describe runtime UI state. Associated identity/credential handles provide context but their ownership is implementation-specific and must be held while the sheet is live. Property changes are persisted by page dialog procedures or providers, not by the wrapper itself.

## Dependencies and Integration Points

The header depends on Win32 property sheet types and `khui_action_context`. It integrates with `KMSG_CRED_PP_BEGIN`, `PRECREATE`, `END`, and `DESTROY` from `khmsgtypes.h`; KCDB identity/credential handles; and plugin-provided property pages for credential providers.

## Risks and Edge Cases

- Page limit is fixed at 16; additional provider pages should fail cleanly.
- `LPPROPSHEETPAGE` is not managed until page creation, so stack or short-lived descriptors are unsafe.
- Pages can only be added before the sheet is visible; late additions should be rejected.
- Ordering by credential type name is undefined if type metadata is unavailable.
- Sheet destroy status must guard against reentrancy from page callbacks.

## Test Signals

- Add identity, credential, and provider pages with ordinals at boundary values and confirm ordering.
- Try to add pages after `RUNNING` and past `KHUI_PS_MAX_PSP`.
- Drive modeless message handling through `khui_ps_check_message()`.
- Verify `KMSG_CRED_PP_*` message order and plugin cleanup on destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khprops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khremote.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khremote.h

## Purpose

`khremote.h` defines the compatibility IPC contract used by external processes, especially older Leash-compatible callers, to request NetIDMgr credential dialogs. It names the request daemon window, shared-memory mapping format, request command, and fixed-layout dialog information structure.

## Important APIs, Types, and Functions

- `ID_OBTAIN_TGT_WITH_LPARAM` is the Leash-compatible command ID.
- `KHUI_REQDAEMONWND_CLASS` and `KHUI_REQDAEMONWND_NAME` identify the request daemon window.
- `KHUI_REQD_MAPPING_FORMAT` formats a per-request local file mapping name using a process or request ID.
- Fixed string sizes cover username, realm, title, and credential cache name.
- Dialog types are `NETID_DLGTYPE_TGT` and `NETID_DLGTYPE_CHPASSWD`.
- `NETID_DLGINFO` contains structure size, dialog type, input title/principal/realm/ccache/options/lifetimes/flags, and output username/realm/ccache.
- `NETID_DLGINFO_V1_SZ` records the version-1 structure size for compatibility.

## Control Flow

An external caller locates the NetIDMgr request daemon window, creates or opens a named mapping following `KHUI_REQD_MAPPING_FORMAT`, fills `NETID_DLGINFO`, then sends the Leash-compatible command with mapping information in `LPARAM`. NetIDMgr reads input fields, opens either an initial-ticket or password-change dialog, writes selected output fields, and signals completion according to the surrounding window-message protocol.

## State and Persistence Behavior

The structure is a shared-memory IPC record. Input fields are fixed-size wide-character buffers; output fields are written back into the same mapped region. Kerberos credential persistence happens in the selected credential cache, not in this structure. The `size` field supports compatibility with `NETID_DLGINFO_V1_SZ` and future extension.

## Dependencies and Integration Points

The header depends on Win32 `DWORD` and `WCHAR`. It duplicates a compatible shape also visible in `inc/leash/leashwin.h`, tying NetIDMgr to older Leash/KfW callers. It integrates with new-credentials UI in `khnewcred.h`, action IDs for obtaining tickets, and Kerberos cache settings.

## Risks and Edge Cases

- Fixed-size arrays must be explicitly null-terminated by readers and writers.
- Shared mappings named under `Local\\` are session-local; services or elevated processes may need different namespace handling.
- `NETID_DLGINFO_V1_SZ` is manually computed; adding fields requires careful version checks.
- The contract exposes credential options across process boundaries, so callers and the daemon must validate structure size and mapping ownership.

## Test Signals

- Exercise both TGT and password-change dialog requests through a mapped `NETID_DLGINFO`.
- Validate behavior with `size == NETID_DLGINFO_V1_SZ`, larger sizes, and too-small sizes.
- Test maximum-length username, realm, title, and cache fields for termination.
- Verify output username/realm/cache are written back after success and unchanged or cleared on cancel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khremote.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khrescache.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khrescache.h

## Purpose

`khrescache.h` declares small UI resource-cache helpers for bitmaps and custom image lists. It lets NetIDMgr cache GDI bitmaps by resource ID, wrap bitmap dimensions, and draw masked image-list entries without repeatedly loading or recomputing resources.

## Important APIs, Types, and Functions

- `khui_init_rescache()` and `khui_exit_rescache()` start and stop global resource caching.
- `khui_cache_bitmap()` stores an `HBITMAP` by numeric ID, and `khui_get_cached_bitmap()` retrieves it.
- `khui_bitmap` wraps an `HBITMAP` with dimensions.
- `khui_bitmap_from_hbmp()`, `khui_delete_bitmap()`, and `khui_draw_bitmap()` manage/draw bitmap wrappers.
- `khui_ilist` stores cell dimensions, capacity/growth counters, backing image and mask bitmaps, usage count, and an optional ID list.
- Image-list APIs create/delete lists, add masked bitmaps with optional IDs, look up IDs, and draw by index or ID with optional background color.
- `KHUI_SMICON_CX` and `KHUI_SMICON_CY` define 16x16 small icon dimensions.

## Control Flow

The UI initializes the cache, loads bitmaps once, wraps them or adds them to image lists, then draws cached images into device contexts during window painting. ID-based image lists allow callers to decouple credential or status type IDs from physical image indices. Exit tears down cached GDI resources.

## State and Persistence Behavior

Resource-cache contents and image lists are in-process GDI state. They are not persisted across sessions. Ownership must be clear: cached bitmaps and image-list backing bitmaps should be deleted exactly once by cache/list teardown or explicit bitmap delete APIs.

## Dependencies and Integration Points

The header depends on `khdefs.h` and Win32 GDI types (`HBITMAP`, `HDC`, `COLORREF`, `BOOL`). It is included by `khuidefs.h` and used by UI components, alerts, action lists, credential displays, and plugin icons.

## Risks and Edge Cases

- GDI handle leaks are the main risk if callers bypass delete APIs or cache the same ID repeatedly without defined replacement semantics.
- Drawing by ID uses `khui_ilist_lookup_id()` inline; if lookup returns an invalid index, draw code must handle it.
- Image-list growth fields (`n`, `ng`, `nused`) require bounds checking in implementation.
- Bitmap dimensions must be valid before drawing; zero-size or deleted handles should be rejected.

## Test Signals

- Initialize/exit repeatedly under leak checking for GDI object counts.
- Cache duplicate IDs and verify replacement or rejection behavior.
- Add masked images until growth occurs and draw every index.
- Lookup missing IDs and confirm draw-by-ID fails safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khrescache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khtracker.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khtracker.h

## Purpose

`khtracker.h` declares a pseudo-logarithmic duration editor used by NetIDMgr. It combines an edit control with a slider so users can choose lifetimes or renewal durations with coarser granularity for longer intervals.

## Important APIs, Types, and Functions

- `khui_tracker` stores original edit and tracker window procedures, slider and edit HWNDs, label layout positions, activation time, and current/min/max `time_t` values.
- `khui_tracker_install()` subclasses an edit control and attaches tracker behavior.
- `khui_tracker_reposition()` moves associated controls to match the edit control.
- `khui_tracker_initialize()` initializes structure fields before installation.
- `khui_tracker_refresh()` redraws or resynchronizes displayed state from current/min/max values.
- `khui_tracker_kill_controls()` tears down associated controls and subclassing.

## Control Flow

Callers initialize a `khui_tracker`, set valid `min`, `max`, and `current` durations, then install it on an edit control. The tracker subclasses the edit and creates/manages a slider. User typing or slider movement updates `current`, with tick mapping based on ranges documented in the header: minutes at short ranges, then 5/15/30-minute, hourly, 6-hour, and day increments for longer ranges. Reposition and refresh keep the edit/slider synchronized as the parent dialog moves or settings change.

## State and Persistence Behavior

The supplied `khui_tracker` structure must remain alive for the edit control lifetime. It owns runtime HWND/subclass state but does not persist duration settings; callers copy `current` into configuration or credential request fields when needed. `act_time` tracks interaction timing for UI behavior.

## Dependencies and Integration Points

The header depends on Win32 `WNDPROC`, `HWND`, `DWORD`, and standard `time_t`. It is included by `khuidefs.h` and is likely used by Kerberos lifetime/renewal controls in new-credential and configuration panels.

## Risks and Edge Cases

- Structure lifetime is caller-managed; stack allocation for a dialog that outlives the stack frame is unsafe.
- Subclass procedures must be restored by `khui_tracker_kill_controls()` to avoid calls into freed memory.
- Min/current/max must be valid before install; current outside range or min greater than max need rejection or clamping.
- Long durations above four days intentionally do not gain finer adjustment, which may surprise callers expecting exact seconds.

## Test Signals

- Install, move, refresh, and destroy trackers in a dialog while checking subclass restoration.
- Test tick/value mapping at every documented range boundary.
- Validate typed edits clamp or reject invalid durations.
- Persist a selected duration through a credential/config flow and verify expected seconds are stored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khtracker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khuidefs.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khuidefs.h

## Purpose

`khuidefs.h` is the umbrella public UI header for NetIDMgr. It includes Windows, KMQ, credential database, error, action, resource, hyperlink, new-credential, property-sheet, alert, configuration, tracker, and remote-dialog contracts, then exposes version-query APIs for plugin compatibility and common controls.

## Important APIs, Types, and Functions

- Includes `windows.h`, `kmq.h`, `kcreddb.h`, `kherror.h`, `kherr.h`, `khmsgtypes.h`, `khaction.h`, `khactiondef.h`, `khrescache.h`, `khhtlink.h`, `khnewcred.h`, `khprops.h`, `khalerts.h`, `khconfigui.h`, `khtracker.h`, and `khremote.h`.
- Internal `khm_version_init()` initializes library version state.
- `khm_get_lib_version(khm_version * libver, khm_ui_4 * apiver)` returns NetIDMgr library and API versions.
- `khm_get_commctl_version(khm_version * pdvi)` returns a packed Windows Common Controls version and optionally fills a version record.

## Control Flow

Plugins include this one header to gain access to the full UI surface. During plugin loading, the module manager can compare plugin version metadata with `khm_get_lib_version()` results. UI code may call `khm_get_commctl_version()` before using controls that require a minimum Common Controls version.

## State and Persistence Behavior

Version state is initialized in-process and read by callers. It reflects the loaded NetIDMgr library and API level rather than persisted configuration. Common Controls version reflects the currently loaded Windows library in the process.

## Dependencies and Integration Points

This header deliberately creates a broad dependency fan-in. It is the integration point between KMQ, KCDB, KMM/plugin-facing UI helpers, alerts, actions, and remote compatibility. Its use simplifies plugin source at the cost of increased rebuild and namespace coupling.

## Risks and Edge Cases

- Including this header pulls in many Windows and NetIDMgr symbols, increasing compile-time coupling and collision risk.
- The Common Controls version function returns `MAKELONG(minor, major)` packing; callers must unpack correctly.
- `khm_get_lib_version()` accepts optional API version but requires a valid library-version pointer by contract.
- Version checks must consider both library version and API version, not only one.

## Test Signals

- Compile representative plugins with only `khuidefs.h` and verify all included contracts are visible.
- Assert library/API version values match build metadata from `netidmgr_version.h`.
- Test Common Controls version retrieval on supported Windows versions and fallback behavior if optional output is null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khuidefs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kmm.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kmm.h

## Purpose

`kmm.h` declares the NetIDMgr Module Manager API. It controls module and plugin registration, loading/unloading, dependency handling, runtime handles, plugin/module information queries, enable/disable state, configuration namespaces, and localization resource libraries.

## Important APIs, Types, and Functions

- Opaque handles `kmm_module` and `kmm_plugin` are `khm_handle`.
- Limits define maximum name, description, vendor, support URI, dependency count, dependant count, and dependency multistring sizes.
- `kmm_plugin_reg` describes a plugin: name, owning module, type, flags, KMQ message processor, dependency multistring, description, and optional icon.
- `kmm_plugin_info` extends registration with runtime state, failure count/time/reason, handle, and disabled flag.
- Plugin types are credential, identity, configuration, and miscellaneous.
- Plugin states cover failure reasons, placeholder, registered, preinit, hold, init, running, and exited.
- `kmm_module_reg` describes a module path, descriptive metadata, and provided plugin registrations.
- `kmm_module_info` adds language, state, versions, failure data, and handle.
- Module states cover failure reasons and lifecycle from none through preinit/init/init plugins/running/exit plugins/exit/exited.
- Runtime APIs initialize/exit KMM, identify current plugin/module, load/unload/default-load modules, query pending loads and state, get Win32 module handle, hold/release module/plugin handles, provide plugins during `init_module()`, and query plugin state.
- Registration/config APIs open module/plugin config spaces, get info by name or handle, enumerate plugins, enable plugins, register/unregister plugins and modules.
- Localization APIs define `kmm_module_locale`, `LOCALE_DEF`, default-locale flag, `kmm_set_locale_info()`, `kmm_get_resource_hmodule()`, and convenience resource-loading macros.

## Control Flow

The core calls `kmm_init()`, loads default modules from configuration, and eventually calls `kmm_exit()`. Loading can be async or sync. A module is loaded from its registered path, its `init_module()` entry point runs, and the module calls `kmm_provide_plugin()` for each plugin. KMM initializes plugin message processors after module init, respecting dependencies; unresolved dependencies put plugins on hold. Unload reverses the lifecycle: plugins exit, then module exit runs, then resource libraries are released. Registration APIs can be used by installers or tools to persist module/plugin metadata before runtime.

## State and Persistence Behavior

KMM maintains runtime module/plugin handles with reference counts and state machines. It also persists registration, enable/disable state, failure counts, failure timestamps, module paths, plugin dependencies, and metadata in configuration spaces opened via `kconfig.h`. Locale selection loads a resource module for the current user locale and stores the selected language on module info.

## Dependencies and Integration Points

`kmm.h` depends on `khdefs.h`, `kmq.h`, Windows `HMODULE`/`HICON`/resource APIs, `kconfig.h` for configuration spaces, and `kplugin.h` for required module exports. Plugin message processors are KMQ callbacks and consume message types from `khmsgtypes.h`. OpenAFS NetIDMgr plugin modules use this interface to provide AFS credential and configuration plugins.

## Risks and Edge Cases

- `KMM_MAXCB_DESC` is defined using `KMM_MAXCCH_NAME` rather than `KMM_MAXCCH_DESC`, likely undercounting description bytes.
- `kmm_provide_plugin()` is only valid during `init_module()`; late calls must fail.
- Async `kmm_load_module()` success only means queued, not loaded; callers must query state or wait.
- Automatic registration uses user configuration, which can diverge from machine registration expectations.
- Dependencies are stored as multistrings with fixed maximum count/length; malformed or unterminated multistrings can block plugin startup.
- Direct use of `kmm_get_hmodule()` can desynchronize state if callers perform arbitrary Win32 module operations.

## Test Signals

- Register modules/plugins with maximum-length metadata, dependencies, duplicate names, and disabled flags.
- Load modules sync and async, checking every state transition and failure reason.
- Verify dependency ordering, hold state, failure propagation, and plugin enable/disable persistence.
- Query info by name and handle, then release internal-buffer info correctly.
- Exercise locale matching, default fallback, and convenience resource macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kmm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kmq.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kmq.h

## Purpose

`kmq.h` declares the NetIDMgr Message Queue. KMQ is the asynchronous and synchronous dispatch layer that routes typed messages to per-thread callback or window subscribers, supports ad-hoc subscription handles, call waiting, completion handlers, and error-context propagation.

## Important APIs, Types, and Functions

- `kmq_thread_id` and `kmq_timer` are Win32 `DWORD` values.
- `KMQ_WM_DISPATCH` is the window message used for HWND subscribers.
- `kmq_callback_t` is the callback signature for subscribers and plugins.
- `kmq_response` stores per-thread response payloads for scatter/gather messages.
- `kmq_message` stores type, subtype, integer and pointer parameters, sent/completed/failed counters, response list, wait event, send/expiry timers, `kherr_context`, refcount, and list links.
- `kmq_call` is a `kmq_message *` handle for posted calls.
- `kmq_message_ref` binds a message to a recipient in a queue.
- `kmq_queue` is per-thread and stores critical section, wait event, load, last post time, deleted flag, queued refs, and global list links.
- `kmq_msg_subscription` binds a message type to a callback or HWND recipient and queue.
- `kmq_msg_type` stores type ID, subscriptions, completion handler, optional name, and list links.
- APIs initialize/exit KMQ, register/find/unregister message types, subscribe/unsubscribe callbacks or windows, handle `KMQ_WM_DISPATCH`, create/delete ad-hoc subscriptions, post/send to one or many subscriptions, dispatch queued messages, broadcast post/send messages, free calls, send/post thread quit messages, enumerate responses, test/wait completion, and set completion handlers.

## Control Flow

Subscribers register by message type in the current thread. A broadcast post creates a `kmq_message`, queues message references on each subscriber thread's `kmq_queue`, signals the queues, and returns immediately unless the caller requested a call handle. Synchronous send posts and waits for all recipients. Threads without Windows message loops call `kmq_dispatch(timeout)` to process queued refs. Threads with windows subscribe HWNDs and process `KMQ_WM_DISPATCH` via `kmq_wm_begin`/`end` or `kmq_wm_dispatch`. Completion handlers run after all instances of a message type complete and before message cleanup.

## State and Persistence Behavior

KMQ state is in-process and per-thread: queues, subscriptions, message refs, refcounted messages, wait events, and completion handlers. It is not persisted across sessions. Messages can carry `kherr_context` so async work remains associated with the originating error context. Call handles must be freed with `kmq_free_call()` after waiting or inspection.

## Dependencies and Integration Points

`kmq.h` depends on `khdefs.h`, `khlist.h`, `kherr.h`, Win32 synchronization/window types, and standard message IDs from `khmsgtypes.h`. It is central to KMM plugin message processors (`kmm_plugin_reg.msg_proc`), credential acquisition, alerts, action updates, KCDB notifications, and identity-provider dispatch.

## Risks and Edge Cases

- Subscriptions are per-thread; subscribing the same callback in multiple threads intentionally creates multiple deliveries.
- Callback unsubscribe only removes subscriptions for the current thread, so cleanup must run in the subscribing thread.
- Window subscribers must unsubscribe before window destruction to avoid dispatch to dead HWNDs.
- Synchronous sends can deadlock if a recipient thread is not dispatching or waits back on the sender.
- More than one waiter on a call is serialized by call freeing behavior; callers should avoid sharing call handles casually.
- Completion handler spelling parameter `hander` is harmless but highlights that only one handler exists per type and later calls overwrite it.

## Test Signals

- Broadcast to multiple callback and HWND subscribers across threads and verify sent/completed/failed counts.
- Test `kmq_send_message()` partial failure when one subscriber returns error.
- Create ad-hoc subscriptions and send targeted messages without broadcast delivery.
- Exercise quit messages causing `kmq_dispatch()` to return `KHM_ERROR_EXIT`.
- Wait/free call handles under timeout, already-completed, and multi-waiter cases.
- Verify completion handlers release payloads and can enqueue follow-up messages safely.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kmq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kplugin.h -->
# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kplugin.h

## Purpose

`kplugin.h` defines the required exported callbacks and symbol names for NetIDMgr plugin modules. It is the binary contract that lets KMM load a DLL, initialize it, discover provided plugins, route plugin messages, and optionally run module cleanup.

## Important APIs, Types, and Functions

- `init_module(kmm_module h_module)` is the required module initialization entry point.
- `init_module_t` is its function-pointer type.
- `EXP_INIT_MODULE` is the exported symbol name, undecorated on Win64 and `_init_module@4` on 32-bit stdcall.
- `_plugin_proc()` is the KMQ-compatible plugin message processor prototype; `_plugin_proc_t` aliases `kmq_callback_t`.
- `exit_module(kmm_module h_module)` is the optional cleanup entry point.
- `exit_module_t` is its function-pointer type.
- `EXP_EXIT_MODULE` mirrors architecture-specific export decoration.

## Control Flow

KMM loads a module DLL and resolves `EXP_INIT_MODULE`. `init_module()` runs on the plugin-manager thread in the current user context. It must not rely on `DllMain` for NetIDMgr API calls; instead it calls `kmm_set_locale_info()` for localization and `kmm_provide_plugin()` for every plugin implemented by the module. If it returns `KHM_ERROR_SUCCESS` and provides plugins, KMM initializes those plugins and routes KMQ messages to their message processors. On unload or failed init, KMM stops plugins, then calls optional `exit_module()` before unloading the module and any resource libraries.

## State and Persistence Behavior

The callback declarations themselves hold no state. Module/plugin runtime state is tracked by KMM handles and plugin message processors. Registration metadata and locale information are persisted or managed through `kmm.h`. A module that provides no plugins is immediately exited and unloaded even if `init_module()` succeeds.

## Dependencies and Integration Points

`kplugin.h` includes `kmm.h` and `kherror.h`. It is consumed by plugin DLLs and by KMM's dynamic loader. The callback contracts interact with KMQ (`_plugin_proc_t`), module locale/resource APIs, and plugin registration/lifecycle state in `kmm.h`.

## Risks and Edge Cases

- Export decoration differs by architecture; incorrect `.def` files or compiler calling conventions make modules unloadable.
- Calling NetIDMgr APIs from `DllMain` can deadlock or observe uninitialized subsystems; the header explicitly directs initialization into `init_module()`.
- `exit_module()` is optional and its return value is ignored, so critical cleanup should generally live in per-plugin shutdown paths as well.
- `init_module()` success without provided plugins still causes immediate unload.
- The documentation mentions `kmm_set_locale()` but the declared API in `kmm.h` is `kmm_set_locale_info()`, so plugin authors should follow the actual declaration.

## Test Signals

- Build sample plugins for x86 and x64 and verify exported names match `EXP_INIT_MODULE` and `EXP_EXIT_MODULE`.
- Load a module that provides one plugin, multiple plugins, no plugins, and an init failure.
- Confirm `kmm_provide_plugin()` is accepted only during `init_module()`.
- Verify KMQ messages reach `_plugin_proc` and shutdown calls `exit_module()` after plugin exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kplugin.h -->
