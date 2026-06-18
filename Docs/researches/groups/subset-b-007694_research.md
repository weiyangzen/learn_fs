# subset-b-007694 research

This grouped report covers the requested OpenAFS Windows afsapplib controls and dialog helper sources. Each source file has a separately titled section wrapped in the exact reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_time.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_time.cpp

Purpose: implements the `Time` custom Win32 control registered by `RegisterTimeClass()`. The control presents an hour edit, minute edit, optional AM/PM owner-drawn listbox, and spinner buddy as one logical time input bound to `SYSTEMTIME` hour/minute fields.

Important APIs/types/functions: `TimeInfo` is the per-control state record stored in a global `aTime` table protected by `csTime`. `RegisterTimeClass()` registers class `Time`. `TimeProc()` handles `WM_CREATE`, focus/enabled forwarding, keyboard spinner commands, and `TM_GETTIME`/`TM_SETTIME`. `TimeDlgProc()` subclasses the parent dialog to route child control notifications, colors, AM/PM measuring/drawing, and spinner updates. `TimeEditProc()` subclasses child edit/listbox controls. `Time_OnCreate()` builds children using locale-specific separators, 12/24-hour mode, leading-zero mode, and AM/PM strings. `Time_Edit_OnSetFocus()`, `Time_Edit_OnUpdate()`, and `Time_Edit_SetText()` synchronize spinner range/format and the backing `SYSTEMTIME`. `Time_SendCallback()` emits `TN_UPDATE` while guarding reentrant callbacks.

Control flow: creation allocates or reuses a `TimeInfo` slot, then builds child windows next to the placeholder control in the parent dialog. Parent subclassing receives spinner/listbox updates and dispatches them back to the owning `TimeInfo`. Setting focus to the outer control posts focus to the hours edit; focusing a child retargets the spinner to that field and sets its legal range. User edits or spinner changes update `timeNow`, normalize invalid `24:xx` to `24:00`, and notify the parent. `TM_GETTIME` copies only time fields back to the caller; `TM_SETTIME` replaces `timeNow` and refreshes child text.

State and persistence behavior: all state is process-local UI state. `aTime` grows in four-entry increments through `TimeReallocFunction()` and slots are reused after `WM_DESTROY` clears `hTime`. No registry or file persistence exists. `fCanCallBack` and `fCallingBack` suppress callback storms while focus/spinner setup is changing controls programmatically.

Dependencies and integration points: depends on Win32 windowing/common controls, OpenAFS allocation helpers from `afs/stds.h`, `WINNT/subclass.h`, `WINNT/ctl_spinner.h`, `WINNT/dialog.h`, `WINNT/resize.h`, and `WINNT/TaLocale.h`. It uses dialog helper functions such as `NextControlID()` and `LB_*`, and exposes the public `TM_*` messages plus `TI_GetTime()`/`TI_SetTime()` macros declared in `ctl_time.h`.

Risks: the global state table is protected only while looking up slots; most mutation happens on the UI thread by convention. `WM_CTLCOLOR*` creates a new solid brush for each paint callback without an obvious deletion path, which can leak GDI objects. `Time_OnSetTime()` trusts caller-provided `SYSTEMTIME` values, so invalid hours/minutes can reach display and spinner state until the user changes fields. The 12-hour conversion uses listbox selection and numeric text parsing, so empty text or unexpected listbox state can coerce values to zero. The control resizes and creates siblings in the parent rather than owning all children, making z-order/tab-order and parent subclass removal important.

Test signals: register/create/destroy multiple controls and verify slot reuse; exercise 12-hour and 24-hour locales, leading-zero locale, custom time separator, and localized AM/PM strings; send `TM_SETTIME`/`TM_GETTIME` around edge values such as `00:00`, `12:00`, `23:59`, and `24:00`; verify spinner key handling, focus changes between fields, disabled-state colors, callback suppression, and parent notification `TN_UPDATE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_time.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_time.h -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_time.h

Purpose: declares the public interface for the OpenAFS `Time` custom control implemented in `ctl_time.cpp`.

Important APIs/types/functions: `RegisterTimeClass()` registers the window class. `TM_GETTIME` and `TM_SETTIME` are private `WM_USER` messages that pass a `SYSTEMTIME *` through `LPARAM`. `TN_CHANGE` and `TN_UPDATE` are notification codes sent to the parent through `WM_COMMAND`; this implementation actively uses `TN_UPDATE`. `TI_GetTime()` and `TI_SetTime()` are convenience macros over `SendMessage()`. The header also supplies fallback utility macros such as `THIS_HINST`, `EXPORTED`, `limit`, `inlimit`, `cxRECT`, and `cyRECT`.

Control flow: callers must register the class, create a window of class `Time`, and then use `TI_SetTime()`/`TI_GetTime()` to synchronize a `SYSTEMTIME`. Parent dialogs receive notification codes in `HIWORD(wParam)` from `WM_COMMAND`.

State and persistence behavior: the header owns no state. Its message contract exposes transient process-local state held by the control instance.

Dependencies and integration points: intended for Win32 dialog code. It relies on `windows.h`-style types and is consumed alongside `WINNT/dialog.h`, `WINNT/ctl_spinner.h`, and the OpenAFS Windows application library.

Risks: the macros do not validate HWNDs or pointers. `TM_GETTIME`/`TM_SETTIME` depend on a valid writable/readable `SYSTEMTIME *`, and the message IDs occupy a fixed `WM_USER+311/312` namespace that must not conflict with other custom control messages in the same window class.

Test signals: compile clients that include only this header after Win32 headers; verify class registration and message macros work from C/C++ dialog code; confirm callers see parent `TN_UPDATE` after changes and that the `SYSTEMTIME` pointer convention remains compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/dialog.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/dialog.cpp

Purpose: provides the OpenAFS Windows application dialog utility layer. It wraps property sheets, FastList/ListView/ComboBox/ListBox/TreeView common operations, browse dialogs, cursor state, context menus, tab helpers, and small HWND utilities used by the Win32 UI codebase.

Important APIs/types/functions: `DialogReallocFunction()` is the local grow-copy-free allocator. Property sheet support centers on `PROPSHEET`, `aPropSheets`, `PropTab_HookProc()`, `PropSheet_HookProc()`, `PropSheet_Create()`, `PropSheet_AddTab()`, `PropSheet_ShowModal()`, `PropSheet_ShowModeless()`, `PropSheet_Free()`, `PropSheet_FindTabParam()`, and `PropSheetChanged()`. FastList helpers include `FL_StartChange()`, `FL_EndChange()`, `FL_SetColumns()`, `FL_AddItem()`, selection/data helpers, `FL_RestoreView()`, and `FL_StoreView()`. ListView helpers mirror that surface with `LV_*` functions plus `LV_SortView()` and `LV_PickInsertionPoint()`. `CB_*`, `LB_*`, and `TV_*` wrap selection preservation and item data lookup. `Browse_Open()` and `Browse_Save()` build `OPENFILENAME` structures from localized filter strings. Miscellaneous helpers include `StartHourGlass()`, `StopHourGlass()`, `DisplayContextMenu()`, `CountChildren()`, `NextControlID()`, `IsAncestor()`, `GetTabChild()`, `GetLastDlgTabItem()`, and `IsPropSheet()`.

Control flow: property sheet creation builds a `PROPSHEETHEADER` and one `PROPSHEETPAGE` per tab, with every page routed through `PropTab_HookProc()`. The global `aPropSheets` registry bridges the time between `PropertySheet()` returning a sheet HWND and individual pages receiving `WM_INITDIALOG`; tab hooks call the caller-provided page proc and maintain reference counts. Modal display is implemented by showing a modeless sheet, disabling the parent, and running a local message pump until the sheet closes. Control refresh helpers generally capture the selected item's `LPARAM`, suppress redraw or call `FastList_Begin()`, reset/repopulate, then restore selection by matching item data. Browse helpers temporarily switch the current directory to the caller's last directory, show the common dialog, store the resulting current directory, and restore the original process current directory.

State and persistence behavior: property-sheet bookkeeping is global in-memory state and is freed when page/sheet reference counts drop. `VIEWINFO` is caller-owned state used to persist list or FastList view mode, column order/width/justification, and sort style across UI refreshes or sessions if the caller stores it elsewhere. `nHourGlassRequests` is a process-global nesting count. Browse functions mutate `pszLastDirectory` with the last current directory but do not write persistent storage directly.

Dependencies and integration points: depends on Win32 `commctrl`, `commdlg`, property sheet APIs, OpenAFS allocation/string helpers from `afs/stds.h` and `WINNT/talocale.h`, subclass support, and the custom FastList API. The file is the compatibility adapter used by higher-level OpenAFS admin/client UI dialogs that want one set of helpers for native common controls and FastList.

Risks: the property-sheet registry has no critical section and assumes UI-thread access. Reference-count/free behavior is subtle because tabs and sheets can destroy each other through hook callbacks. `Browse_Open()` and `Browse_Save()` change the process current directory, which can affect unrelated code if invoked concurrently. Many wrappers use `0` or `(UINT)-1` as not-found sentinels; a valid item with `LPARAM 0` cannot be distinguished from no selection by helpers such as `*_GetSelectedData()`. Several varargs helpers assume the caller passes exactly the expected number and type of `LPTSTR` arguments. `LV_SortView()` indexes `lpvi->cxColumns[lpvi->iSort]` while `iSort` may carry `COLUMN_SORTREV`, so callers must preserve the expected bit masking.

Test signals: property sheets should be tested for modal/modeless creation, start page, help/apply/cancel forwarding, page destruction, and `WM_INITDIALOG_SHEET`/`WM_DESTROY_SHEET` broadcast. Control wrappers need selection-preservation tests for no selection, `LPARAM 0`, duplicate item data, and reset/no-reset paths. View restore/store tests should cover column subsets, justification flags, sort reversal, and switching between icon/list/tree modes. Browse helpers should verify filter delimiter conversion and current-directory restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/dialog.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/dialog.h -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/dialog.h

Purpose: declares the public utility API implemented by `dialog.cpp` for OpenAFS Win32 dialogs and common controls.

Important APIs/types/functions: `PROPSHEET` extends `PROPSHEETHEADER` with tab metadata and caller `lpUser`. `VIEWINFO` captures view style, available/shown columns, column resource IDs, widths/justification flags, and sort column/reverse bit. Constants include `IDINIT`, `IDAPPLY`, `IDHELP`, property-sheet lifecycle messages `WM_INITDIALOG_SHEET` and `WM_DESTROY_SHEET`, `nCOLUMNS_MAX`, `COLUMN_*` flags, and `INDEX_SORT`. The header declares `PropSheet_*`, `FL_*`, `LV_*`, `CB_*`, `LB_*`, `TV_*`, `Browse_*`, and miscellaneous HWND/cursor/menu helpers.

Control flow: callers include this header to build property sheets, preserve and restore view state, batch control updates, add rows/items, retrieve selected item data, and use common dialog helpers. `StartChange()`/`EndChange()` pairs form the expected update transaction pattern for FastList, ListView, ComboBox, ListBox, and TreeView controls.

State and persistence behavior: `VIEWINFO` is the only explicit persistence carrier in the interface; callers can store it to restore view mode and columns later. `PROPSHEET` is heap-allocated by `PropSheet_Create()` and owned by the property-sheet lifecycle until `PropSheet_Free()`.

Dependencies and integration points: includes `commctrl.h`, `commdlg.h`, and `WINNT/fastlist.h`, so it exposes both native common-control and custom FastList types. It is a central include for OpenAFS Windows UI code that needs resource-string based columns, property sheets, list wrappers, browse dialogs, and tab helpers.

Risks: the API is macro- and HWND-heavy, so type safety is limited. `VIEWINFO` has fixed `nCOLUMNS_MAX` arrays and requires callers to keep `nColsAvail`, `nColsShown`, and `aColumns[]` coherent. The `Set2State`/`Set3State`, `CheckMenu`, and `EnableMenu` macros directly send Win32 messages without validation. Function declarations mix `LPARAM` cookies, resource IDs, string pointers, and varargs, making call-site correctness important.

Test signals: compile coverage for C++ default arguments and varargs declarations; property-sheet callbacks receiving `IDINIT`/`IDAPPLY`/`IDHELP`; column view round trips through `VIEWINFO`; and common-control selection helpers across empty, single, and duplicate-data controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/dialog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/fastlist.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/fastlist.cpp

Purpose: implements `WC_FASTLIST`, an OpenAFS custom Win32 list control that combines ListView-like large/small/list modes, TreeView-like hierarchy, TreeList columns, owner-drawn rendering, fast item lookup by user `LPARAM`, custom sorting, selection policies, scrolling, and drag notifications.

Important APIs/types/functions: `_FASTLISTITEM` stores user data, visible index, images, list/tree/selection links, visibility/expanded/selected/focused flags, item flags, and per-column text. `FASTLIST` stores HWNDs, style, scroll offsets, per-control critical section, pending repaint/sort/sync flags, image lists, text and sort callbacks, hash list, list/tree/selection roots, drag state, columns, and visible heap. `FASTLIST_GLOBAL fg` stores a shared double-buffer bitmap and shared sort/object array under a global critical section. `RegisterFastListClass()` registers the window class. `FastList_ControlProc()` dispatches Win32 messages and `FLM_*` API messages. `FastList_ParentProc()` handles owner-draw and auto-sort-header notifications. Command handlers implement add/remove, text/param/flag/image changes, expand/collapse, focus, image lists, drag image creation, sorting, columns, selection, enumeration, item hit testing, region calculation, and text callbacks. Support routines implement painting, layout, header/scroll synchronization, sorting, visibility repair, selection enforcement, ensure-visible, mouse/keyboard behavior, and default sort functions.

Control flow: `WM_CREATE` allocates `FASTLIST`, stores it in extra window bytes, creates a hash key for `lpUser`, optionally adds `WS_CLIPCHILDREN`, syncs header/scroll state, and subclasses the parent. Public macros in `fastlist.h` send `FLM_*` messages to `FastList_ControlProc()`, which calls the matching command handler. Mutating operations set deferred flags such as `fSortBeforePaint`, `fSyncIndicesBeforePaint`, and `fSyncScrollBeforePaint`; `FastList_Begin()`/`FastList_End()` batches these operations and delays repaint. Painting first performs deferred sort/index/scroll/ensure-visible work, calculates the client field after header/scrollbars, paints through a shared compatible bitmap when possible, and delegates item rendering by current view style. User input flows through hit testing and region calculation: clicks can expand tree buttons, select/anchor/range-select items, focus items, initiate drag notifications, or post context menus; keyboard arrows navigate visible heap and expand/collapse tree nodes.

State and persistence behavior: state is entirely in memory per control, except caller-owned view persistence through `dialog.cpp` helpers. Items are linked simultaneously through all-items list, tree sibling/child chains, and selection chain. The `aVisibleHeap` array is rebuilt from sorted visible items and provides O(1) visible-index navigation. `HASHLIST` with key `lkUserParam` supports quick `LPARAM` lookup and enumerations. Column definitions own allocated header text. Item text can be stored per item or lazily obtained through a text callback/`FLN_GETITEMTEXT`; lazy text uses static reusable buffers. No disk or registry writes occur.

Dependencies and integration points: depends on Win32 drawing, headers, scrollbars, image lists, keyboard/mouse capture, and notifications. It integrates with OpenAFS `WINNT/hashlist.h`, `WINNT/subclass.h`, `WINNT/TaLocale.h`, and allocation helpers. Public integration is through `fastlist.h` macros and notifications such as `FLN_GETITEMTEXT`, `FLN_ITEMCHANGED`, `FLN_ADDITEM`, `FLN_REMOVEITEM`, `FLN_COLUMNCLICK`, `FLN_COLUMNRESIZE`, `FLN_ITEMSELECT`, `FLN_ITEMEXPAND`, and drag notifications. `dialog.cpp` builds higher-level `FL_*` wrappers over these messages.

Risks: the code stores a pointer with `SetWindowLong()`/`GetWindowLong()` and `cbWndExtra = 4`, which is 32-bit specific and unsafe for 64-bit HWND extra data. `FastList_OnCommand_Sort()` appears to clear `fSortBeforePaint` rather than force a sort, so explicit `FastList_Sort()` deserves regression coverage. `FastList_OnCommand_IsSelected()` dereferences `hItem` without a null guard. Global sort/object and text buffers mean reentrancy and multi-control interactions are delicate, although the global arrays are guarded during sort/paint allocation. Parent subclassing is added/removed per control and can become complex when several FastLists share a parent. Many APIs trust `HLISTITEM` handles from callers; stale handles after removal can corrupt or crash. GDI resource management in drag image creation and double buffering needs leak coverage.

Test signals: class registration and create/destroy with multiple controls under one parent; all view modes with and without columns, image lists, headers, and scrollbars; add/remove recursive tree items and verify list/tree/selection/hash links; visible heap repair after sorting, collapsing, `FLIF_TREEVIEW_ONLY`, and style changes; single, multiple, sibling, and level selection with mouse, shift/control, and keyboard; text callback growth and lazy columns; header resize/click/autosort; drag begin/drag/end and context menu paths; 32-bit pointer assumptions if porting to 64-bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/fastlist.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/fastlist.h -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/fastlist.h

Purpose: declares the public API, styles, messages, notification structures, and helper macros for the OpenAFS FastList custom control implemented by `fastlist.cpp`.

Important APIs/types/functions: `WC_FASTLIST` names the window class. `HLISTITEM` is the opaque item handle. View styles include `FLS_VIEW_LARGE`, `FLS_VIEW_SMALL`, `FLS_VIEW_LIST`, `FLS_VIEW_TREE`, and `FLS_VIEW_TREELIST`; behavior flags include sorting-header, multi-selection, sibling/level selection, root lines, long columns, text-only hit testing, and autosort header. Item flags include `FLIF_TREEVIEW_ONLY`, `FLIF_DROPHIGHLIGHT`, `FLIF_DISALLOW_COLLAPSE`, and `FLIF_DISALLOW_SELECT`. Structures define add-item input, item drawing/regions, columns, item image/text addressing, text callbacks, sort callbacks, and all `FLN_*` notification payloads. The `FastList_*` macros wrap `SendMessage()` for batching, item CRUD, images, expansion, visibility/focus, image lists, drag images, sorting, columns, selection, enumeration, hit testing, regions, and text callbacks. Exported functions include class registration, type check, explicit enter/leave critical-section helpers, and default sort callbacks.

Control flow: clients register the class, create a `WC_FASTLIST` window with desired `FLS_*` styles, set columns/image lists/text callback/sort callback as needed, add items through `FastList_AddItem()`, and react to parent `WM_NOTIFY` notifications. Most API calls are synchronous `SendMessage()` calls into the control window procedure.

State and persistence behavior: the header does not store state, but its API exposes the control's in-memory item, column, selection, sort, and view state. Persistent view storage is intentionally external and usually handled through `VIEWINFO` in `dialog.h`.

Dependencies and integration points: includes `commctrl.h` for common-control types, image lists, headers, and notification conventions. It is consumed directly by `dialog.h`/`dialog.cpp` and OpenAFS Windows UI code that needs a fast hierarchical list with custom notifications.

Risks: the API is macro-based and trusts HWND/HLISTITEM lifetimes. Enumeration with `LPENUM *` requires callers to call `FastList_FindClose()` when stopping early. Notification handlers must return `TRUE` when they handle text or behavior requests, especially `FLN_GETITEMTEXT` and `FLN_BEGINDRAG`. Message IDs and notification codes live in fixed custom ranges and must stay coordinated with the implementation.

Test signals: compile and runtime tests for every macro message; notification structure layout compatibility; item add/remove and enumeration contracts including early close; selection mode behavior; custom sort callback and text callback invocation; drag-image creation; and style combinations such as `FLS_AUTOSORTHEADER` versus `FLS_NOSORTHEADER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/fastlist.h -->
