<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/graphics.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/graphics.cpp

Purpose: Draws wizard progress graphics: per-step state icons in the final configuration page and the custom left-pane wizard progress bar/arrow/text.

Important APIs/functions: `PaintStepGraphic` paints a blue/green dot, checkmark, or red X based on `STEP_STATE`. `PaintPageGraphic` renders the left-pane current-step label, progress bar, arrow, and current page description. Static helpers erase rectangles and draw each icon.

Control flow: `config_server_page.cpp` subclasses static controls to call `PaintStepGraphic` during `WM_PAINT`. `afscfg.cpp` registers `PaintPageGraphic` as the wizard graphic callback, so it runs whenever the wizard left pane repaints.

State and persistence: Uses static GDI pens/fonts in `PaintPageGraphic` for process lifetime. No persistent state.

Dependencies and integration points: Depends on Win32 GDI, `STEP_STATE`, `g_pWiz`, `g_nNumStates`, `g_StateDesc`, resource strings, and app-library font creation.

Risks: Static GDI objects are never destroyed. Drawing assumes `g_pWiz` and state indexes are valid. Color constants are raw BGR `COLORREF` values and comments may be confusing. Manual pixel drawing is brittle under high DPI/themes.

Test signals: Visual-test all step states, every wizard page index, resize/repaint behavior, high-DPI display, and repeated wizard open/close for GDI object growth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/graphics.cpp -->
