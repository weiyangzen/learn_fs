## sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_spinner.cpp

Purpose: Implements a reusable spinner/up-down scrollbar class that attaches to a buddy edit/listbox/combobox and synchronizes numeric or selected-index state.

Important APIs and functions: `RegisterSpinnerClass`, `CreateSpinner`, `fHasSpinner`, `SpinnerProc`, `SpinnerDialogProc`, `SpinnerBuddyProc`, `SpinnerSendCallback`, and handlers for all `SPM_*` messages. `Spinner_GetNewText` parses buddy content/selection; `Spinner_SetNewText` writes clamped text/selection and emits notifications.

Control flow: `CreateSpinner` allocates a `SpinnerInfo`, creates a vertical scrollbar-derived `Spinner` window next to the buddy or at a requested rect, and shows/enables it. Creation hooks the parent and buddy. Parent `WM_VSCROLL` increments/decrements position, allows `SPN_CHANGE_UP/DOWN` overrides, clamps to range, writes buddy text, and sends `SPN_UPDATE`. Buddy messages route keyboard arrows/page/home/end to the spinner, mark text dirty, reattach on move/size, and answer `SPM_*` messages.

State and persistence: Global `aSpinners` table guarded by `csSpinners` stores spinner HWND, buddy HWND, requested rect, min/max/base/signed/pos, callback flags, and optional format string. No persistence.

Dependencies and integration points: Uses Win32 scrollbar class metadata, `subclass.h`, app allocation, and public macros in `ctl_spinner.h`. Date and elapsed controls depend on it heavily.

Risks: Original scrollbar proc and class proc are stored in `LONG`, risky on 64-bit. The code enters `csSpinners` then calls `Spinner_FindSpinnerInfo`, which re-enters the same critical section. Signed numeric limits are represented in `DWORD` and cast to `signed long`. Buddy text parsing resets base to 10 for edits before detecting prefixes; custom format suppresses automatic base prefix behavior. Thread-safety is limited to table lookup/mutation, not all HWND lifetimes.

Test signals: Edit/listbox/combobox buddies; range and position get/set; signed decimal, hex, binary, octal-like input; custom format; keyboard and scrollbar changes; callback override with `SPVAL_UNCHANGED`; buddy move/resize; reattach/set-buddy; destroy cleanup.
