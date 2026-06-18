# File Research: sources/block-storage/util-linux/sys-utils/tunelp.c

This deprecated maintenance-mode utility configures Linux line-printer (`lp`) driver parameters. It parses command options into a linked list of ioctl commands, opens the target device nonblocking, verifies it is a character device, applies queued ioctls, optionally prints status, and prints the IRQ/polling mode by default.

Each option appends a `struct command` containing an lp ioctl number and value: `LPSETIRQ`, `LPTIME`, `LPCHAR`, `LPWAIT`, `LPABORT`, `LPABORTOPEN`, `LPCAREFUL`, `LPGETSTATUS`, and `LPRESET`. Numeric arguments use util-linux checked parsers; `on|off` arguments go through `ul_parse_switch()`. `-q` controls whether the final IRQ query is printed.

The device is opened `O_WRONLY | O_NONBLOCK` specifically to avoid blocking when `ABORTOPEN` is already configured and the printer is offline or in error. The program tests for old-kernel ioctl numbering compatibility by probing `LPGETIRQ`; if the new ioctl range returns `EINVAL`, it subtracts `0x0600` from ioctl numbers.

For `LPGETSTATUS`, it handles historical kernels that return status as the ioctl return value rather than through the output pointer, then decodes busy, ready, out-of-paper, online, and error bits. For all other commands it warns on ioctl failure but continues through the command list. The final IRQ query treats zero as polling mode and nonzero as the active IRQ.
