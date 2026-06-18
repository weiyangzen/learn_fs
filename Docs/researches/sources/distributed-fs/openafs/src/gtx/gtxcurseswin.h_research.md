# sources/distributed-fs/openafs/src/gtx/gtxcurseswin.h

Purpose: declares the GTX curses backend. It adapts platform curses headers, provides portability glue for `getmaxyx`, defines curses-private window data, and exports the `gwinops` functions used by the generic GTX window interface.

Important APIs and types: `GATOR_WIN_CURSES`, `struct gator_cursesgwin` with `WINDOW *wp`, character dimensions, and box characters; `struct gator_cursesgwin_params`; `gator_curses_gwinbops`; and init/create/cleanup/draw/input functions.

Control flow and state: the header defines shape only. Curses state is held in backend-private `WINDOW` objects and attached to `gwin.w_data`. Creation parameters include common geometry through `gwin_createparams` and curses-specific character metrics.

Dependencies and integration: includes `gtxwindows.h` and conditionally includes `ncurses.h`, `ncurses/ncurses.h`, or `curses.h`. `windows.c`, `gtx_Init`, `screen_test.c`, and `object_test.c` rely on this backend as the practical interactive implementation.

Risks: portability macros use private curses fields `_maxy`/`_maxx` as a fallback. Code outside the header, including tests, uses global `LINES` and `COLS`, so curses initialization order matters. Test signals should include configure variants with different curses header availability and runtime creation/dimension/readiness checks.
