## sources/distributed-fs/openafs/src/WINNT/afsapplib/ctl_spinner.h

Purpose: Declares the spinner custom control API, notification codes, helper macros, and creation functions.

Important APIs and definitions: `RegisterSpinnerClass`, `CreateSpinner`, `fHasSpinner`, messages `SPM_GETRANGE` through `SPM_SETBUDDY`, notifications `SPN_CHANGE_UP`, `SPN_CHANGE_DOWN`, `SPN_CHANGE`, `SPN_UPDATE`, sentinel `SPVAL_UNCHANGED`, and helper macros `SP_GetRange`, `SP_SetRange`, `SP_GetPos`, `SP_SetPos`, `SP_GetBase`, `SP_SetBase`, `SP_GetSpinner`, `SP_SetRect`, `SP_SetFormat`, and `SP_SetBuddy`.

Control flow: All control messages are sent to the buddy control, not the spinner HWND. Notifications return through parent `WM_COMMAND` with `LOWORD` equal to the buddy control ID and `HIWORD` equal to an `SPN_*` code.

State and persistence: None in the header; runtime state is in `ctl_spinner.cpp`.

Dependencies and integration points: Used directly by dialogs and by composite controls such as Date and Elapsed. Consumers must understand that `SP_GetSpinner` returns the generated spinner HWND while most APIs target the buddy.

Risks: `SP_GetPos` returns the `SendMessage` result cast as `DWORD` through macro context, but the underlying handler returns `BOOL`, which is type-confusing even if values fit in `LRESULT`. Multi-argument macros do not enforce pointer types.

Test signals: Compile all helper macros, verify message target convention, callback payload semantics, and interoperation with all supported buddy classes.
