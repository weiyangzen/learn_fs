<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/chan.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/chan.h

Purpose: declares the kernel-side UML channel abstraction used by virtual consoles and serial lines. A channel joins a `struct line` TTY endpoint to one host-side backend such as fd, null, port, pty, tty, or xterm.

Important APIs/types/functions: `struct chan` stores list membership, owning `line`, device string, primary/input/output/opened/enabled flags, input/output FDs, backend `chan_ops`, and backend-private data. Exported functions include `parse_chan_pair()`, `enable_chan()`, `close_chan()`, `deactivate_chan()`, `write_chan()`, `console_write_chan()`, `console_open_chan()`, `chan_interrupt()`, `chan_enable_winch()`, `chan_window_size()`, and `chan_config_string()`.

Control flow: users do not call backend operations directly; `line.c` calls the channel API, and `chan_kern.c` dispatches through `chan_ops` while managing IRQs and file descriptor lifecycle.

State and persistence: channel state is per-line runtime state. It tracks opened host FDs and parsed configuration strings but has no persistence beyond boot command-line or mconsole reconfiguration.

Dependencies and integration points: depends on Linux TTY/console/list APIs, `chan_user.h` backend operations, and `line.h`. It is used by stdio console and software serial drivers.

Risks: the same backend FD can be input and output or split across two channels, so close order and primary-channel semantics matter. Fields are bitflags with lifecycle-sensitive transitions.

Test signals: compile all channel backends, boot with single and split `con=`/`ssl=` channel pairs, reconfigure via mconsole, and verify hangup/window-size behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/chan.h -->
