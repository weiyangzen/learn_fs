# sources/distributed-fs/openafs/src/WINNT/afsapplib/test/wiztest.cpp

## Purpose
Provides a Win32 sample/test application for the afsapplib `WIZARD` class. It demonstrates wizard state setup, page transitions, button text/default control changes, optional state disabling, help/cancel handling, bitmap graphics, and a custom animated overlay callback.

## Important APIs and Control Flow
`WinMain` seeds randomness, starts a timer for animation, constructs a `WIZARD`, binds the outer template and pane/button IDs, sets 16/256-color graphics, registers `Wiz_DrawOverlay`, supplies three `WIZARD_STATE` entries, starts at step one, and shows the wizard modally. `WizStep_Common_DlgProc` handles help and cancel commands. Step procedures configure buttons during `WM_INITDIALOG` and change wizard state on `IDBACK`/`IDNEXT`. Step two handles `wcIS_STATE_DISABLED` so the first page can skip it.

The drawing section computes animated line endpoints inside the left graphic pane. `Wiz_ForceGraphicRedraw` invalidates and updates the left pane on each timer tick. `Wiz_DrawOverlay` chooses a color based on display depth, draws a bounding rectangle and rotating cross, moves the center point with bouncing velocity, and cleans up GDI pen objects.

## State, Dependencies, and Integration
Global state includes `g_pWiz`, `g_fSkipStep2`, wizard states, and static animation variables inside the drawing callback. Dependencies include `afsapplib.h`, Win32 dialogs/GDI/timers, math functions, and `resource.h`. It is a test/demo executable rather than production library code.

## Risks and Test Signals
The timer is created with a NULL HWND and never explicitly killed; the process exit normally cleans it up, but repeated embedding would need lifecycle care. `g_pWiz` is assumed valid during timer callbacks. The sample returns `FALSE` after common handling even when it handled a command, which may be intentional for this wizard framework but is worth checking. Tests are mostly interactive: resource loading, page navigation, skip-step behavior, cancel confirmation, help display, bitmap rendering, and overlay animation without GDI leaks.
