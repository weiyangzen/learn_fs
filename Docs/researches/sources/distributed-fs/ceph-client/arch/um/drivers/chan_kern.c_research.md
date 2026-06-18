<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/chan_kern.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/chan_kern.c

Purpose: implements the kernel-side channel core for UML TTY devices. It parses backend strings, opens host descriptors, installs read/write IRQs, routes input bytes into TTY flip buffers, writes console/TTY output, handles window-change setup, and tears down disappearing interrupt sources safely.

Important APIs/types/functions: key functions are `open_one_chan()`, `enable_chan()`, `free_irqs()`, `close_one_chan()`, `close_chan()`, `write_chan()`, `console_write_chan()`, `console_open_chan()`, `chan_window_size()`, `chan_config_string()`, `parse_chan()`, `parse_chan_pair()`, and `chan_interrupt()`. `struct chan_type` maps backend names to `fd_ops`, `null_ops`, `port_ops`, `pty_ops`, `pts_ops`, `tty_ops`, `xterm_ops`, or `not_configged_ops`.

Control flow: `parse_chan_pair()` replaces any existing channel list, splitting `input,output` strings or using one backend for both directions. `enable_chan()` opens each channel, sets nonblocking input, optionally duplicates output as blocking in time-travel external/infinite-CPU modes, and requests UML read/write IRQs. Read IRQs call `chan_interrupt()`, which drains bytes until EAGAIN/EIO, inserts them into the TTY flip buffer, schedules retry work if the flip buffer is full, and hangs up/defers IRQ freeing on EOF. Writes go through the active output channel and return only the primary channel result.

State and persistence: per-channel runtime state includes host FDs, enabled/opened flags, backend data, and line membership. `irqs_to_free` is a global deferred-free list for IRQ cleanup that cannot happen in IRQ context. No disk state is written.

Dependencies and integration points: depends on UML IRQ allocation/freeing, `os_*` host FD helpers, `time_travel_mode`, Linux TTY flip buffers, delayed work, and backend `chan_ops`. It is driven by `line.c`, `stdio_console.c`, and `ssl.c`.

Risks: close paths run from both process and interrupt contexts; freeing IRQs immediately in the wrong context can crash. Time-travel blocking-output mode deliberately avoids output IRQs and changes FD semantics. Bad parser lifetime handling can free strings still referenced by backend `dev` pointers.

Test signals: boot with `fd`, `null`, `port`, `pty/pts`, `tty`, and configured-out channels; exercise split input/output pairs; close host endpoints to trigger hangups; fill TTY flip buffers; run time-travel modes; and use mconsole config/get_config/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/chan_kern.c -->
