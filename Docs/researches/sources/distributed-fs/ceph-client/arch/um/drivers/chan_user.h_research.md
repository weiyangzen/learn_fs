<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/chan_user.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/chan_user.h

Purpose: defines the host-side channel backend interface and shared option structure. It is the contract between kernel channel management in `chan_kern.c` and individual host descriptor backends.

Important APIs/types/functions: `struct chan_opts` carries an announce callback, xterm title, and raw-mode flag. `struct chan_ops` supplies backend type, init/open/close/read/write/console_write/window_size/free callbacks, and a `winch` capability flag. It declares backend ops objects and generic helper functions.

Control flow: backend code populates one `chan_ops` instance. `chan_kern.c` parses backend names and calls `init`, `open`, I/O callbacks, and `free`; `line.c` asks `register_winch_irq()` to translate window-change pipe events into guest signals.

State and persistence: the header owns no state. Backend-private state is opaque `void *` returned from `init`.

Dependencies and integration points: includes UML init and Linux types, forward-declares `tty_port`, and integrates with `__uml_help` through `__channel_help()`.

Risks: callback prototypes must stay synchronized across all backends. The `type` string is exposed in `mconsole config` query output. Backends that claim `winch` must provide FDs valid for TTY window handling.

Test signals: build every backend, verify parser accepts each declared `type`, query config strings through mconsole, and compile with backends excluded so declarations still match fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/chan_user.h -->
