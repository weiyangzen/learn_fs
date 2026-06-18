# sources/distributed-fs/openafs/src/gtx/gtxdumbwin.h

Purpose: declares the "dumb terminal" GTX backend interface. It exposes the same generic operation surface as curses and X11 while assigning the backend type `GATOR_WIN_DUMB`.

Important APIs and types: `struct gator_dumbgwin_params` embeds common `gwin_createparams` and box characters. Exported functions include package initialization, window creation/cleanup, all drawing operations, input polling, dimension lookup, and wait.

Control flow and state: no state is declared in the header. Runtime users call `gw_init` with `GATOR_WIN_DUMB`, then interact through `WOP_*` macros backed by `gator_dumb_gwinbops` and the dumb backend `gwinops` table.

Dependencies and integration: includes `gtxwindows.h`; used by `windows.c`, `screen_test.c`, `object_test.c`, and `textobject.c` as one of the selectable backends. The implementation currently does not create usable windows.

Risks: the header advertises full backend capability but `dumbwindows.c` is largely nonfunctional. Callers selecting this backend need explicit handling for failed creation and unsupported input/dimension operations. Test signals should validate advertised signatures and confirm callers degrade cleanly when `gator_dumbgwin_create` returns `NULL`.
