# sources/distributed-fs/ceph-client/drivers/tty/hvc/hvc_console.c

## Purpose
`hvc_console.c` is the shared hypervisor virtual console core. It exposes early kernel console support and a tty driver named `hvc` on major 229, then lets low-level platform backends provide transport operations through `struct hv_ops`. The file handles generic tty lifetime, buffering, polling, IRQ notifier integration, resize delivery, hangup behavior, and the `khvcd` kernel thread.

## Important APIs, Types, and Functions
The external entry points are `hvc_instantiate()`, `hvc_alloc()`, `hvc_remove()`, `hvc_poll()`, `hvc_kick()`, and `__hvc_resize()`. `hvc_instantiate()` registers an early console slot before a full tty exists. `hvc_alloc()` creates an `hvc_struct`, attaches tty-port state, assigns a stable tty index, and lazily initializes the global tty driver via `hvc_init()`. `hvc_remove()` invalidates early-console arrays and vhangups any attached tty.

TTY operations are implemented by `hvc_install()`, `hvc_open()`, `hvc_close()`, `hvc_cleanup()`, `hvc_hangup()`, `hvc_write()`, `hvc_write_room()`, `hvc_chars_in_buffer()`, `hvc_tiocmget()`, and `hvc_tiocmset()`. Console output uses `hvc_console_print()` and translates LF to CRLF before calling backend `put_chars()`.

## Control Flow
Early boot calls `hvc_console_init()` to register a `struct console`. Backend discovery later calls `hvc_instantiate()` and possibly re-registers the console when the selected index becomes usable. Runtime device discovery calls `hvc_alloc()`, which starts `khvcd` once, registers the tty driver, links the new `hvc_struct`, and wakes console registration if needed.

Writes copy user data into `hp->outbuf`, call `hvc_push()` under `hp->lock`, and kick `khvcd` if data remains or wakeups are needed. Reads are driven by `__hvc_poll()`: it flushes pending output, gets the attached tty, checks throttling, requests flip-buffer room, invokes backend `get_chars()`, handles `-EPIPE` as carrier loss via `tty_hangup()`, processes Magic SysRq for the active console, and pushes flip-buffer data outside the lock. `khvcd()` walks all registered consoles, backs off from 10 ms to 2000 ms when idle, and can be woken by `hvc_kick()` or backend IRQ notifiers.

## State and Persistence Behavior
Persistent state is in global early-console arrays `vtermnos[]` and `cons_ops[]`, global device list `hvc_structs`, `last_hvc`, `hvc_driver`, `hvc_task`, and each `hvc_struct`. Per-device state includes tty-port reference counts, output buffer fill, backend data/ops, IRQ-requested state, terminal size, and deferred resize work. No on-disk persistence exists.

## Dependencies and Integration Points
The core integrates with Linux tty, console, tty-port, kthread, workqueue, Magic SysRq, freezer, and optional console-poll APIs. Backends supply `struct hv_ops` for transports such as OPAL, VIO, Xen, RTAS, SBI, DCC, udbg, and IUCV. IRQ-capable backends commonly use `hvc_irq.c` notifier callbacks.

## Risks and Edge Cases
The file is concurrency-sensitive: `hvc_structs_mutex`, `hp->lock`, `hp->port.lock`, tty krefs, and console locking have distinct roles. Backend `put_chars()` returning zero or `-EAGAIN` causes buffered retry and tty wakeup behavior, while other errors discard buffered output. `hvc_remove()` intentionally does not clear IRQ state because hangup paths may still free it. Early-console slots are limited to `MAX_NR_HVC_CONSOLES`, while additional ttys get indices beyond that range and cannot be kernel consoles.

## Test Signals
Useful signals include successful `hvc` tty registration, early `console=hvcN` output, backend hotplug add/remove, close with pending output, IRQ and polling mode reads, throttled tty input, Magic SysRq over active console, terminal resize delivery, and `-EPIPE` backend hangup behavior.
