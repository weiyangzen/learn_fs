# sources/distributed-fs/ceph-client/tools/perf/ui/keysyms.c

## Purpose

`keysyms.c` converts key codes into human-readable names for UI warnings and help.

## Important APIs, Types, and Functions

It implements `const char *key_name(int key, char *bf, size_t size)`. Printable keys are returned as one-character strings; control keys and SLang key constants are mapped to names such as ENTER, ESC, BACKSPACE, UP, DOWN, F1, TAB, and TIMER; unknown keys are formatted numerically.

## Control Flow and State

The function is stateless and writes into caller-provided storage for non-static names.

## Dependencies and Integration Points

It depends on `keysyms.h`, Linux ctype/kernel helpers, and SLang constants through `libslang.h`. Browser code uses it for unhandled-hotkey messages.

## Risks and Test Signals

Risks are missing key mappings and buffer truncation. Tests should cover printable, control, navigation, function, timer, resize, and unknown keys.
