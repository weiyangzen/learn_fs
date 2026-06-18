## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_wizard.cpp

Purpose: Implements a reusable wizard framework with a template dialog, switchable right-hand state panes, optional left graphic rendering, and optional full-screen/background wash window.

Important APIs and functions: Public methods configure template/control IDs, graphics, state table, graphic callback, current state, background, buttons, and default control. Internal logic includes `Refresh`, `GetRightHandWindow`, `GeneratePalette`, `FindState`, `SendStateCommand`, template/background dialog procedures, left-pane paint hook, and background paint helpers.

Control flow: `Show(TRUE)` creates the template modeless dialog and enters a message loop until the wizard closes. `SetState` sends leave/enter commands and skips disabled states unless forced. `Refresh(REFRESH_RIGHT_PANE)` creates the state's modeless child dialog, sizes it over the right-pane placeholder, hides the placeholder, and destroys the old pane. Left-pane painting selects the 256-color bitmap when display depth allows, otherwise the 16-color bitmap, centers/crops/fills, optionally double-buffers, and invokes a custom draw callback. Background windows render a blue wash bitmap and route cancellation back to the wizard/current state.

State and persistence: Object fields own HWNDs, bitmaps, palette, current state, state array pointer, background text/font/buffer, and callback pointers. No durable persistence.

Dependencies and integration points: Uses `TaLocale_LoadImage`, `GetString`, subclass hooks, Win32 GDI, dialogs, and property/window APIs. State pane dialog procs receive `IDC_WIZARD` command notifications for `wcSTATE_ENTER`, `wcSTATE_LEAVE`, and `wcIS_STATE_DISABLED`.

Risks: The wizard owns GDI objects and window lifetime; misuse can double-destroy or leave callers with invalid pane HWNDs. `SetStates` stores a raw pointer, so caller must keep the array alive. The modal loop inside `Show` can conflict with outer pumps. Palette/bitmap handling targets legacy 8-bit displays and uses many GDI objects. Disabled-state skipping briefly sends enter/leave to candidate states.

Test signals: Show/hide lifecycle, state transitions forward/back/disabled/forced, pane replacement, left graphic with 16/256 assets, custom graphic callback, background resize/paint/close, button enable/text/default control, and GDI leak checks.
