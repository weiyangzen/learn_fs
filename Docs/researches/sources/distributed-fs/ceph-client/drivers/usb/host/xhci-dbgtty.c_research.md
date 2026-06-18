# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-dbgtty.c

Purpose: provides the tty backend for DbC, exposing a configured debug capability as dynamic raw serial devices named `ttyDBC*`. It maps tty writes into DbC bulk OUT requests and DbC bulk IN completions into tty flip-buffer input.

Important APIs and functions: global lifecycle uses `dbc_tty_init()` and `dbc_tty_exit()`. Device lifecycle uses `xhci_dbc_tty_probe()` and `xhci_dbc_tty_remove()`. The backend callbacks are `xhci_dbc_tty_register_device()` and `xhci_dbc_tty_unregister_device()` through `struct dbc_driver`. TTY operations include install/open/close/write/put_char/flush/write_room/chars_in_buffer/unthrottle. Request completions are `dbc_read_complete()` and `dbc_write_complete()`.

Control flow: `dbc_tty_init()` allocates a 64-minor dynamic tty driver. Probe allocates `dbc_port`, calls `xhci_alloc_dbc()`, stores `port` in `dbc->priv`, and assigns `xhci->dbc`. When DbC reaches configured state, the backend initializes a tty port, allocates an IDR minor, allocates the transmit kfifo and read/write request pools, then registers the tty device. On tty activation it queues read requests. Writes fill the kfifo, preserve each tty write as a transfer boundary with `tx_boundary`, and queue available write requests to DbC. Read completions push immediately to tty unless throttled or partially copied; otherwise they enqueue to `read_queue` and a tasklet retries.

State and persistence: state is runtime-only: global tty driver and IDR minor map; per-port kfifo, request pools, pending read queue, tasklet, lock, minor, and `registered/tx_running/tx_boundary` flags. Request buffers are owned by pool lists when idle and by DbC pending lists while in flight.

Dependencies and integration points: depends on `xhci-dbgcap.h` request APIs, tty core, tty flip buffers, IDR, kfifo, spinlocks, tasklets, and the xHCI device lifecycle. The tty backend is selected by `xhci_create_dbc_dev()` through `xhci_dbc_tty_probe()`.

Risks: concurrency spans tty methods, tasklet context, and DbC completion callbacks; `port_lock` protects list/kfifo state but completion callbacks drop into tty core paths. Partial flip-buffer copies rely on `n_read` and deferred retry ordering. `dbc_tty_write()` returns 0 while a previous write boundary is pending, which can affect user-space write behavior. Unregister must hang up and free all request pools without racing active completions; correctness depends on DbC stop/flush before request memory is freed.

Test signals: loading/unloading tty driver; minor allocation and reuse; opening/closing `ttyDBC0`; large writes split into 1024-byte requests while respecting write boundaries; throttled tty RX and unthrottle; cable disconnect causing `-ESHUTDOWN`; fault injection for partial request-pool allocation; lockdep for tty callbacks and tasklet paths.
