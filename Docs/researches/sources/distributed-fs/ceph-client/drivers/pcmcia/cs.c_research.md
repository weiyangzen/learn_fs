# sources/distributed-fs/ceph-client/drivers/pcmcia/cs.c

Purpose: Implements the PCMCIA socket core and Card Services event engine. It registers socket devices, starts the per-socket `pccardd` thread, handles insertion/ejection, power/reset sequencing, suspend/resume, CardBus dispatch, callback registration for the PCMCIA bus layer, socket sysfs event handling, and socket class registration.

Important APIs and functions: Exported functions include `pcmcia_register_socket()`, `pcmcia_unregister_socket()`, `pcmcia_get_socket()`, `pcmcia_put_socket()`, `pcmcia_parse_events()`, `pcmcia_parse_uevents()`, `pccard_register_pcmcia()`, and `pcmcia_reset_card()`. Important internals are `socket_setup()`, `socket_shutdown()`, `socket_insert()`, `socket_suspend()`, resume stages, `socket_detect_change()`, and `pccardd()`.

Control flow: Socket registration assigns a socket number, initializes locks/completions, runs resource init, starts `pccardd`, queues an initial detect event, and asynchronously requests the `pcmcia` module. `pccardd` registers the socket device/sysfs, waits for userspace, then loops over hardware and sysfs events under `skt_mutex`. Insert powers and resets the card through socket ops, distinguishes CardBus from 16-bit PCMCIA, calls `cb_alloc()` for CardBus or bus callback `add()` for PCMCIA. Remove calls bus callback `remove()`, powers down, clears fake CIS and function count, and frees CardBus devices.

State and persistence: Maintains global `pcmcia_socket_list` protected by `pcmcia_socket_list_rwsem`, socket state bits, lock counts, socket voltage/reset fields, callback pointer, event bitmasks, thread pointer, CIS cache, fake CIS, and per-socket completions. State is volatile and rebuilt across insertion/removal.

Dependencies and integration points: Depends on socket controller `pccard_operations`, resource ops, socket sysfs helpers, `cardbus.c`, `ds.c` callback registration, kernel kthreads/freezer, device class PM, and module parameters controlling reset and delay timings.

Risks: The core is concurrency-heavy: socket ops, sysfs events, PM callbacks, card interrupts, and kthread shutdown converge on the same state. Timing parameters affect real hardware stability. CardBus and 16-bit flows diverge, so state bits must stay coherent. Cleanup waits for device references via completions.

Test signals: Register/unregister socket drivers, insert/eject PCMCIA and CardBus cards, sysfs insert/eject/suspend/resume/requery, system suspend/resume with card replacement, reset requests, and lockdep/kthread teardown coverage.
