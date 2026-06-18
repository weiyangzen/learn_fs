<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/port_kern.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/port_kern.c

Purpose: implements the kernel-side listener and connection queue for UML `port:` channels. It accepts host TCP connections, starts telnet helper handoff, queues completed connections, and wakes UML line openers waiting for a connection.

Important APIs/types/functions: main structs are `port_list`, `port_dev`, and `connection`. Key functions are `port_data()`, `port_wait()`, `port_remove_dev()`, `port_kern_free()`, `free_port()`, plus IRQ/work handlers `port_interrupt()`, `port_work_proc()`, `port_accept()`, and `pipe_interrupt()`.

Control flow: `port_data()` finds or creates a shared listener for a TCP port, registers an accept IRQ, and returns a per-device `port_dev`. Accept IRQs schedule work; work calls `port_accept()` until no more connections. A helper/telnetd pipe IRQ receives the connected FD and helper PID, moves the connection from pending to completed, and completes waiters. `port_wait()` waits interruptibly, consumes a completed connection, frees the helper IRQ, and returns the connected FD.

State and persistence: global `ports` stores listeners, each with wait count, pending/completed lists, completion, socket FD, and lock. Per-device state tracks helper/telnetd PIDs for cleanup. No persistent data is written.

Dependencies and integration points: depends on UML IRQs, completions, workqueues, host FD-passing helpers, `port_user.c`, and channel backend lifecycle.

Risks: list operations span IRQ, workqueue, and process contexts. Some connection-list manipulation relies on serialized paths and minimal locking. If no UML line waits, a telnet client receives a message but the connection is still queued/pending until helper completion. Cleanup must kill helper processes and free IRQs outside IRQ context.

Test signals: connect multiple telnet clients to one port, open/close UML lines, no-waiter behavior, helper failure, interrupted `port_wait()`, mconsole remove, and UML exit cleanup of listening sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/port_kern.c -->
