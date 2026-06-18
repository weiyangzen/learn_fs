# sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/inputbox.c

## Purpose

`lxdialog/inputbox.c` implements the ncurses input dialog used by `mconf` for string, int, hex, load-file, save-file, and search-entry prompts.

## Important APIs, Types, and Functions

The exported function is `dialog_inputbox()`, and the global output buffer is `dialog_input_result[MAX_LEN + 1]`. `print_buttons()` renders Ok and Help controls.

## Control Flow

The dialog copies the initial value into `dialog_input_result`, draws the prompt, input field, and buttons, then processes keyboard input. When the input field is active, printable characters insert at the cursor, backspace deletes, left/right move with horizontal scrolling, and max length is enforced with `flash()`. Tab and arrow keys cycle focus between input, Ok, and Help. `o`/Enter/space return success, `h` returns Help, resize redraws, and ESC exits through `on_key_esc()`.

## State and Persistence Behavior

Input persists only in the global `dialog_input_result` buffer until the next input dialog. Cursor position, visible horizontal offset, and selected button are local state. There is no file persistence.

## Dependencies and Integration Points

It depends on ncurses drawing helpers and theme attributes from `util.c`. `mconf.c` reads `dialog_input_result` after return and validates through `sym_set_string_value()`, `conf_read()`, `conf_write()`, or search APIs.

## Risks and Edge Cases

Input is byte-oriented and limited to `MAX_LEN`, so multibyte terminal input may not behave as a user expects. The code manually redraws the field and must keep `pos`, `len`, `input_x`, and `show_x` consistent. Small terminals return `-ERRDISPLAYTOOSMALL`.

## Test Signals

Test insertion/deletion in middle of text, long input horizontal scrolling, empty input, Help, load/save filenames, invalid symbol values, resize, ESC, and terminal small-size returns.
