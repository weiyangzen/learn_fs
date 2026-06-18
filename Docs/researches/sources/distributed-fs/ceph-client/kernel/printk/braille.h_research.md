# sources/distributed-fs/ceph-client/kernel/printk/braille.h

## Purpose

`braille.h` provides the internal printk-facing braille console API. It hides `CONFIG_A11Y_BRAILLE_CONSOLE` behind no-op inline stubs so the main console registration and command-line parsing code can call braille helpers unconditionally.

## Important APIs

- `braille_set_options(struct console_cmdline *c, char *brl_options)` stores parsed braille options in the command-line console entry when braille support is enabled.
- `_braille_console_setup(char **str, char **brl_options)` parses braille syntax from `console=` options.
- `_braille_register_console(struct console *console, struct console_cmdline *c)` registers the braille backend and marks the console `CON_BRL`.
- `_braille_unregister_console(struct console *console)` unregisters a braille console during console teardown.

When `CONFIG_A11Y_BRAILLE_CONSOLE` is disabled, all helpers compile to no-ops returning success.

## Control flow and state

`printk.c` uses this header in command-line parsing and console registration. The enabled build stores braille options in `struct console_cmdline`; the disabled build drops them and lets the normal console parsing path proceed without braille-specific state. The header itself owns no state. It controls whether `struct console_cmdline::brl_options` is populated, and that field is also gated by the same Kconfig symbol.

## Dependencies and integration points

The header depends on `struct console_cmdline` and `struct console` being visible to users. It must remain synchronized with `console_cmdline.h`; otherwise inline access to `c->brl_options` could break disabled or enabled builds. The main integration pattern is compile-time polymorphism, allowing `printk.c` to call the helpers unconditionally while the compiler removes braille behavior from non-accessibility builds.

## Risks and test signals

Any future added braille state must be gated consistently in both `braille.h` and `console_cmdline.h`. The stub functions return success, so callers must not rely on a nonzero result to detect that braille support is absent. Build tests should cover `CONFIG_A11Y_BRAILLE_CONSOLE=y` and `n`, with runtime checks that console options either register braille behavior or are harmless.
