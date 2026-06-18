# sources/distributed-fs/openafs/src/WINNT/afsapplib/dialog.h

Purpose: declares the public utility API implemented by `dialog.cpp` for OpenAFS Win32 dialogs and common controls.

Important APIs/types/functions: `PROPSHEET` extends `PROPSHEETHEADER` with tab metadata and caller `lpUser`. `VIEWINFO` captures view style, available/shown columns, column resource IDs, widths/justification flags, and sort column/reverse bit. Constants include `IDINIT`, `IDAPPLY`, `IDHELP`, property-sheet lifecycle messages `WM_INITDIALOG_SHEET` and `WM_DESTROY_SHEET`, `nCOLUMNS_MAX`, `COLUMN_*` flags, and `INDEX_SORT`. The header declares `PropSheet_*`, `FL_*`, `LV_*`, `CB_*`, `LB_*`, `TV_*`, `Browse_*`, and miscellaneous HWND/cursor/menu helpers.

Control flow: callers include this header to build property sheets, preserve and restore view state, batch control updates, add rows/items, retrieve selected item data, and use common dialog helpers. `StartChange()`/`EndChange()` pairs form the expected update transaction pattern for FastList, ListView, ComboBox, ListBox, and TreeView controls.

State and persistence behavior: `VIEWINFO` is the only explicit persistence carrier in the interface; callers can store it to restore view mode and columns later. `PROPSHEET` is heap-allocated by `PropSheet_Create()` and owned by the property-sheet lifecycle until `PropSheet_Free()`.

Dependencies and integration points: includes `commctrl.h`, `commdlg.h`, and `WINNT/fastlist.h`, so it exposes both native common-control and custom FastList types. It is a central include for OpenAFS Windows UI code that needs resource-string based columns, property sheets, list wrappers, browse dialogs, and tab helpers.

Risks: the API is macro- and HWND-heavy, so type safety is limited. `VIEWINFO` has fixed `nCOLUMNS_MAX` arrays and requires callers to keep `nColsAvail`, `nColsShown`, and `aColumns[]` coherent. The `Set2State`/`Set3State`, `CheckMenu`, and `EnableMenu` macros directly send Win32 messages without validation. Function declarations mix `LPARAM` cookies, resource IDs, string pointers, and varargs, making call-site correctness important.

Test signals: compile coverage for C++ default arguments and varargs declarations; property-sheet callbacks receiving `IDINIT`/`IDAPPLY`/`IDHELP`; column view round trips through `VIEWINFO`; and common-control selection helpers across empty, single, and duplicate-data controls.
