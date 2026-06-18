# sources/distributed-fs/openafs/src/WINNT/afs_setup_utils/animate_icon.cpp

Purpose: provides a small Windows control animation helper for setup progress UI.

Important APIs/types/functions: `AnimateIcon(HWND,int*)` lazy-loads stop and eight spinner icons with `TaLocale_LoadIcon()` and sets the static control icon. `AnimationHook()` is a subclass hook that advances frames on `WM_TIMER` and removes itself on `WM_DESTROY`. `StartAnimation()` adds the hook, starts a timer, and displays the first frame. `StopAnimation()` kills the timer, displays the stop icon, and removes the hook.

Control flow: progress dialogs call `StartAnimation()` with an icon control. Timer messages flow through the subclass hook, which calls `AnimateIcon()` and then chains to the previous hook or default window procedure.

State/persistence: static icon handles and `fLoaded` cache loaded resources for process lifetime; `AnimationHook()` uses a static frame index shared by all hooked controls. No disk persistence.

Dependencies/integration: depends on Windows messages/timers, `talocale` resource loading, the OpenAFS subclass helper, and spinner resource IDs in `resource.h`.

Risks/test signals: the frame counter is shared across controls, and `1000 / fps` can divide by zero only because the expression substitutes 8 when `fps` is zero. Tests should verify hook chaining, start/stop idempotence, destroy cleanup, localized icon loading, and timer cadence.
