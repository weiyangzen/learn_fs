# sources/distributed-fs/openafs/src/gtx/windows.c

Purpose: implements generic GTX window package initialization and backend selection.

Important functions and state: global `struct gwinbaseops gwinbops`, global `struct gwin gator_basegwin`, and `gw_init`. `gw_init` reads `gwin_initparams`, selects dumb, curses, or X11 backend, copies the backend base ops table, calls backend initialization, and returns errors for invalid package selection.

Control flow and state: initialization is a switch over `params->i_type`. It does not fill `gator_basegwin` directly in this file; backend initialization is responsible for base-window setup. `gwin_debug` is local and controls diagnostic logging.

Dependencies and integration: includes generic window header and all three backend headers. `gator_objects_init`, `screen_test`, and `gtx_Init` call `gw_init`; object and frame code depend on `gwinbops` and `gator_basegwin` after it succeeds.

Risks: no global initialized guard; reinitializing with another backend overwrites `gwinbops`. Invalid or partially initialized backends can leave globals inconsistent. Test signals should cover each backend type, invalid type errors, reinitialization behavior, and whether backend init correctly populates `gator_basegwin`.
