## sources/distributed-fs/openafs/src/WINNT/afsapplib/checklist.h

Purpose: Declares the checklist control registration function, class name, custom messages, notification alias, and helper macros.

Important APIs and definitions: `RegisterCheckListClass`, `WC_CHECKLIST`, `LB_GETCHECK`, `LB_SETCHECK`, `LBN_CLICKED`, `LB_GetCheck`, and `LB_SetCheck`.

Control flow: Header-only macro dispatch sends custom messages to checklist HWNDs. Runtime handling is in `checklist.cpp`.

State and persistence: None in the header. Checked state is implemented as listbox item data by the source file.

Dependencies and integration points: Consumers create controls with class `OpenAFS_CheckList`, call `RegisterCheckListClass`, and use standard listbox APIs plus these macros.

Risks: Custom `WM_USER+300/301` messages assume no conflict with other subclassed listbox behavior. `LBN_CLICKED` is aliased to `BN_CLICKED`, which works numerically but may confuse readers/tools.

Test signals: Compile inclusion in C++ UI modules, class registration before dialog creation, get/set macros, and parent notification handling.
