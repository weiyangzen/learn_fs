# sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/dialog.h

## Purpose

`lxdialog/dialog.h` is the common declaration header for the ncurses dialog toolkit used by `mconf`. It defines shared key constants, minimum sizes, color/theme structures, global dialog state, item-list structures, and widget function prototypes.

## Important APIs, Types, and Functions

Important constants include `KEY_ESC`, `TAB`, `MAX_LEN`, `BUF_SIZE`, `ERRDISPLAYTOOSMALL`, and per-widget minimum dimensions. Key types are `struct dialog_color`, `struct subtitle_list`, `struct dialog_info`, `struct dialog_item`, and `struct dialog_list`. It declares global `dlg`, `dialog_input_result`, `saved_x`, `saved_y`, item-list APIs, drawing helpers, generic key handlers, lifecycle functions, and dialog functions such as `dialog_yesno()`, `dialog_textbox()`, `dialog_menu()`, `dialog_checklist()`, and `dialog_inputbox()`.

## Control Flow

No runtime flow is implemented. The header establishes the call contract between `mconf.c` and lxdialog implementation files.

## State and Persistence Behavior

It exposes process-global UI state: theme colors, backtitle/subtitles, input buffer, saved cursor coordinates, and the current linked list of menu items. There is no file persistence.

## Dependencies and Integration Points

It includes system headers and `<ncurses.h>`, with ACS fallback macros for terminals or curses variants missing line-drawing constants. `mconf.c` includes it directly and relies on the return-code convention of each dialog.

## Risks and Edge Cases

The shared item list and input buffer are global and not reentrant. `dialog_msgbox()` is prototyped here but not implemented in the files in this subset, so either another object provides it or the prototype is legacy. Static buffer sizes cap input and displayed line lengths.

## Test Signals

Compile/link `mconf`, verify no unresolved dialog symbols, run all dialog types, and test terminal variants with missing ACS macros, small sizes, resize events, ESC handling, and long strings.
