# sources/distributed-fs/ceph-client/drivers/macintosh/macio-adb.c

Purpose: provides an ADB controller driver for the Mac I/O Hydra ADB block. It implements the `struct adb_driver` operations used by the unified ADB core.

Important APIs and functions: `macio_probe()` detects OF compatible `chrp,adb0`; `macio_init()` maps controller registers, initializes active devices/autopoll, maps IRQ, and enables DFB/TAG interrupts. `macio_send_request()` queues ADB requests after stripping the leading `ADB_PACKET`. `macio_adb_interrupt()` handles transmit grants, replies, errors, and autopoll packets. `macio_adb_autopoll()`, `macio_adb_reset_bus()`, and `macio_adb_poll()` implement the remaining ADB driver callbacks.

Control flow: queued requests are protected by `macio_lock`. If idle, a new request asserts `TAR`; on `TAG`, the interrupt handler writes request bytes and either completes immediately or waits for `DFB`. On reply, it copies the controller data registers into `req->reply`, advances the queue, and calls the completion callback outside the lock. Unsolicited autopoll bytes are copied into a stack buffer and passed to `adb_input()`.

State and persistence: global controller MMIO pointer, current/last request queue, and spinlock. Autopoll device mask is held in hardware `active_hi/active_lo` registers. No persistent storage.

Dependencies and integration: relies on OF address/IRQ parsing, Hydra register layout, `linux/adb.h`, and the unified ADB core. Hardware access uses `in_8()`/`out_8()`.

Risks: synchronous requests spin in `macio_adb_poll()`. Request lifetime relies on callers keeping `struct adb_request` alive until completion. Error bits are cleared but not surfaced strongly to callers. Reset holds the spinlock with IRQs disabled for a long timeout loop.

Test signals: driver selection by ADB core, interrupt-driven and polled request completion, autopoll delivery to keyboards/mice, reset-bus behavior, IRQ request failure cleanup, and no queue corruption under multiple outstanding ADB requests.
