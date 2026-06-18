# sources/distributed-fs/ceph-client/tools/perf/ui/tui/util.c

## Purpose

`tui/util.c` implements common terminal dialogs: popup menus, input windows, info/help/question windows, yes/no prompts, and TUI error/warning callbacks.

## Important APIs, Types, and Functions

Public APIs include `ui__popup_menu`, `ui_browser__input_window`, `__ui__info_window`, `ui__info_window`, `ui__question_window`, `ui__help_window`, and `ui__dialog_yesno`. It also exports `perf_tui_eops` with TUI error/warning functions.

## Control Flow and State

Popup menus use a temporary `ui_browser` over argv strings. Input windows draw a boxed prompt, edit a buffer with printable characters/backspace/escape/enter, and preserve terminal state under `ui__lock`. Info/question windows size text, draw boxes, and wait for a key through `ui__getch`. Error/warning callbacks format a message and show it as a question window.

## Dependencies and Integration Points

It depends on SLang, browser primitives, keysyms, helpline, generic UI utilities, and `ui__lock`. Histogram, script, map, and setup code use these dialogs.

## Risks and Test Signals

Risks include buffer bounds in text input, long-line clipping, terminal resize during modal windows, and `vasprintf` failure fallback. Tests should cover popup hotkey return, text editing, ESC/ENTER behavior, long prompts, yes/no dialogs, and warning display.
