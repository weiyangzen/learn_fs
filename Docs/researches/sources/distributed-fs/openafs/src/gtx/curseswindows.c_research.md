# sources/distributed-fs/openafs/src/gtx/curseswindows.c

## Purpose
Implements the functional curses backend for the gtx window abstraction, mapping generic gwin operations to curses windows and terminal input.

## Important APIs, Types, And Functions
Exports `curses_gwinops`, `gator_curses_gwinbops`, `gator_cursesgwin_init`, `gator_cursesgwin_create`, `gator_cursesgwin_cleanup`, and operations for box, clear, destroy, display, draw line/rectangle/char/string, invert, getchar, wait, and getdimensions. Private data is `struct gator_cursesgwin` from `gtxcurseswin.h`.

## Control Flow
Initialization calls `initscr`, allocates private data for the global base window, sets default character geometry and box characters, fills `gator_basegwin`, enables raw mode, creates a frame, and clears the screen. Window creation allocates a generic `gwin`, allocates curses-private data, creates a curses `WINDOW` with `newwin`, initializes frame/private fields, and returns the new window. Display clears the curses window, renders the gtx frame, and refreshes. Character/string drawing maps coordinates directly, optionally enters standout mode, writes content, and exits standout. Wait spins on `LWP_WaitForKeystroke`; getchar reads from stdin; dimensions use `getmaxyx`.

## State And Persistence
State includes global `curses_debug`, the global `gator_basegwin`, curses terminal state, allocated `gwin`/private structs, curses `WINDOW` objects, and frames. Cleanup restores non-raw mode and calls `endwin`, but destroy only deletes the curses window and does not free the surrounding structs.

## Dependencies And Integration Points
Depends on curses/ncurses headers, LWP keyboard waiting, `gtxobjects`, `gtxframe`, and the generic `gtxwindows` operation table. It is the main terminal backend for gtx tools.

## Risks And Test Signals
Coordinate units are treated as curses rows/columns despite generic fields being described as pixels. Several drawing operations are no-ops, allocation cleanup is incomplete on destroy, and blocking input depends on LWP behavior. Tests should cover init/cleanup terminal restoration, create failure cleanup, box/clear/display/draw string highlighting, dimension reads, wait/getchar behavior, and repeated create/destroy leak checks.
