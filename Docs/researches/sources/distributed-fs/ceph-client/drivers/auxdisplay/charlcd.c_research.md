# sources/distributed-fs/ceph-client/drivers/auxdisplay/charlcd.c

## Purpose
Provides the common character LCD core behind `/dev/lcd`. It translates writes and escape sequences into `struct charlcd_ops` callbacks supplied by hardware drivers, manages cursor position, backlight flash behavior, boot/shutdown messages, and single-open misc-device access.

## Important APIs, Types, And Functions
- Exported lifecycle/API: `charlcd_alloc()`, `charlcd_free()`, `charlcd_register()`, `charlcd_unregister()`, `charlcd_backlight()`, and `charlcd_poke()`.
- `struct charlcd_priv` wraps public `struct charlcd` with delayed backlight work, flags, escape parser state, clear-on-open state, and driver private storage.
- `charlcd_write_char()` handles printable characters, control characters, ANSI-like clears/home, and LCD-specific `ESC [ L...` commands.
- `handle_lcd_special_code()` implements display/cursor/blink/backlight/font/line/shift/kill-line/reinitialize/custom-character commands.
- `charlcd_init()` initializes hardware and prints the boot message.

## Control Flow
Hardware drivers allocate a `struct charlcd`, fill dimensions and ops, then call `charlcd_register()`. Registration initializes display flags, optional backlight delayed work, calls the hardware `init_display()`, prints configured initial text, registers `/dev/lcd`, stores global `the_charlcd`, and registers a reboot notifier. Writes from userspace are write-only, single-open, and processed byte-by-byte with periodic `cond_resched()`.

## State And Persistence
Global `the_charlcd` and `charlcd_available` impose one active LCD core and one open file. Per-device state persists in `struct charlcd_priv`: flags for display/cursor/blink/backlight/font/line mode, cursor address, escape-sequence buffer, delayed backlight flash state, and `must_clear` for first open after boot text.

## Dependencies And Integration Points
Integrates with misc devices (`/dev/lcd`), reboot notifier chain, generated `UTS_RELEASE` or `CONFIG_PANEL_BOOT_MESSAGE`, delayed work, mutexes, and hardware drivers such as HD44780 GPIO, LCD2S, and legacy panel. The ops contract is defined in `charlcd.h`.

## Risks And Edge Cases
There is a global singleton, so multiple registered LCDs are not supported. Many ops are assumed present after registration; incomplete driver ops can crash on escape sequences. Escape parsing accepts partially valid sequences until max length and silently drops invalid gotoxy syntax. Backlight flash suppresses explicit backlight changes while active, which can surprise callers.

## Test Signals
Exercise `/dev/lcd` single-open and write-only enforcement, clear-on-first-open behavior, newline/backspace/form-feed/carriage-return/tab handling, every `ESC [ L` command, invalid and overlong escape sequences, reboot notifier messages, and unregister cancellation of delayed backlight work.
