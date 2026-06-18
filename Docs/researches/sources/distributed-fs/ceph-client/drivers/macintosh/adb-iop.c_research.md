<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/adb-iop.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/adb-iop.c

Purpose: This is an Apple Desktop Bus controller backend for Macintosh systems with an I/O Processor (IOP), such as IIfx/Quadra 9x0-class systems. It adapts unified ADB requests to IOP messages and handles autopoll responses.

Important APIs and state: It provides `struct adb_driver adb_iop_driver` with probe, init, send_request, autopoll, poll, and reset_bus callbacks. Global request queue state is `current_req`, `last_req`, and `adb_iop_state` (`idle`, `sending`, `awaiting_reply`). Autopoll state is `autopoll_devs` and `autopoll_addr`.

Control flow: `adb_iop_write()` validates ADB packets, initializes request fields, queues them under local IRQ masking, and starts sending if idle. `adb_iop_start()` strips the leading `ADB_PACKET` byte, wraps the remaining packet in `struct adb_iopmsg`, marks the request sent, and submits to the IOP manager. `adb_iop_complete()` marks the state as awaiting a reply after send completion. `adb_iop_listen()` handles explicit replies and autopoll messages, copies replies into the current ADB request when expected, forwards valid autopoll packets to `adb_input()`, prepares the IOP reply that selects the next autopoll address, completes the IOP message, and finalizes the ADB request if applicable.

State and persistence: State is global to the single IOP ADB controller. Local IRQ disabling protects request queue and state transitions. Autopoll device masks are remembered in globals and programmed through IOP messages.

Dependencies and integration: It depends on m68k Macintosh IOP infrastructure, `linux/adb.h`, `asm/adb_iop.h`, unaligned helpers, and the ADB core's driver table. It calls `adb_input()` for autopoll data.

Risks and test signals: Synchronous sends busy-poll `adb_iop_poll()` until completion. Request lifecycle assumes one explicit reply at a time. Autopoll address selection depends on IOP flags and masks. Test queue ordering, explicit requests with and without reply, autopoll enable/disable masks, reset-bus delay, and timeout packets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/adb-iop.c -->
