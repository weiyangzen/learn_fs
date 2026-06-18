# sources/distributed-fs/ceph-client/scripts/kconfig/lxdialog/yesno.c

## Purpose

`lxdialog/yesno.c` implements the two-button confirmation dialog used by `mconf`, most importantly for the exit/save prompt.

## Important APIs, Types, and Functions

The exported function is `dialog_yesno()`. Internal `print_buttons()` renders Yes and No through the shared `print_button()` helper.

## Control Flow

`dialog_yesno()` validates terminal size, centers and draws the dialog, prints the prompt and buttons, and loops for key input. `y` returns 0, `n` returns 1, Tab/left/right toggles the selected button, Enter/space returns the selected button, resize redraws, and ESC exits through `on_key_esc()`.

## State and Persistence Behavior

All state is local to the call except shared theme/backdrop state from `dlg`. It has no persistence.

## Dependencies and Integration Points

It uses ncurses and drawing/key helpers from `util.c`. `mconf.c::handle_exit()` interprets return 0 as save, 1 as discard, and `KEY_ESC` as continue configuration.

## Risks and Edge Cases

Return-code meaning is caller convention, so changes must be coordinated with `mconf`. Small terminal sizes return `-ERRDISPLAYTOOSMALL`, which callers should treat intentionally. Prompt wrapping depends on the fixed dialog dimensions passed by the caller.

## Test Signals

Test y/n shortcuts, selected-button return, ESC/double-ESC, resize, small terminal return, and integration with menuconfig exit flow.
