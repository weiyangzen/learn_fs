# Research: subset-b-009891

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_list.c -->
# sources/user-network-fs/samba/source3/utils/regedit_list.c

## Purpose
`regedit_list.c` implements `struct multilist`, a reusable ncurses-backed table/pad widget used by Samba's terminal registry editor. It separates presentation from data by requiring callers to provide `struct multilist_accessors`, then handles column sizing, header drawing, row rendering, cursor movement, scrolling, and window resize rerendering.

## Important APIs, Types, And Functions
The file defines private `struct multilist` state: outer `WINDOW`, backing `pad`, dimensions, scroll start, cursor row, column metadata, opaque data pointer, current row pointer, and accessor callbacks. Public entry points are `multilist_new`, `multilist_column_config`, `multilist_set_window`, `multilist_set_data`, `multilist_refresh`, `multilist_driver`, `multilist_get_current_row`, and `multilist_set_current_row`. Internal helpers provide fallback implementations for row count, previous row, and row-by-index when callbacks are absent. `put_item`, `put_header`, `put_data`, and `calc_column_widths` perform rendering and truncation.

## Control Flow
Construction allocates a talloc object and column array, installs a destructor, and binds the ncurses window. `multilist_set_data` recalculates column widths, recreates the pad, draws headers into the window, draws all rows into the pad, and initializes selection to the first row. Navigation enters through `multilist_driver`, which maps abstract cursor commands to row-index changes, uses callback/fallback row lookup to update `current_row`, highlights/unhighlights pad rows, and calls `fix_start_row` to keep selection visible. `multilist_refresh` copies the visible pad slice into the visible window, accounting for a header row.

## State And Persistence
State is in-memory UI state only. The source data is not owned by `multilist`; it is held as an opaque pointer and must remain valid for the lifetime of rendering and navigation. The pad is owned by the list and deleted by the talloc destructor. Resize can rerender the backing pad and then restore the previously selected row by pointer identity.

## Dependencies And Integration Points
The implementation depends on Samba `talloc`, `WERROR`, `SMB_ASSERT`, and ncurses primitives. It integrates with `regedit_treeview.c` and `regedit_valuelist.c`, which implement the accessors for registry key and value rows. Color pair `PAIR_YELLOW_BLUE` comes from `regedit.h`.

## Risks
The data contract is pointer-identity based, so changing or reallocating rows behind the list can invalidate `current_row` and selection restoration. Fallback `get_prev_row` and `get_row_n` are O(n), so very large lists should provide fast callbacks. `multilist_set_data` highlights row zero even when no rows exist; the pad is allocated with at least one row, but consumers should still avoid interpreting `current_row` when `nrows == 0`.

## Test Signals
Useful tests or manual checks include empty data sets, long labels that force `~` truncation, right-aligned columns, missing optional callbacks, page up/down at boundaries, window width changes preserving selection, and valgrind/leak checks for repeated data reloads and resizes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_list.h -->
# sources/user-network-fs/samba/source3/utils/regedit_list.h

## Purpose
`regedit_list.h` declares the generic multicolumn list interface used by the registry editor UI. It exposes a compact table model in which callers provide row traversal and cell-label callbacks while the implementation owns ncurses rendering and cursor behavior.

## Important APIs, Types, And Functions
`struct multilist_accessors` is the central integration contract. Required callbacks are `get_first_row`, `get_next_row`, and `get_item_label`; optional callbacks add headers, row count, previous row, row-by-index, and item prefixes. `struct multilist_column` exposes width and `align_right` configuration. The header declares creation, column configuration, window/data binding, refresh, cursor driver commands, and current-row accessors. Cursor commands are enumerated as `ML_CURSOR_UP`, `ML_CURSOR_DOWN`, `ML_CURSOR_PGUP`, `ML_CURSOR_PGDN`, `ML_CURSOR_HOME`, and `ML_CURSOR_END`.

## Control Flow
Consumers instantiate with `multilist_new`, optionally tune columns through `multilist_column_config`, pass data through `multilist_set_data`, and call `multilist_driver` in response to key events. UI containers call `multilist_set_window` during resize and `multilist_refresh` during paint.

## State And Persistence
The header defines an opaque `struct multilist`; ownership and persistence details remain hidden in the C file. The public contract implies that row pointers returned by accessors must remain stable enough to serve as selection handles.

## Dependencies And Integration Points
The header depends on Samba `includes.h`, `TALLOC_CTX`, `WERROR`, and ncurses `WINDOW`. It is used directly by `regedit_treeview.c` and `regedit_valuelist.c`.

## Risks
Callback nullability is partly documented in comments but enforced by runtime assertions in the implementation. Callers must match the advertised number of columns and must not return transient strings or rows that disappear during rendering.

## Test Signals
Compile-time coverage should catch signature drift between accessors and implementations. Runtime tests should exercise a consumer with only required callbacks and another with optional fast callbacks to verify fallback behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_samba3.c -->
# sources/user-network-fs/samba/source3/utils/regedit_samba3.c

## Purpose
`regedit_samba3.c` adapts Samba3 registry APIs into Samba's generic `struct registry_operations` interface for the terminal registry editor. It lets regedit treat Samba3 registry hives as regular registry contexts, keys, subkeys, and values.

## Important APIs, Types, And Functions
Private `struct samba3_key` embeds a generic `struct registry_key` plus a `struct samba3_registry_key` wrapper. `struct samba3_registry_context` embeds `struct registry_context`. The `reg_backend_s3` operation table implements `open_key`, `get_predefined_key`, key/value enumeration, value get/set/delete, key create/delete, and key info lookup. `reg_open_samba3` initializes the wrapped Samba3 registry subsystem and returns a generic registry context.

## Control Flow
`reg_open_samba3` calls `reg_init_wrap`, allocates context state, and assigns the backend ops table. Predefined-key lookup maps Windows hive constants to short hive names such as `HKLM` and `HKCU`, allocates a `samba3_key`, and calls `reg_openhive_wrap`. Child opens, enumeration, queries, mutations, and info calls downcast generic keys with `talloc_get_type` and delegate to `regedit_wrap.c`.

## State And Persistence
The file stores no global mutable state beyond the static operation table and hive map. Persistent registry state is changed by wrapper calls such as `reg_setvalue_wrap`, `reg_createkey_wrap`, and `reg_deletekey_wrap`, which operate on Samba3 registry storage.

## Dependencies And Integration Points
It depends on `lib/registry/registry.h`, `regedit.h`, and the wrapper API from `regedit_wrap.c`. It integrates with higher-level regedit code through `reg_open_samba3` and the generic registry interface used by tree and value views.

## Risks
The backend ignores `key_class` and `sec` in create-key operations, so security/class metadata is not honored here. Predefined hives unsupported by Samba3 simply return `WERR_NO_MORE_ITEMS`. All opened keys request read/write access through the wrappers, so permission failures can affect even read-oriented UI operations.

## Test Signals
Tests should open each known predefined hive, enumerate subkeys and values, create/delete a temporary key, set/delete a value, and verify unsupported hives fail cleanly. Memory ownership tests should ensure returned generic keys retain their wrapped Samba3 keys.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_samba3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_treeview.c -->
# sources/user-network-fs/samba/source3/utils/regedit_treeview.c

## Purpose
`regedit_treeview.c` implements the left-side registry key browser for Samba's ncurses regedit. It models registry keys as talloc-owned `tree_node` objects, lazily loads subkeys, traverses sibling/depth-first order, and presents the current level through `multilist`.

## Important APIs, Types, And Functions
Key node APIs include `tree_node_new`, `tree_node_new_root`, `tree_node_append`, `tree_node_pop`, `tree_node_first`, `tree_node_last`, `tree_node_next`, `tree_node_prev`, `tree_node_load_children`, `tree_node_reopen_key`, `tree_node_get_path`, and `tree_node_print_path`. View APIs include `tree_view_new`, `tree_view_resize`, `tree_view_show`, `tree_view_set_root`, `tree_view_set_path`, `tree_view_update`, selection helpers, and `tree_view_driver`. Static multilist accessors render a single `Name` column with `+` prefix for nodes that have children.

## Control Flow
`tree_node_new_root` creates an artificial `ROOT` and tries to add all known hives whose `reg_get_predefined_key_by_name` calls succeed. Child loading starts by querying `reg_key_get_info`, enumerating subkey names, opening each subkey, creating child nodes, sorting them with `TYPESAFE_QSORT`, and linking the sibling list. `tree_node_next` and `tree_node_prev` can move either among siblings or depth-first, forcing lazy loads as needed. The view allocates a boxed ncurses window plus subwindow, creates a one-column multilist, and refreshes it with the current sibling list.

## State And Persistence
Tree nodes own duplicated names and steal opened `registry_key` handles. Loaded children persist under their parent until the root/view is freed. `tree_node_reopen_key` drops and reopens a node key, supporting refresh after external or UI mutations. The UI state is current-row selection inside `multilist`.

## Dependencies And Integration Points
The file depends on `regedit_treeview.h`, `regedit_list.h`, ncurses panels, and generic registry APIs. It is a bridge between registry backends such as `regedit_samba3.c` and higher-level regedit command/search behavior.

## Risks
Lazy loading means `tree_node_has_children` may perform registry info calls during rendering through `tv_get_item_prefix`, which can be expensive or fail-sensitive. `tree_view_set_path` returns `WERR_OK` if a path component is not found after walking, so callers need to verify selection if exact restoration matters. Node list manipulation depends on parent `child_head` consistency.

## Test Signals
Tests should cover root hive creation with unavailable hives, sorted child enumeration, depth-first next/previous across nested nodes, pop/insert behavior at list head, resize repainting, path reconstruction, and reopen after key changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_treeview.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_treeview.h -->
# sources/user-network-fs/samba/source3/utils/regedit_treeview.h

## Purpose
`regedit_treeview.h` declares the registry tree model and ncurses view surface used by regedit. It exposes linked `tree_node` objects and a `tree_view` wrapper around windows, panel, root node, and multilist.

## Important APIs, Types, And Functions
`struct tree_node` contains a display name, opened `registry_key`, parent pointer, first child, and sibling links. `struct tree_view` stores root, frame/sub windows, panel, and list widget. Macros `tree_node_is_root` and `tree_node_is_top_level` classify artificial root and hive-level nodes. The header declares creation, sibling operations, traversal, lazy loading, path printing/getting, view construction/resizing/showing, root/path/current-node updates, selection highlighting, and key reopening.

## Control Flow
Callers create a root with `tree_node_new_root`, pass it to `tree_view_new`, feed UI input to `tree_view_driver`, and request child loading or path changes through tree APIs. The view exposes current selection as a `tree_node`, which other regedit components use to load values or perform mutations.

## State And Persistence
The declared structs are not opaque, so callers can inspect and manipulate links directly. Ownership is talloc-based; registry keys are expected to be children of their corresponding nodes after construction or reopening.

## Dependencies And Integration Points
The header pulls in Samba basics plus ncurses and panel APIs. It forward-declares `registry_key`, `registry_context`, and `multilist` to connect the generic registry layer with UI code.

## Risks
Because internals are public, misuse can break sibling or parent invariants. The macros assume non-null parent relationships for top-level checks, so callers must only pass properly initialized nodes.

## Test Signals
Build checks should catch signature drift with `regedit_treeview.c`. Structural tests should assert that root, top-level hive, child, and sibling pointers meet the invariants expected by traversal and view visibility helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_treeview.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_valuelist.c -->
# sources/user-network-fs/samba/source3/utils/regedit_valuelist.c

## Purpose
`regedit_valuelist.c` implements the right-side registry value table for regedit. It loads values from a selected registry key, summarizes registry data into printable strings, sorts values by name, supports search navigation, and renders through the shared `multilist` table widget.

## Important APIs, Types, And Functions
Public APIs include `value_list_new`, `value_list_resize`, `value_list_show`, `value_list_set_selected`, `value_list_load_quick`, `value_list_sync`, `value_list_load`, `value_list_find_next_item`, `value_list_find_prev_item`, current-item getters/setters, and `value_list_driver`. Static accessors expose three columns: `Name`, `Type`, and `Data`. `append_data_summary` formats `REG_DWORD`, `REG_SZ`, `REG_EXPAND_SZ`, `REG_MULTI_SZ`, `REG_BINARY`, and unknown types.

## Control Flow
Construction creates a boxed window, subwindow, panel, and three-column multilist. `value_list_load_quick` clears old state, queries value count through `reg_key_get_info`, enumerates each value with `reg_key_get_value_by_index`, and sorts the array by value name. `value_list_sync` walks the loaded values, appends human-readable data summaries, binds the list data, and refreshes the UI. Searches linearly scan forward or backward from the current item using a caller-provided match function.

## State And Persistence
`struct value_list` owns a talloc array of `struct value_item`; each item stores the registry type, raw `DATA_BLOB`, value name, rendered summary string, and an `unprintable` flag. This is an in-memory snapshot of a registry key. Persistence occurs only through external registry edit paths; this file reads and displays.

## Dependencies And Integration Points
The file depends on regedit headers, `regedit_list.h`, generic registry APIs, registry type string helpers, and data conversion helpers such as `pull_reg_sz` and `pull_reg_multi_sz`. It is driven by tree selection changes from `regedit_treeview.c`.

## Risks
Backward search computes `&vl->values[-1]` as a sentinel, which is a common C idiom but formally outside the allocated object. Formatting large multi-string values can allocate very long display strings. `string_is_printable` uses `isprint(*p)` on `char`, which can be locale/signedness sensitive for high-bit bytes.

## Test Signals
Tests should load keys with zero values, all supported registry types, unprintable strings, large binary and multi-string values, sorted names, current-item restoration by name, and forward/backward search boundary cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_valuelist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_valuelist.h -->
# sources/user-network-fs/samba/source3/utils/regedit_valuelist.h

## Purpose
`regedit_valuelist.h` declares the registry value-list UI model for regedit. It exposes the value item snapshot structure, the list container, and operations for loading, syncing, searching, selecting, resizing, and driving the ncurses widget.

## Important APIs, Types, And Functions
`struct value_item` stores registry value metadata: `type`, raw `DATA_BLOB`, `value_name`, rendered `value`, and `unprintable`. `struct value_list` stores ncurses windows/panel, value count, value array, and `multilist`. Public functions include `value_list_new`, `value_list_load`, `value_list_load_quick`, `value_list_sync`, `value_list_find_next_item`, `value_list_find_prev_item`, current item helpers, and `value_list_driver`.

## Control Flow
The header supports a two-stage load flow: quick name/type/data enumeration for search and later sync to produce printable summaries and render the table. UI input is passed to the shared list driver.

## State And Persistence
The value list is an in-memory snapshot. The header makes fields public, so callers can inspect `nvalues` and `values`, but mutation must preserve the array and multilist row-pointer assumptions.

## Dependencies And Integration Points
It uses ncurses panels, Samba `DATA_BLOB`, generic `registry_key`, and `regedit_search_match_fn_t` from regedit declarations. It is tightly coupled with `regedit_valuelist.c` and `regedit_list.c`.

## Risks
The public structure layout increases coupling. The declared `value_list_load_names` is not implemented in the corresponding C file in this subset, which is a stale API signal unless implemented elsewhere.

## Test Signals
Compile/link checks should verify all declared symbols used by callers exist. Runtime tests should verify load/sync, cursor movement, and search against stable `value_item` pointers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_valuelist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_wrap.c -->
# sources/user-network-fs/samba/source3/utils/regedit_wrap.c

## Purpose
`regedit_wrap.c` wraps Samba3 registry APIs to avoid type-name conflicts with Samba4 libregistry structures used by regedit. It exposes a small compatibility layer that stores Samba3 `registry_key` pointers inside `struct samba3_registry_key`.

## Important APIs, Types, And Functions
The wrapper functions are `reg_openhive_wrap`, `reg_openkey_wrap`, `reg_enumvalue_wrap`, `reg_queryvalue_wrap`, `reg_enumkey_wrap`, `reg_createkey_wrap`, `reg_deletekey_wrap`, `reg_deletevalue_wrap`, `reg_queryinfokey_wrap`, `reg_setvalue_wrap`, and `reg_init_wrap`. Value wrappers convert `struct registry_value` into type plus `DATA_BLOB`.

## Control Flow
Hive opening creates an admin security token and calls `reg_openhive` with read/write access. Key opens and creates request read/write access. Enumeration/query wrappers call the underlying Samba3 functions and copy out type/data only when the returned registry value exists and the operation succeeds. `reg_setvalue_wrap` constructs a local `registry_value` and delegates to `reg_setvalue`.

## State And Persistence
The wrapper owns no persistent state. It mutates Samba3 registry storage through create/delete/set calls and returns key handles in caller-provided wrapper structs. `reg_init_wrap` initializes the basic registry subsystem.

## Dependencies And Integration Points
It includes Samba3 registry headers, admin token helpers, and `regedit.h`, and is consumed by `regedit_samba3.c`.

## Risks
All opens use read/write access, so read-only operations can fail under restrictive permissions. `reg_openhive_wrap` asserts the output key is initially null, making reuse without clearing fatal in assert builds. Returned `DATA_BLOB` ownership follows the underlying registry value allocation under the caller's talloc context.

## Test Signals
Tests should validate read/write hive opening, value enumeration/query data lifetime, setting/deleting values, creating/deleting keys, and initialization failure propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/regedit_wrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/sharesec.c -->
# sources/user-network-fs/samba/source3/utils/sharesec.c

## Purpose
`sharesec.c` implements the `sharesec` utility for viewing and modifying Samba share security descriptors. It supports Samba ACL text operations, full SDDL import/export, deleting stored descriptors, listing all shares, and machine SID initialization.

## Important APIs, Types, And Functions
Mode selection is represented by `enum acl_mode`: add, modify, delete, replace, view, view-all, delete descriptor, set SDDL, and view SDDL. `parse_acl_string` converts comma-separated ACE text into a self-relative security descriptor with a DACL. `change_share_sec` implements add/delete/modify/set/view behavior against `get_share_security` and `set_share_security`. `set_sharesec_sddl` and `view_sharesec_sddl` use `sddl_decode`/`sddl_encode`. `registry_share`, `txt_share`, and `share_exists` validate that the target share exists in registry-backed or file-backed smbconf.

## Control Flow
`main` initializes Samba command-line state, parses popt options, loads the configuration either with or without registry shares depending on view-all mode, optionally prints/initializes the machine SID, validates option combinations, resolves the share name, checks existence, and dispatches to SDDL or ACL-string handlers. `change_share_sec` loads the old descriptor unless replacing or deleting; parses requested ACEs for mutating modes; applies the chosen transformation; sorts/deduplicates the DACL; and writes the descriptor back.

## State And Persistence
Persistent state is the share security descriptor stored by Samba passdb/registry helpers. `--delete` removes the entire descriptor. `--setsddl`, `--replace`, `--add`, `--modify`, and `--remove` persist modified descriptors. Global `ctx` is a talloc stack frame for process-lifetime allocations.

## Dependencies And Integration Points
The utility depends on Samba command-line initialization, loadparm, smbconf, machine SID helpers, security descriptor utilities, SDDL helpers, and share security APIs from `util_sd.h`. It integrates with both registry and text configuration backends to validate shares.

## Risks
The popt entries for `--setsddl` and `--viewsddl` pass `arg = the_acl` rather than `&the_acl`, but the switch body still obtains the option argument manually for `-S`; the no-argument view case is harmless. ACL parsing assumes comma-separated ACEs and does not support commas inside any future ACE syntax. `--force` is parsed but only rejects view+force; it does not appear to alter persistence behavior in this file.

## Test Signals
Tests should cover share validation in registry and text backends, view/view-all output, add/modify/delete/set with duplicate ACE collapse and deny-before-allow ordering, descriptor deletion, SDDL round trips, invalid ACE/SDDL handling, and machine SID output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/sharesec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/smb_prometheus_endpoint.c -->
# sources/user-network-fs/samba/source3/utils/smb_prometheus_endpoint.c

## Purpose
`smb_prometheus_endpoint.c` is a small libevent HTTP server that exports Samba smbd profiling counters in Prometheus text format. It serves `/metrics`, reads an smbd profile TDB, emits global worker/session/file/tcon metrics, and then emits selected per-share metrics.

## Important APIs, Types, And Functions
`struct export_state` stores the response `evbuffer` and one-shot HELP/TYPE flags for metric families. Export helpers handle count, time, SMB1 basic request, SMB2 input bytes, output bytes, latency histogram, and failed request counters. `export_profile_stats` expands `SMBPROFILE_STATS_ALL_SECTIONS` repeatedly with different macro definitions to visit stats groups. `metrics_handler` handles HTTP metrics requests; `default_handler` returns 404; `main` binds the libevent server.

## Control Flow
Startup parses `-a` address and `-p` port options plus a required TDB filename, creates an event base and HTTP server, binds the socket, registers `/metrics`, and dispatches forever. On `/metrics`, the handler creates a buffer, opens the TDB read/write with mutex locking for global collection, verifies the profile magic, collects aggregate stats, writes gauge/counter families, exports aggregate profile stats, then reopens the TDB read-only and iterates per-service records.

## State And Persistence
The process itself keeps no long-term metrics state; profile data lives in the external TDB. It reads with locking but does not intentionally write. Response-local state prevents duplicate HELP/TYPE lines within a scrape.

## Dependencies And Integration Points
It depends on `tdb`, libevent2 HTTP/buffer APIs, and Samba `smbprofile` collection helpers. It integrates with smbd profiling TDB layout and Prometheus scrape conventions.

## Risks
Metric label values use raw share/service names without Prometheus escaping, so quotes, backslashes, or newlines in service names could produce invalid exposition. On `smbprofile_magic` failure, the handler returns without closing the TDB. The outbytes HELP text says "Bytes received" even though it exports output bytes. The HTTP server has no authentication or TLS; binding defaults to localhost.

## Test Signals
Tests should scrape empty/missing/corrupt TDBs, verify HTTP status codes, validate Prometheus text with unusual service names, compare aggregate and per-service counters against known profile fixtures, and check file descriptor cleanup on error paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/smb_prometheus_endpoint.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/smbcacls.c -->
# sources/user-network-fs/samba/source3/utils/smbcacls.c

## Purpose
`smbcacls.c` implements the `smbcacls` utility for inspecting, changing, saving, restoring, and propagating Windows security descriptors on files over SMB. It supports Samba text ACL syntax, SDDL, owner/group changes, inheritance toggles, maximum-access queries, recursive DACL save, and restore from icacls-compatible UTF-16 files.

## Important APIs, Types, And Functions
Global options track inheritance propagation, save/restore paths, recursion, test mode, SDDL mode, explicit security-info masks, maximum-access queries, and optional domain SID. `sec_desc_parse` parses `REVISION`, `OWNER`, `GROUP`, and `ACL` tokens. `get_secdesc_with_ctx`, `set_secdesc`, `get_fileinfo`, and `cacl_mxac` are the remote SMB primitives. `cacl_dump`, `cacl_set`, `cacl_set_from_sd`, `owner_set`, and `inherit` implement main actions. Inheritance propagation uses `prepare_inheritance_propagation`, `get_inheritable_aces`, `get_flags_to_propagate`, `propagate_inherited_aces`, `cacl_set_cb`, and `inheritance_cacl_set`. Save/restore uses `write_dacl`, `cacl_dump_dacl_cb`, `dump_dacl_dirtree`, `cacl_dump_dacl`, and `cacl_restore`.

## Control Flow
`main` initializes Samba client command-line state, parses options, validates `//server/share filename`, connects to the share, resolves DFS paths with `cli_resolve_path`, normalizes separators, and dispatches in priority order: inherit mode, owner/group change, ACL mutation, save/restore, or dump. ACL mutation parses either SDDL or text, optionally prepares inheritance propagation, applies the change to the target descriptor, canonicalizes ACE order, and writes it via `cli_set_security_descriptor`. Save writes a target DACL as SDDL after clearing owner/group, then optionally recurses through directories with `cli_list`. Restore reads UTF-16 path/SDDL line pairs, decodes SDDL, sets auto-inherit flags, resolves each path, and sets descriptors.

## State And Persistence
Persistent state is remote file security metadata changed through SMB create/query/set calls. Save mode writes a local restore file in icacls-like UTF-16 line format. Domain SID may be obtained remotely over LSA IPC$ or supplied by `--domain-sid`.

## Dependencies And Integration Points
The utility depends on Samba client connection code, LSA RPC for SID lookup, security descriptor and SDDL helpers, DFS path resolution, libsmb `cli_*` file and quota-like calls, command-line credentials, and local file conversion utilities.

## Risks
Security-info masks directly affect requested access; SACL operations require `SEC_FLAG_SYSTEM_SECURITY` and appropriate privileges. Inheritance propagation is complex and recursively mutates children; failures during `cli_list` callbacks are captured in context because `cli_list` may otherwise ignore callback failures. Save/restore assumes an even number of UTF-16 lines and path/SDDL pair ordering. `test_args` exits before network operations in `main`, so it validates only argument shape, not remote semantics.

## Test Signals
Coverage should include text ACL and SDDL parsing errors, owner/group changes, DACL add/delete/modify/set, explicit query/set security masks, maximum-access output, inheritance allow/remove/copy, propagation to nested files and directories, DFS paths, save/restore round trips including share root paths, and no-op `--test-args` behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/smbcacls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/smbcontrol.c -->
# sources/user-network-fs/samba/source3/utils/smbcontrol.c

## Purpose
`smbcontrol.c` implements the `smbcontrol` administrative utility for sending Samba internal messaging commands to daemons or specific process IDs. It controls debug/profile state, asks for replies, triggers print notifications, forces disconnects, manages winbind online/offline state, retrieves diagnostics, and supports developer-only fault/sleep operations.

## Important APIs, Types, And Functions
`send_message` wraps `messaging_send_buf` and `messaging_send_all`; `wait_replies` uses a tevent timer and message loop. Command handlers follow the `do_*` signature and are registered in `msg_types[]`. Reply callbacks include `print_pid_string_cb`, `pong_cb`, `profilelevel_cb`, `print_ringbuf_log_cb`, `print_uint32_cb`, and `winbind_validate_cache_cb`. `parse_dest` resolves `all`, `self`, numeric PIDs, pidfiles, and messaging names DB entries. `do_command` dispatches destination plus subcommand.

## Control Flow
`main` initializes Samba client command-line handling, parses `--timeout`, creates a command-line messaging context and global event context, and executes the selected command. One-way commands validate arguments and send a typed message. Query commands register a reply callback, send request messages, wait until a timeout or first/all replies depending on destination, print "No replies received" on timeout, and deregister. Some commands bypass messaging for local support tasks, such as stack tracing through ptrace/libunwind or editing `winbindd_cache.tdb` before sending online/offline messages.

## State And Persistence
Most commands modify daemon runtime state through Samba messaging. `do_winbind_offline` persists an offline marker in `winbindd_cache.tdb`, retrying to avoid a race with winbind children; `do_winbind_online` removes it. Stacktrace attaches to target processes temporarily. Developer/selftest fault injection can intentionally crash targets.

## Dependencies And Integration Points
The file depends on Samba messaging, server-id and pidfile helpers, tevent, TDB, printing notification helpers, nmb packet structures, loadparm, optional libunwind/ptrace, and command-line global contexts. It is a central control-plane integration point for smbd, nmbd, winbindd, ldap_server, and RPC workers.

## Risks
Administrative commands can disrupt service: shutdown, close-share, kill-client-ip, offline, inject, and sleep are intentionally intrusive. `num_replies` is global and not reset inside every command, relying on one command per process. `do_profilelevel` deregisters `MSG_PROFILE` rather than the registered request/reply pair, which is harmless at process exit but suspicious. Broadcast waits depend on timeout rather than knowing the full recipient set.

## Test Signals
Tests should cover destination resolution, usage errors for every command, timeout behavior, ping/profile/debuglevel replies, winbind online/offline TDB marker behavior, invalid IP rejection, developer gating for inject/sleep, and command table/help consistency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/smbcontrol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/smbcquotas.c -->
# sources/user-network-fs/samba/source3/utils/smbcquotas.c

## Purpose
`smbcquotas.c` implements the `smbcquotas` utility for querying and setting NT quota information on SMB shares. It can show filesystem default quotas, list user quotas, query a single user's quota, set user limits, set filesystem default limits, and set quota flags.

## Important APIs, Types, And Functions
`parse_quota_set` parses `UQLIM:`, `FSQLIM:`, and `FSQFLAGS:` strings into quota type, command, username, and `SMB_NTQUOTA_STRUCT`. `dump_ntquota` and `dump_ntquota_list` format quota records. `do_quota` performs feature detection, opens the quota fake file, and dispatches get/list/set operations. `SidToString` and `StringToSid` optionally resolve SIDs through LSA RPC opened by `cli_open_policy_hnd`.

## Control Flow
`main` parses mutually exclusive quota operation options, defaults to querying the command-line credential username, validates `//server/share`, splits server/share, optionally parses set strings, connects to the share, and calls `do_quota`. `do_quota` checks `FILE_VOLUME_QUOTAS`, opens `FAKE_FILE_NAME_QUOTA_WIN32`, resolves user SIDs for user quota operations, invokes `cli_get_user_quota`, `cli_list_user_quota`, `cli_set_user_quota`, `cli_get_fs_quota_info`, or `cli_set_fs_quota_info`, then prints the resulting state.

## State And Persistence
Set operations persist remote quota state through SMB quota calls. The process maintains global IPC/LSA handles for SID lookup and a global `server` string used by both share and IPC connections.

## Dependencies And Integration Points
It depends on Samba client connection helpers, LSA RPC, fake quota file support, quota list utilities, credentials, and loadparm. It shares SID/name conversion idioms with `smbcacls.c`.

## Risks
`parse_quota_set` mutates the option string in place. `FSQFLAGS` precedence means `DENY_DISK` implies enabled behavior and overrides plain enabled in output flags. The global IPC connection assumes `server` has already been parsed and remains valid. Quota support varies by server and filesystem, so feature detection and fake-file open errors are normal outcomes.

## Test Signals
Tests should cover all set-string syntaxes, invalid/multiple operations, numeric vs resolved SID output, unsupported quotas, disabled quotas, user get/list/set, filesystem limits/flags set, and `--test-args` exit behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/smbcquotas.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/smbfilter.c -->
# sources/user-network-fs/samba/source3/utils/smbfilter.c

## Purpose
`smbfilter.c` is a simple SMB TCP proxy/filter used for debugging and protocol experimentation. It listens locally on port 445, connects each accepted client to a destination server, optionally rewrites NetBIOS session-request destination names, and can inspect or modify selected SMB negotiation/session setup fields.

## Important APIs, Types, And Functions
`save_file` writes captured data to disk. `filter_request` handles NetBIOS session requests and SMB session setup requests. `filter_reply` handles SMB negotiate replies. `send_smb` writes complete NetBIOS-framed SMB messages. `filter_child` proxies one client/server pair using polling and `receive_smb_raw`. `start_filter` binds, listens, resolves the destination, accepts connections, and forks child proxy processes.

## Control Flow
`main` loads Samba global config, accepts `desthost` and optional replacement NetBIOS name, then calls `start_filter`. The listener forks for each client. A child opens an outbound SMB socket, polls client and server descriptors, reads raw SMB packets, applies direction-specific filters, and forwards the packet. Session setup requests save password/session bytes to `sessionsetup.dat` after moving the previous capture aside.

## State And Persistence
Runtime state is per-process sockets and optional global `netbiosname`. Persistent side effects include `sessionsetup.dat` and `sessionsetup1.dat` captures in the current directory. No Samba server state is changed except through forwarded traffic and packet modifications.

## Dependencies And Integration Points
The file depends on Samba socket helpers, NetBIOS name parsing/mangling, SMB packet layout macros, polling wrappers, and raw SMB receive/write helpers. It integrates externally as a local TCP proxy in front of an SMB server.

## Risks
The utility binds privileged port 445 and forks unbounded children. Capturing session setup data may write sensitive authentication material to disk. Capability/security masks are currently zero, but changing macros can silently alter protocol negotiation. `system("mv ...")` is avoidable and may fail based on environment.

## Test Signals
Manual tests should proxy a client through localhost to a test server, verify NetBIOS name rewrite, confirm packet forwarding in both directions, exercise disconnects, inspect captured session setup files, and test IPv4/IPv6 destination resolution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/smbfilter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/smbget.c -->
# sources/user-network-fs/samba/source3/utils/smbget.c

## Purpose
`smbget.c` implements `smbget`, a wget-like downloader for `smb://` URLs using libsmbclient. It supports recursive traversal, resume, update-if-newer, stdout or named output, progress display, guest/credential handling, SMB encryption selection, Kerberos options, NT hash passwords, winbind credential cache use, and rate limiting.

## Important APIs, Types, And Functions
`struct opt` stores output, block size, verbosity/progress, stdout/update, and rate limit options. `get_auth_data_with_context_fn` bridges Samba command-line credentials into libsmbclient auth callbacks. `smb_download_dir` recursively lists directories/shares and calls `smb_download_file`. `smb_download_file` implements remote open/stat, local path selection, update/resume checks, transfer loop, progress, and rate limiting. `human_readable`, `print_time`, and `print_progress` format status; signal handlers update terminal width and cleanly print totals on exit.

## Control Flow
`main` initializes command-line state, installs signals, parses options, validates incompatible mode combinations, initializes an `SMBCCTX`, maps Samba credential encryption/Kerberos/NT-hash/ccache options into libsmbclient options, and iterates URLs. Non-recursive mode downloads the given URL as one file; recursive mode walks directories and shares. Resume verifies a 512-byte overlap before restarting from a prior local offset. Rate limiting uses a 100ms token-bucket-like bucket and may shrink block size.

## State And Persistence
Persistent state is local downloaded files and directories. Resume and update modes inspect local file size and mtime. Global counters track total downloaded bytes and elapsed time for process summary. Credentials are stored in Samba's command-line credential object and passed to libsmbclient.

## Dependencies And Integration Points
It depends on libsmbclient, Samba command-line credentials, gensec features, loadparm configuration, POSIX file APIs, terminal sizing, and signals. It is a user-facing client utility rather than a daemon integration.

## Risks
Recursive downloads create local paths directly from remote names and can collide with existing files. Resume opens local files without truncation and relies on overlap matching, but the download loop does not explicitly seek the remote handle to `offset_download` after overlap verification, so resume behavior should be scrutinized against libsmbclient seek position. `--update` compares mtimes only. Rate limiting uses `clock()`, which measures CPU time on some platforms, not wall time.

## Test Signals
Tests should cover guest and credential auth, encryption-required connections, single-file download, stdout output, output-file conflicts, recursive share traversal, skipped printer/IPC shares, resume success/failure overlap, update mode mtime skipping, progress width changes, rate limiting, and signal-triggered clean exit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/smbget.c -->
