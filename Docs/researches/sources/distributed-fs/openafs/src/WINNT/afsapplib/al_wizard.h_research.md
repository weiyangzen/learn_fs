## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_wizard.h

Purpose: Declares the exported `WIZARD` class, state descriptors, command enum, and button flag constants for the wizard framework.

Important APIs and types: `WIZARD_COMMAND` includes `wcSTATE_ENTER`, `wcSTATE_LEAVE`, and `wcIS_STATE_DISABLED`. `WIZARD_STATE` maps a numeric state to a dialog template, dialog proc, and init lparam. The class exposes configuration, state navigation, show/background, button, and state-command methods.

Control flow: Header-only declarations; runtime behavior is implemented in `al_wizard.cpp`. Dialog procs integrate through `WM_COMMAND` with `LOWORD == IDC_WIZARD` and `HIWORD` set to a `WIZARD_COMMAND`.

State and persistence: The class stores template IDs, bitmap handles, palette, raw state array pointer/count, current state, foreground/background HWNDs, background rendering state, and callback pointer. No persistence.

Dependencies and integration points: Includes Win32, property sheet, `TaLocale`, and subclass headers. Consumers must provide dialog templates containing left/right pane placeholders and navigation controls.

Risks: Raw pointers and GDI/HWND ownership are exposed through the class lifecycle. Copying a `WIZARD` object would be unsafe because no copy control is declared. Header uses `cchRESOURCE` without defining it locally, relying on included headers.

Test signals: Compile client code, verify expected resource IDs/control IDs, state dialog command handling, and object destruction with active/inactive windows.
