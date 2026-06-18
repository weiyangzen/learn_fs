# sources/distributed-fs/ceph-client/kernel/printk/braille.c

## Purpose

`braille.c` bridges printk console command-line parsing with the kernel braille-console driver. It recognizes braille prefixes in `console=` arguments, stores parsed braille options in `struct console_cmdline`, and registers or unregisters the braille backend when a matching console is enabled or removed.

## Important APIs

- `_braille_console_setup(char **str, char **brl_options)` parses `console=` fragments. `brl,` means braille with empty braille options and advances `*str` past the prefix. `brl=<opts>,<port>` stores the substring after `brl=` as braille options, replaces the separator comma with `NUL`, and advances `*str` to the serial or console port string.
- `_braille_register_console(struct console *console, struct console_cmdline *c)` checks `c->brl_options`, sets `CON_BRL`, and calls `braille_register_console(console, c->index, c->options, c->brl_options)`.
- `_braille_unregister_console(struct console *console)` calls `braille_unregister_console()` only for consoles flagged `CON_BRL`.

## Control flow

`printk.c:console_setup()` calls `_braille_console_setup()` before it decodes the tty name and options. Later, `try_enable_preferred_console()` calls `_braille_register_console()` after a candidate console matches a preferred command-line entry but before normal console setup. On unregister, `unregister_console_locked()` calls `_braille_unregister_console()` before disabling and removing the console from the console list.

## State and persistence behavior

The parser mutates the boot command-line string in place by writing a `NUL` over the comma after `brl=<opts>`. The persistent state is the `brl_options` pointer saved in `struct console_cmdline` and the `CON_BRL` flag set on the `struct console`. The file itself owns no global state.

## Dependencies and integration points

It depends on `linux/console.h` for `struct console` and `CON_BRL`, `console_cmdline.h` for the parsed console record, and the external braille console APIs declared through kernel console headers. The parser uses `str_has_prefix()` and `strchr()`. Normal printk consoles do not output to the braille console after registration: in `register_console()`, a successful braille registration or `CON_BRL` flag causes the normal console registration path to skip adding that console as a printk output console.

## Risks and test signals

The parser assumes mutable boot option storage, rejects `brl=` without a following comma, and leaves `brl_options` pointing into command-line storage. Useful tests include `console=brl,ttyS0`, `console=brl=<driver-options>,ttyS0`, malformed `console=brl=<driver-options>`, and unregister tests confirming `CON_BRL` consoles call braille unregister and skip normal printk output registration.
