# sources/distributed-fs/ceph-client/scripts/kconfig/nconf.h

## Purpose
`nconf.h` is the shared header for the ncurses Kconfig frontend. It includes curses dependencies, declares UI attribute globals, defines small `max`/`min` helper macros and function-key constants, and publishes the dialog/window helper API implemented by `nconf.gui.c`.

## Important APIs, Types, and Functions
The `function_key` enum maps `F_HELP` through `F_EXIT` to F1-F9 behavior. `extra_key_cb_fn` defines callbacks used by scroll windows for search-result jump handling. Extern attributes cover all color/style roles in the main menu, scroll windows, dialogs, inputs, and function key bar.

Published functions include `set_colors()`, `print_in_middle()`, line-count/line-length utilities, `fill_window()`, `btn_dialog()`, `dialog_inputbox()`, `refresh_all_windows()`, `show_scroll_win_ext()`, and `show_scroll_win()`.

## Control Flow
The header has no runtime control flow. Its macros evaluate operands once using GNU statement expressions and `typeof`, making it tied to GNU C-compatible host compilers.

## State and Persistence
It declares process-global style state, owned and initialized by `nconf.gui.c`, then consumed by `nconf.c`.

## Dependencies and Integration Points
It includes `<ncurses.h>`, `<menu.h>`, `<panel.h>`, and `<form.h>`, making frontend compilation dependent on full ncurses development headers. It also pulls standard headers used by the implementation.

## Risks and Edge Cases
The `max` and `min` macro names are broad and can conflict if included with other headers that define them. The exported globals make style state mutable from any translation unit. GNU-only macro syntax reduces portability but matches kernel host-tool expectations.

## Test Signals
Successful `nconf` build against ncurses and runtime exercise of dialogs, scroll windows, and function-key handling validate this header contract.
