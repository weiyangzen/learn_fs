# sources/distributed-fs/openafs/src/gtx/gtxwindows.h

Purpose: defines the generic GTX window abstraction and dispatch macros independent of curses, dumb-terminal, or X11 backends.

Important APIs and types: `struct gwin`, linked-list and parameter structs for initialization, creation, drawing lines/rectangles/chars/strings, inversion and size lookup, `struct gwinops`, `WOP_*` macros, `struct gwinbaseops`, global `gwinbops`, global `gator_basegwin`, `gw_init`, and `gtx_Init`.

Control flow and state: `gw_init` selects backend base ops. Created windows carry backend-private data in `w_data`, draw/input functions in `w_op`, parent pointers, and optional attached frame state. `WOP_CREATE` and `WOP_CLEANUP` dispatch through `gwinbops`; window-level operations dispatch through `w_op`.

Dependencies and integration: included by all backend headers, object headers, frames, input, and tests.

Risks: macros do no NULL checking and assume fully initialized operation tables. `w_data` is typed as `int *`, forcing casts. Test signals should cover backend initialization, base window invariants, subwindow creation, dimensions, display dispatch, and cleanup for each enabled backend.
