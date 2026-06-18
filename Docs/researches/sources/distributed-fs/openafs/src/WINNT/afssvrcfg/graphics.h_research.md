<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/graphics.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/graphics.h

Purpose: Declares drawing hooks for wizard and configuration progress UI.

Important APIs/functions: `PaintStepGraphic(HWND, STEP_STATE)` and `PaintPageGraphic(LPWIZARD, HDC, LPRECT, HPALETTE)`.

Control flow: No implementation logic; functions are passed to subclass/callback mechanisms.

State and persistence: None in the header.

Dependencies and integration points: Includes `config.h` and requires wizard/app-library Win32 types.

Risks: Callers must provide valid paint contexts and a synchronized wizard state.

Test signals: Compile integration with wizard callback signatures and static-control subclass calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/graphics.h -->
