<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/line.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/line.h

Purpose: declares the shared UML TTY line structures and operations used by console and serial drivers.

Important APIs/types/functions: `struct line_driver` defines static driver identity, device name, major/minor, TTY type/subtype, IRQ names, mconsole device, and registered `tty_driver`. `struct line` stores per-line TTY port, validity, IRQs, init string, channel list, channel pointers, lock, throttled flag, ring-buffer pointers, SIGWINCH state, delayed work, and owning driver.

Control flow: the header supplies prototypes for TTY operations, setup/config/remove helpers, IRQ setup, channel close, driver registration, and xterm title augmentation.

State and persistence: no state is instantiated here, but the structs define runtime state layout for console and serial arrays.

Dependencies and integration points: depends on Linux list/workqueue/TTY/interrupt/spinlock/mutex APIs, `chan_user.h`, and `mconsole_kern.h`.

Risks: structure fields are shared by several C files; changing layout or semantics affects channel activation, buffering, and mconsole config. The buffer comments note a future kfifo replacement but current callers depend on raw pointers.

Test signals: compile users of all declared functions, register both console and serial line drivers, and exercise per-line state transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/line.h -->
