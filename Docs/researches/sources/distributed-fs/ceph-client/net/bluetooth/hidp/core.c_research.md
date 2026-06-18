# sources/distributed-fs/ceph-client/net/bluetooth/hidp/core.c

## Purpose
Implements the Bluetooth HIDP runtime: session creation/deletion, L2CAP control and interrupt channel I/O, HID/input device registration, boot-protocol keyboard/mouse fallback, HID raw report transactions, idle timeout handling, and module init/exit.

## APIs, Types, and Functions
Public entry points used by `sock.c` are `hidp_connection_add()`, `hidp_connection_del()`, `hidp_get_connlist()`, and `hidp_get_conninfo()`. Module lifecycle is `hidp_init()`/`hidp_exit()`, which delegate socket setup/cleanup to `hidp_init_sockets()` and `hidp_cleanup_sockets()`.

Session management uses global `hidp_session_list`, `hidp_session_sem`, and `hidp_session_wq`; `struct hidp_session` is defined in `hidp.h` and refcounted with `kref`. Key helpers include `hidp_session_new()`, `hidp_session_start_sync()`, `hidp_session_probe()`, `hidp_session_remove()`, `hidp_session_run()`, `hidp_session_thread()`, `hidp_session_unregister_conn()`, `hidp_session_get()`, and `hidp_session_put()`.

I/O helpers include `hidp_send_message()`, `hidp_send_ctrl_message()`, `hidp_send_intr_message()`, `hidp_recv_ctrl_frame()`, `hidp_recv_intr_frame()`, `hidp_process_handshake()`, `hidp_process_hid_control()`, `hidp_process_data()`, `hidp_process_transmit()`, and `hidp_send_frame()`. HID/input integration uses `hidp_setup_hid()`, `hidp_setup_input()`, `hidp_session_dev_init()`, `hidp_session_dev_add()`, `hidp_session_dev_del()`, `hidp_session_dev_work()`, and HID low-level driver callbacks `hidp_parse()`, `hidp_raw_request()`, `hidp_output_report()`, `hidp_get_raw_report()`, and `hidp_set_raw_report()`.

## Control Flow, State, and Persistence
`hidp_connection_add()` verifies that both sockets are connected L2CAP sockets with matching source/destination addresses, validates flags, gets the underlying `l2cap_conn`, allocates a session, initializes HID or boot input devices, takes socket file references, and registers an `l2cap_user`. The L2CAP probe callback prevents duplicate sessions for the same remote address, starts the kthread, registers boot input synchronously or schedules HID registration asynchronously, then links the session into the global list with its own reference.

The session thread attaches wait entries to both socket wait queues, boosts priority, starts the idle timer, signals startup, and loops while not terminated and both sockets are `BT_CONNECTED`. Each loop drains interrupt receive skbs, sends queued interrupt frames, drains control receive skbs, sends queued control frames, then sleeps on the global HIDP wait queue. Runtime errors, socket disconnect, virtual cable unplug, idle timeout, or explicit deletion set `terminate`, wake the thread, unregister the L2CAP user, wake report waiters, delete timers, and drop references.

Incoming interrupt data with `HIDP_TRANS_DATA | HIDP_DATA_RTYPE_INPUT` resets the idle timer and feeds either boot input decoding or the HID core. Control frames handle handshakes, HID_CONTROL commands, and DATA reports. Raw GET_REPORT and SET_REPORT are serialized by `report_mutex`, set wait bits in `session->flags`, transmit control requests, and wait up to 5 or 10 seconds for matching DATA/handshake completion on `report_queue`.

State persists in `struct hidp_session`: address, L2CAP user/connection, control and interrupt sockets, transmit queues, MTUs, idle timeout, HID/input devices, report descriptor data, keyboard state, LED state, report transaction fields, timer, kthread state, termination flag, and refcount. Global state persists as the session list and module/socket registrations.

## Dependencies and Integration
Depends on Bluetooth core, L2CAP socket internals, HID core and hidraw, input core, skbs, kthreads, timers, wait queues, kernel socket send APIs, file references, and module reference counting. It integrates with userspace through the HIDP ioctl ABI in `sock.c`, with L2CAP through `l2cap_register_user()`, with the HID subsystem through `hid_ll_driver`, and with the input subsystem for boot-protocol devices when no usable HID report descriptor is supplied or the HID device is ignored.

## Risks and Test Signals
Risks include concurrent teardown between userspace deletion, L2CAP removal, idle timeout, and self-unregistering thread exit; report waiters hanging or receiving the wrong report if flags/numbered reports are mishandled; skb ownership transfer in `hidp_process_data()`; unbounded trust in userspace report descriptors subject to HID parser behavior; boot keyboard/mouse decoding limits; socket wakeup and memory-barrier assumptions; and cleanup ordering for asynchronous HID registration work versus session removal.

Strong test signals are ioctl-driven add/delete/list/info flows with duplicate-session checks, mismatched or disconnected socket rejection, HID descriptor device registration and fallback boot input registration, virtual cable unplug behavior, idle timeout disconnect, GET_REPORT/SET_REPORT success/handshake/timeout/signal paths, interrupt input delivery to HID and input devices, transmit retry on `-EAGAIN`, L2CAP removal during device probe, and module unload after active sessions terminate.
