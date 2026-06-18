# sources/distributed-fs/openafs/src/gtx/frame.c

Purpose: implements GTX frames, which bind a `gwin` to a keymap, display list, menus, prompt/default input state, and a bottom message line. Frames are the interactive controller between the window backend, key processing, and object rendering.

Important APIs and functions: `gtxframe_Create/Delete`, `gtxframe_SetFrame/GetFrame`, menu operations, display-list operations, `gtxframe_Display`, `gtxframe_DisplayString`, `gtxframe_ClearMessageLine`, `gtxframe_AskForString`, and `gtxframe_ExitCmd`. Internal command handlers implement recursive input editing for backspace, Ctrl-U, self-insert, accept, and abort.

Control flow and state: `gtxframe_AskForString` saves the caller keymap, installs a singleton `recursiveMap`, fills `promptLine` and `defaultLine`, then calls `gtx_InputServer` until accept/abort flags are set. `gtxframe_Display` draws menu text, dispatches each listed `onode` through `OOP_DISPLAY`, then draws prompt/message text on the last line.

Dependencies and integration: uses `gtxkeymap`, `gtxinput`, `gtxobjects`, generic `WOP_*` drawing, and curses cleanup in `gtxframe_ExitCmd`.

Risks: fixed 1024-byte buffers are used for menu and prompt composition with unbounded `strcat`/`strcpy`; `gtxframe_ExitCmd` directly calls curses cleanup even when another backend was selected; `gtxframe_Delete` does not clear menus/display-list entries or prompt/default strings. Test signals should exercise recursive input, long menu labels, frame switching, duplicate display-list insertion, abort paths, and non-curses backend exit.
