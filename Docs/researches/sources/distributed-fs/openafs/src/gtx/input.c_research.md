# sources/distributed-fs/openafs/src/gtx/input.c

Purpose: implements the GTX input loop and the high-level `gtx_Init` convenience initializer.

Important APIs: `gtx_InputServer` draws the active window, waits for backend input, reads one character, clears stale message state, dispatches through the current frame keymap, handles recursive-edit end flags, and redisplays. `gtx_Init` initializes objects/windows with a curses default and returns `&gator_basegwin`.

Control flow and state: `gtx_InputServer` repeatedly reads `awin->w_frame`; commands may change the frame, so it reloads after key processing. `GTXFRAME_NEWDISPLAY`, `GTXFRAME_RECURSIVEEND`, and `GTXFRAME_RECURSIVEERR` control message clearing and recursive prompt returns.

Dependencies and integration: uses pthreads, `gtxobjects`, `gtxwindows`, curses backend, keymaps, frames, `afs/stds.h`, and `opr_Verify`.

Risks: `gtx_Init` ignores its `atype` argument and hardcodes `GATOR_WIN_CURSES`. If `astartInput` is true, it starts `gtx_InputServer` with `NULL`, which would dereference a null window. Wait failures call `exit(1)`. Test signals should cover synchronous input with a valid frame, recursive prompt return, and either disable or repair threaded startup before testing it.
