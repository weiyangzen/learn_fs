# sources/distributed-fs/openafs/src/WINNT/client_creds/afswiz.h

Purpose: declares the startup wizard entry point.

Important APIs/types: `void ShowStartupWizard(void)` is called from main application startup and tray activation paths when the service needs interactive startup/configuration help.

Control flow: no implementation. It is the public boundary to the multi-page wizard in `afswiz.cpp`.

State/persistence: none in header; wizard state is in `g.pWizard` and a file-static state block in the implementation.

Dependencies/integration: included through `afscreds.h`; consumers do not need to know wizard state IDs or dialog procedures.

Risks: single function hides substantial side effects including service start and drive mapping writes, so callers must only invoke it from UI-safe contexts.

Test signals: build references from `main.cpp` and `window.cpp`, and UI smoke test for startup wizard display.
