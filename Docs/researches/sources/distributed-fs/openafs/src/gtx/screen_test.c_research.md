# sources/distributed-fs/openafs/src/gtx/screen_test.c

Purpose: manual test driver for generic GTX window operations and backend selection.

Important functions: `test_this_package` initializes a selected backend, writes screen-size strings, draws a diagonal of characters, boxes the base window, creates a subwindow, draws in it, displays, sleeps, and cleans up. `screen_testInit` parses `-package` and `-debug`; `main` registers the syntax and dispatches.

Control flow and state: the test starts with `gw_init`, uses global `gator_basegwin`, curses globals `LINES` and `COLS`, and a backend-specific creation parameter union by declaring all backend parameter types but filling the curses-shaped one for `WOP_CREATE`.

Dependencies and integration: includes generic, curses, dumb, and X11 window headers plus `afs/cmd.h`.

Risks: because it always fills `gator_cursesgwin_params` for subwindow creation, non-curses backends may receive mismatched parameters. It is visual and sleep-based, with no automated pass/fail. The dumb backend create path returns `NULL`. Test signals should include backend init failure paths, base draw operations, subwindow creation, display/cleanup, and portability around curses global dimensions.
