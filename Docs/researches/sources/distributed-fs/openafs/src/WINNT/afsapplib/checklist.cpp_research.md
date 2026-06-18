## sources/distributed-fs/openafs/src/WINNT/afsapplib/checklist.cpp

Purpose: Implements `OpenAFS_CheckList`, an owner-drawn listbox-derived control with a checkbox glyph per item and click/double-click toggling.

Important APIs and functions: `RegisterCheckListClass` clones base `LISTBOX` class metadata and registers `WC_CHECKLIST`; `IsCheckList` validates HWND class. `CheckListProc` handles mouse, enable, create/destroy, and custom `LB_GETCHECK`/`LB_SETCHECK`. Parent hook `CheckList_DialogProc` handles measure/draw/color messages. Draw helpers render checkbox frame/checkmark and text. Input helpers manage hit-test state and multi-select toggling.

Control flow: On create, the control hooks its parent and initializes an internal hit item in `GWLP_USERDATA`. Mouse down over a checkbox captures the mouse and records hit item; mouse up toggles selected items if released over the checkbox; double-click toggles current item. Item checked state is stored in listbox item data.

State and persistence: Global `procListbox` stores original class proc. Per-control hit state is `GWLP_USERDATA`; per-item check state is `LB_SETITEMDATA`. Static selection buffer in `CheckList_OnSetCheck_Selected` is reused. No persistence.

Dependencies and integration points: Requires Win32 listbox owner-draw messages, `TaLocale`, `subclass.h`, and public macros in `checklist.h`. Parent receives `LBN_CLICKED` after toggles.

Risks: Parent hook removal on one checklist destroy can affect siblings because it removes the same hook from the parent. `WM_CTLCOLORLISTBOX` creates brushes without deleting old ones when color changes. Text buffer is fixed at 256 characters. Storing original proc in `LONG` is pointer-width risky on 64-bit.

Test signals: Single and multi-select toggle behavior, disabled rendering, keyboard/listbox behavior pass-through, multiple checklist controls in one dialog, long text drawing, owner-draw measure, and 64-bit build warnings.
