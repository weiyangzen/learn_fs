<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/l2cap_sock.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/l2cap_sock.c

## Purpose
Implements the Linux Bluetooth L2CAP socket layer for `BTPROTO_L2CAP`. It adapts user-visible socket operations (`bind`, `connect`, `listen`, `accept`, `sendmsg`, `recvmsg`, `setsockopt`, `getsockopt`, `shutdown`, and release) onto `struct l2cap_chan` operations in the L2CAP core, handling BR/EDR, LE ATT/fixed channels, LE credit-based connections, enhanced credit-based mode, raw sockets, datagram connectionless sockets, and stream/seqpacket connection-oriented sockets.

## APIs, Types, and Functions
The exported helper `l2cap_is_socket()` identifies sockets using this file's `proto_ops`. `l2cap_sock_ops` is the socket operation table installed for PF_BLUETOOTH/L2CAP sockets, and `l2cap_sock_family_ops` registers the protocol family create hook. `l2cap_proto` defines the per-socket private allocation size as `struct l2cap_pinfo`; `l2cap_sk_list` tracks live sockets for Bluetooth procfs reporting.

Primary socket entry points are `l2cap_sock_create()`, `l2cap_sock_alloc()`, `l2cap_sock_init()`, `l2cap_sock_bind()`, `l2cap_sock_connect()`, `l2cap_sock_listen()`, `l2cap_sock_accept()`, `l2cap_sock_getname()`, `l2cap_sock_sendmsg()`, `l2cap_sock_recvmsg()`, `l2cap_sock_shutdown()`, and `l2cap_sock_release()`. Option handlers split legacy `SOL_L2CAP` behavior into `l2cap_sock_getsockopt_old()` and `l2cap_sock_setsockopt_old()`, while modern `SOL_BLUETOOTH` options are handled by `l2cap_sock_getsockopt()` and `l2cap_sock_setsockopt()`. Helpers such as `l2cap_validate_bredr_psm()`, `l2cap_validate_le_psm()`, `l2cap_valid_mtu()`, `l2cap_get_mode()`, and `l2cap_set_mode()` enforce address-family, PSM, MTU, and mode constraints.

The file also supplies the `struct l2cap_ops` callback table used by the L2CAP core: new connection allocation, receive delivery, close and teardown notification, state change, ready/defer/resume/suspend transitions, send-buffer allocation, shutdown propagation, peer PID lookup, send timeout lookup, and packet filtering. Module lifecycle hooks are `l2cap_init_sockets()` and `l2cap_cleanup_sockets()`.

## Control Flow, State, and Persistence
Socket creation accepts `SOCK_SEQPACKET`, `SOCK_STREAM`, `SOCK_DGRAM`, and `SOCK_RAW`, requiring `CAP_NET_RAW` for non-kernel raw sockets. It allocates a Bluetooth sock, creates a paired `struct l2cap_chan`, stores it in `l2cap_pi(sk)->chan`, assigns default channel type/mode/MTUs, then links the socket into `l2cap_sk_list`. Destruction detaches `chan->data`, drops channel references, frees queued busy receive records, and purges receive, write, and error queues.

Bind validates `sockaddr_l2`, rejects simultaneous CID and PSM binding, validates Bluetooth address type, restricts LE fixed-channel user sockets to ATT, and enforces privileged binding for well-known BR/EDR and LE PSMs. It registers either a source CID or PSM with the L2CAP core, adjusts security defaults for SDP/RFCOMM/3DSP/raw sockets, requests HCI-connection holds for fixed channels, selects LE flow-control mode for LE PSM channels unless ECRED was selected, then moves both socket and channel to `BT_BOUND`.

Connect validates the destination address and prevents BR/EDR/LE source-destination mismatches, with a compatibility fix for old userspace that bound ATT sockets as `BDADDR_BREDR`. It delegates setup to `l2cap_chan_connect()` and waits for `BT_CONNECTED` through `bt_sock_wait_state()`, honoring nonblocking send timeout behavior. Listen requires a bound stream or seqpacket socket, validates the selected L2CAP mode against `disable_ertm` and `enable_ecred`, marks the channel as a parent nesting level, and transitions to `BT_LISTEN`. Accept waits on the parent socket wait queue and dequeues sockets produced by the new-connection callback.

Data transmission checks pending socket errors, rejects `MSG_OOB`, requires `BT_CONNECTED`, parses control messages into `sockcm_cookie`, waits while suspended, then calls `l2cap_chan_send()` under the channel lock. Receive handles deferred setup first: the first read on a deferred connection sends the appropriate deferred connection response for ECRED, LE credit-based, or BR/EDR setup. Normal receive delegates to generic Bluetooth stream or packet receive helpers, then updates L2CAP receive availability and drains `rx_busy` packets that previously could not fit in the socket receive buffer. For ERTM and LE flow-control modes, local busy state is cleared once receive memory drops to half the buffer.

Shutdown maps userspace `how` to socket shutdown bits, holds both socket and channel across lock drops, waits for outstanding ERTM ACKs before closing when needed, marks receive/send shutdown, closes the L2CAP channel under the connection mutex/channel lock ordering expected by the core, and optionally waits for `BT_CLOSED` if linger is configured. Release cleans pending accepted children, unlinks from the global socket list, shuts down, orphans the sock, and kills it when zapped and orphaned.

Persistent kernel-visible state is all in socket/channel structures and global registration objects: `sk_state`, `sk_shutdown`, `sk_err`, socket queues, `bt_sk()` flags, `l2cap_pi()` fields including `rx_busy`, channel addresses/CIDs/PSMs/security/mode/flags/credits/MTUs/connection pointers, and `l2cap_sk_list`. No on-disk persistence is used; procfs state exists only while the Bluetooth stack is registered.

## Dependencies and Integration
Depends on core socket APIs, Bluetooth socket helpers from `net/bluetooth/bluetooth.h`, HCI state and PHY/security helpers from `hci_core.h`, L2CAP core types and operations from `l2cap.h`, and SMP security helpers from `smp.h`. It integrates with protocol registration through `proto_register()`, `bt_sock_register(BTPROTO_L2CAP, ...)`, and `bt_procfs_init("l2cap", ...)`.

The file is tightly coupled to L2CAP core callbacks and lock ordering: channel callbacks call into socket wakeups, accept queues, packet filters, busy-flow control, and security state transitions, while socket operations call back into `l2cap_chan_connect()`, `l2cap_chan_send()`, `l2cap_chan_close()`, `l2cap_chan_reconfigure()`, and connection reference helpers. HCI integration appears through connection handles, device class exposure, encryption key size, LE security escalation via `smp_conn_security()`, PHY get/set, and no-flush capability checks. Security modules are reached through `security_sk_clone()` and `sk_filter()`.

## Risks and Test Signals
Concurrency and lifetime are the highest-risk areas: `chan->data` points back to `struct sock`, callbacks may run during teardown, accepted child sockets use nested locking to avoid lockdep issues, and several paths deliberately drop and reacquire socket/channel locks. Regression tests should stress release during connect/listen/accept, deferred setup races, child cleanup, callback teardown, and orphan/zapped socket cleanup.

Compatibility risks include legacy `SOL_L2CAP` option semantics, ATT userspace compatibility for old BR/EDR bind behavior, mode gating by `disable_ertm`/`enable_ecred`, fixed-channel restrictions, and security-level transitions while connected or deferred. Data-path risks include receive-buffer exhaustion in ERTM/LE modes, `rx_busy` queuing, busy-state recovery thresholds, filter application differences by mode, and ERTM ACK wait timeout/signal handling during shutdown.

Useful test signals are successful PF_BLUETOOTH/L2CAP socket registration and `/proc/net/l2cap` creation, bind/connect/listen/accept across BR/EDR and LE address types, privilege checks for raw sockets and well-known PSMs, getsockopt/setsockopt coverage for `BT_SECURITY`, `BT_DEFER_SETUP`, `BT_FLUSHABLE`, `BT_POWER`, `BT_SNDMTU`, `BT_RCVMTU`, `BT_PHY`, and `BT_MODE`, packet send/receive under all supported channel modes, and fault injection for allocation, copy-to/from-user, signal interruption, timeout, and link teardown paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/l2cap_sock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/leds.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/leds.c

## Purpose
Provides optional Bluetooth LED trigger support for the kernel Bluetooth stack. It exposes a global `bluetooth-power` trigger representing whether any HCI device is powered, and per-HCI-device power triggers named from the controller device name.

## APIs, Types, and Functions
`DEFINE_LED_TRIGGER(bt_power_led_trigger)` defines the global trigger object. `struct hci_basic_led_trigger` wraps a `struct led_trigger` with the owning `struct hci_dev`; `to_hci_basic_led_trigger()` converts from trigger pointer back to that wrapper. Public functions are `hci_leds_update_powered()`, `hci_leds_init()`, `bt_leds_init()`, and `bt_leds_cleanup()`.

`hci_leds_update_powered()` updates the per-device `hdev->power_led` and then updates the global trigger. `power_activate()` initializes a newly attached LED class device to the current HCI powered state. `led_allocate_basic()` allocates and registers a per-device managed LED trigger using `devm_kzalloc()`, `devm_kasprintf()`, and `devm_led_trigger_register()`.

## Control Flow, State, and Persistence
Bluetooth core initialization calls `bt_leds_init()`, registering the simple global trigger name `bluetooth-power`; Bluetooth exit or init failure calls `bt_leds_cleanup()`. HCI device registration calls `hci_leds_init()`, which allocates a managed per-device trigger such as `hci0-power` and stores it in `hdev->power_led`.

When an HCI device powers up, `hci_leds_update_powered(hdev, true)` sets the device trigger to `LED_FULL` and sets the global trigger to `LED_FULL`. When a device powers down, the per-device trigger is set to `LED_OFF`, then the function scans `hci_dev_list` under `hci_dev_list_lock`; if any other device still has `HCI_UP`, the global trigger remains `LED_FULL`, otherwise it becomes `LED_OFF`.

State is held in LED trigger registration objects, `hdev->power_led`, and the live HCI device list/flags. Per-device trigger memory and names are device-managed and disappear with the HCI device. There is no durable persistence; LED brightness is a runtime reflection of HCI flags.

## Dependencies and Integration
Depends on Bluetooth core declarations from `bluetooth.h` and `hci_core.h`, the kernel LED trigger subsystem, device-managed allocation, and the global HCI device list. Integration points are `af_bluetooth.c` for stack-wide init/cleanup, `hci_core.c` for per-device trigger creation during `hci_register_dev()`, and `hci_sync.c` for powered-state updates during open and close.

## Risks and Test Signals
Risks include missed global-trigger updates when HCI power transitions bypass `hci_leds_update_powered()`, stale brightness if `power_activate()` races with HCI flag changes, allocation or registration failures leaving `hdev->power_led` NULL, and global LED state depending on correct locking and iteration of `hci_dev_list`.

Test signals include presence of the `bluetooth-power` trigger when Bluetooth LED support is enabled, per-controller trigger creation after HCI registration, LED brightness changing to full/off on controller up/down, global trigger staying on while at least one controller remains up, and clean unregister behavior on Bluetooth subsystem exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/leds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/leds.h -->
# sources/distributed-fs/ceph-client/net/bluetooth/leds.h

## Purpose
Declares the Bluetooth LED trigger interface used by the core Bluetooth and HCI code, while compiling to no-op inline helpers when `CONFIG_BT_LEDS` is disabled.

## APIs, Types, and Functions
When `CONFIG_BT_LEDS` is enabled, the header declares `hci_leds_update_powered(struct hci_dev *hdev, bool enabled)`, `hci_leds_init(struct hci_dev *hdev)`, `bt_leds_init(void)`, and `bt_leds_cleanup(void)`. When disabled, it provides static inline no-op definitions with the same signatures, allowing callers to invoke LED hooks unconditionally.

## Control Flow, State, and Persistence
There is no runtime control flow in the enabled case beyond providing declarations. In the disabled case, all four functions compile away and do not touch HCI device state, LED triggers, or global Bluetooth state. The header itself owns no state and persists nothing.

## Dependencies and Integration
The header relies on callers already having appropriate declarations for `struct hci_dev` and `bool`, which is true for its Bluetooth core include sites. It is included by `leds.c` for the implementation and by Bluetooth core files that need LED lifecycle hooks. Its config gate keeps the rest of the stack independent from the LED subsystem when Bluetooth LEDs are not built.

## Risks and Test Signals
The main risk is signature drift between the enabled declarations, disabled inline definitions, and `leds.c` implementation. Build coverage should include both `CONFIG_BT_LEDS=y/m` and `CONFIG_BT_LEDS=n`. Runtime tests for the disabled configuration should confirm HCI registration and power transitions do not require LED subsystem symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/leds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/lib.c -->
# sources/distributed-fs/ceph-client/net/bluetooth/lib.c

## Purpose
Provides small exported utility routines shared across the Bluetooth kernel subsystem: Bluetooth address byte-order conversion, conversion between HCI/Bluetooth status codes and Linux errno values, and standardized Bluetooth logging helpers.

## APIs, Types, and Functions
`baswap()` reverses the six bytes of a `bdaddr_t` and is exported for modules that need Bluetooth address order conversion. `bt_to_errno()` maps Bluetooth controller status/error codes to positive Linux errno numbers. `bt_status()` maps negative Linux errno values back to Bluetooth status codes, returning nonnegative input unchanged and using `0x1f` for unspecified errors.

Logging helpers `bt_info()`, `bt_warn()`, `bt_err()`, `bt_warn_ratelimited()`, and `bt_err_ratelimited()` wrap `pr_info`, `pr_warn`, `pr_err`, and ratelimited variants with the `Bluetooth: ` prefix established by `pr_fmt`. Under `CONFIG_BT_FEATURE_DEBUG`, `bt_dbg_set()`, `bt_dbg_get()`, and `bt_dbg()` maintain and use a runtime debug-enable flag; `bt_dbg()` emits `KERN_DEBUG` output only when enabled. Exported symbols make these helpers available to other Bluetooth components and modules.

## Control Flow, State, and Persistence
`baswap()` is a fixed six-iteration byte reversal. `bt_to_errno()` and `bt_status()` are switch-table conversions with explicit fallbacks. Logging helpers build `struct va_format` around their variadic arguments and call the appropriate printk helper.

The only mutable state is the file-local `debug_enable` boolean compiled under `CONFIG_BT_FEATURE_DEBUG`. It is toggled by `bt_dbg_set()` and observed by `bt_dbg_get()` and `bt_dbg()`. There is no locking around this flag; it is a simple runtime subsystem knob used for best-effort debug logging. No state is persisted beyond process/kernel memory.

## Dependencies and Integration
Depends on `linux/export.h`, printk infrastructure, variadic formatting, errno constants, and Bluetooth base types from `net/bluetooth/bluetooth.h`. Address conversion is used by higher-level Bluetooth networking code such as 6LoWPAN and BNEP. Error conversion is used by connection teardown and command paths in L2CAP, SCO, ISO, and HCI sync code. Debug toggling integrates with Bluetooth management commands that expose runtime debug state.

## Risks and Test Signals
Risks include incomplete mappings as Bluetooth status codes evolve, asymmetry between `bt_to_errno()` and `bt_status()` where multiple status codes collapse to one errno, callers confusing positive errno returns from `bt_to_errno()` with normal kernel negative-error conventions, and unsynchronized debug flag reads/writes. `baswap()` also assumes `bdaddr_t` is exactly six address bytes, as expected by Bluetooth core types.

Useful test signals include table-driven checks for known status-code mappings in both directions, fallback behavior for unknown codes, preservation of nonnegative input in `bt_status()`, byte-exact address reversal, logging prefix verification, ratelimit behavior under repeated warnings/errors, and management-path debug toggling under `CONFIG_BT_FEATURE_DEBUG`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/lib.c -->
