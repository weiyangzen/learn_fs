# sources/distributed-fs/openafs/src/gtx/gtxX11win.h

Purpose: declares the GTX X11 backend contract. It gives the generic window layer a backend type value, creation parameters, a base operation table, and the full set of `gwinops`-compatible functions.

Important APIs and types: `GATOR_WIN_X11`, `struct gator_X11gwin_params`, `gator_X11_gwinbops`, `gator_X11gwin_init/create/cleanup`, and drawing/input routines for box, clear, destroy, display, drawline, drawrectangle, drawchar, drawstring, invert, getchar, getdimensions, and wait.

Control flow and state: this header itself stores no state. Runtime state is owned by the X11 backend implementation and generic `struct gwin`. The `gwin_params` embedded in creation parameters carries common type, geometry, and parent-window inputs; `box_vertchar` and `box_horizchar` customize box rendering.

Dependencies and integration: includes `gtxwindows.h`; `windows.c` selects this backend for `GATOR_WIN_X11`. Object and frame code use it only through generic `WOP_*` macros after initialization.

Risks: the interface mirrors curses/dumb, so callers may assume behavioral parity across backends. Test signals should compile the header with the implementation, verify the `gwinops` table signatures stay aligned, and run backend-specific draw/input tests when X11 support is enabled.
