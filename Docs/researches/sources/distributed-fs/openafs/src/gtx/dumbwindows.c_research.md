# sources/distributed-fs/openafs/src/gtx/dumbwindows.c

Purpose: implements the GTX "dumb terminal" backend advertised by `gtxdumbwin.h`, but it is mostly a placeholder implementation. It exports `dumb_gwinops` and `gator_dumb_gwinbops` so the generic window layer can select this backend through `gw_init`.

Important APIs and functions: `gator_dumbgwin_init` records `dumb_debug`; `gator_dumbgwin_create` currently returns `NULL`; cleanup, box, clear, destroy, display, draw-char, and draw-string return success without drawing; draw-line, draw-rectangle, invert, getchar, getdimensions, and wait log that they are no-ops and the input/dimension routines return `-1`.

Control flow and state: calls enter only through the generic `WOP_*` dispatch table. The only persistent module state is the global debug flag. No window instances are allocated, so no backend-private state exists.

Dependencies and integration: depends on `gtxdumbwin.h` and the generic `gwin` structures. `windows.c` can select it for `GATOR_WIN_DUMB`, but tests that try to create a dumb window will fail because creation returns `NULL`.

Risks: many operations report success despite doing nothing, which can hide unsupported backend selection. `gator_dumbgwin_destroy` debug output lacks a newline. Test signals should cover backend selection, `WOP_CREATE` failure behavior, and callers that assume successful no-op drawing means a usable terminal surface exists.
