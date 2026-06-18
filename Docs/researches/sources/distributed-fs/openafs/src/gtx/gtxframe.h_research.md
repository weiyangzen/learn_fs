# sources/distributed-fs/openafs/src/gtx/gtxframe.h

Purpose: defines the public frame structure and frame manipulation API for GTX interactive views. A frame holds a keymap, display object list, menu list, message/prompt strings, an owning window pointer, and state flags.

Important APIs and types: `struct gtxframe_dlist`, `struct gtxframe_menu`, `struct gtx_frame`, flags `GTXFRAME_NEWDISPLAY`, `GTXFRAME_RECURSIVEEND`, and `GTXFRAME_RECURSIVEERR`, plus APIs for frame/window association, menus, prompting, message display, object list operations, display, deletion, and the exit command.

Control flow and state: the header exposes state directly instead of hiding it behind accessors. Input code mutates `flags` and keymap state, frame display traverses `menus` and `display`, and prompt handling uses `promptLine`/`defaultLine`.

Dependencies and integration: relies on forward-visible `struct gwin`, `struct onode`, and keymap types from companion headers. It is included by `frame.c`, input handling, tests, and curses backend code.

Risks: direct struct access makes ABI and invariants fragile. `display` stores `char *data` but actually holds `struct onode *`, which is type-unsafe. Test signals should cover header consumers, frame lifecycle cleanup, and mutation of flags during nested input.
