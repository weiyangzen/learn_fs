# sources/distributed-fs/ceph-client/tools/perf/ui/browser.h

Purpose: Declares the generic perf TUI browser abstraction and helper API.

Important APIs/types/functions: `struct ui_browser` carries navigation state, geometry, callbacks (`refresh_dimensions`, `refresh`, `write`, `seek`, `filter`), content metadata, and UI strings. The header declares color constants, drawing helpers, modal helpers, event loop functions, and ready-made backends for argv, rb-tree, and list-head data.

Control flow: The header has no runtime control flow, but its callback contract drives all browser implementations: callers provide data traversal and row rendering, while `browser.c` owns common navigation and display.

State and persistence: Browser instances store transient TUI state only. Titles and helplines are allocated/freed by show/hide.

Dependencies and integration points: Included by perf TUI modules such as annotation, header, hists, and data-type browsers. It depends on Linux integer types and standard varargs/types.

Risks: Callback signature misuse can corrupt browser state. `u16` dimensions and `u32 nr_entries` constrain maximum visible metadata but are adequate for terminal UI.

Test signals: Compile all TUI users, instantiate each backend type, and run navigation/resizing paths that use the declared helpers.
