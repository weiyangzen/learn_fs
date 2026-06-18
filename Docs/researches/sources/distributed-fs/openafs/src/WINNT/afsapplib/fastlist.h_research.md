# sources/distributed-fs/openafs/src/WINNT/afsapplib/fastlist.h

Purpose: declares the public API, styles, messages, notification structures, and helper macros for the OpenAFS FastList custom control implemented by `fastlist.cpp`.

Important APIs/types/functions: `WC_FASTLIST` names the window class. `HLISTITEM` is the opaque item handle. View styles include `FLS_VIEW_LARGE`, `FLS_VIEW_SMALL`, `FLS_VIEW_LIST`, `FLS_VIEW_TREE`, and `FLS_VIEW_TREELIST`; behavior flags include sorting-header, multi-selection, sibling/level selection, root lines, long columns, text-only hit testing, and autosort header. Item flags include `FLIF_TREEVIEW_ONLY`, `FLIF_DROPHIGHLIGHT`, `FLIF_DISALLOW_COLLAPSE`, and `FLIF_DISALLOW_SELECT`. Structures define add-item input, item drawing/regions, columns, item image/text addressing, text callbacks, sort callbacks, and all `FLN_*` notification payloads. The `FastList_*` macros wrap `SendMessage()` for batching, item CRUD, images, expansion, visibility/focus, image lists, drag images, sorting, columns, selection, enumeration, hit testing, regions, and text callbacks. Exported functions include class registration, type check, explicit enter/leave critical-section helpers, and default sort callbacks.

Control flow: clients register the class, create a `WC_FASTLIST` window with desired `FLS_*` styles, set columns/image lists/text callback/sort callback as needed, add items through `FastList_AddItem()`, and react to parent `WM_NOTIFY` notifications. Most API calls are synchronous `SendMessage()` calls into the control window procedure.

State and persistence behavior: the header does not store state, but its API exposes the control's in-memory item, column, selection, sort, and view state. Persistent view storage is intentionally external and usually handled through `VIEWINFO` in `dialog.h`.

Dependencies and integration points: includes `commctrl.h` for common-control types, image lists, headers, and notification conventions. It is consumed directly by `dialog.h`/`dialog.cpp` and OpenAFS Windows UI code that needs a fast hierarchical list with custom notifications.

Risks: the API is macro-based and trusts HWND/HLISTITEM lifetimes. Enumeration with `LPENUM *` requires callers to call `FastList_FindClose()` when stopping early. Notification handlers must return `TRUE` when they handle text or behavior requests, especially `FLN_GETITEMTEXT` and `FLN_BEGINDRAG`. Message IDs and notification codes live in fixed custom ranges and must stay coordinated with the implementation.

Test signals: compile and runtime tests for every macro message; notification structure layout compatibility; item add/remove and enumeration contracts including early close; selection mode behavior; custom sort callback and text callback invocation; drag-image creation; and style combinations such as `FLS_AUTOSORTHEADER` versus `FLS_NOSORTHEADER`.
