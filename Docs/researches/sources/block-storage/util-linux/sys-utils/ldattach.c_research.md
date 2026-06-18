# File Research: sources/block-storage/util-linux/sys-utils/ldattach.c

`ldattach.c` implements the `ldattach(8)` utility, which opens a serial tty, configures termios settings, attaches a Linux tty line discipline with `TIOCSETD`, and stays resident so the line discipline remains active.

Key behavior:
- Maintains lookup tables for supported line disciplines (`TTY`, `SLIP`, `PPP`, `GSM0710`, `PPS`, etc.) and termios input flags.
- Parses serial configuration options for speed, character size, parity, stop bits, input flags, intro command, intro pause, debug mode, and GSM0710 MTU.
- Uses `cfmakeraw()` and `tcsetattr()` to put the tty into raw mode before attaching the line discipline.
- Supports non-standard baud rates via `struct termios` `c_ispeed`/`c_ospeed` and `BOTHER` where available.
- Sends an optional intro command before attaching, then sleeps for a bounded pause.
- Applies GSM0710-specific configuration through `GSMIOC_GETCONF`/`GSMIOC_SETCONF`.
- Daemonizes unless `--debug` is used, then calls `pause()` to keep the process alive.

Important dependencies:
- Linux tty constants and ioctls from `<linux/tty.h>`, `<linux/gsmmux.h>` or the local fallback `struct gsm_config`.
- util-linux helpers for parsing, I/O, localization, diagnostics, and stdout cleanup.

Risk notes:
- `signal(SIGKILL, handler)` has no practical effect because `SIGKILL` cannot be caught.
- `gsm0710_set_conf()` ignores ioctl return values, so GSM configuration failures are silent.
- `parse_iflag()` mutates `optarg` with `strtok()`, which is acceptable for command-line storage but means the original string is destroyed.
- The process must remain alive for the discipline to remain attached; daemonization failure aborts setup after the ioctl has already succeeded.
