# sources/distributed-fs/ceph-client/net/atm/common.c

Purpose: core ATM socket/VCC implementation shared by PVC and SVC protocol families. It handles VCC allocation, connection, send/receive, QoS options, socket polling, device-signal notification, and module initialization.

Important APIs, types, and functions: exported globals are `vcc_hash` and `vcc_sklist_lock`. Exported functions include `vcc_insert_socket`, `vcc_release_async`, `vcc_process_recv_queue`, `atm_dev_signal_change`, `atm_dev_release_vccs`, `register_atmdevice_notifier`, and `unregister_atmdevice_notifier`. Core socket operations are `vcc_create`, `vcc_release`, `vcc_connect`, `vcc_recvmsg`, `vcc_sendmsg`, `vcc_poll`, `vcc_setsockopt`, and `vcc_getsockopt`.

Control flow: `vcc_create` allocates a `struct atm_vcc` socket, initializes callbacks, QoS defaults, accounting, and flags. `vcc_connect` validates socket state and QoS, looks up or requests an ATM device, reserves a VPI/VCI with collision checks in `vcc_hash`, initializes the requested AAL, adjusts traffic parameters, and calls the driver `open` operation. Send waits for TX accounting space, allocates and fills an skb, optionally calls driver `pre_send`, and invokes driver `send`. Receive pulls datagrams from the socket queue, copies to userspace, and returns receive memory accounting unless peeking. Release closes the VCC, calls driver close and push(NULL), drains queues, drops module/device refs, and removes the socket from the hash.

State and persistence: VCCs are stored in a hash by VCI and protected by `vcc_sklist_lock`. Each VCC tracks device, VPI/VCI, QoS, flags such as `ATM_VF_READY/CLOSE/WAITING/PARTIAL`, callbacks, owner modules, and socket memory accounting. Device notifier chain state is runtime-only.

Dependencies and integration points: depends on ATM resource lookup, PVC/SVC init paths, signaling, AAL protocol initialization, socket core, usercopy, poll, module autoloading, proc/sysfs initialization, and optional backend modules such as BR2684.

Risks: VPI/VCI allocation uses static scan cursors shared across devices. VCC hash collision rules allow shared VPI/VCI only when TX/RX classes do not collide. Send/receive accounting must balance with driver callbacks. Async release removes sockets from hash while waking userspace. QoS changes after connect are intentionally constrained.

Test signals: PF_ATMPVC/PF_ATMSVC socket create/connect/release, QoS validation and change, ANY VPI/VCI allocation, reserved VCI permission checks, send blocking and `MSG_DONTWAIT`, receive `MSG_PEEK`, poll masks, device removal via `atm_dev_release_vccs`, notifier callbacks, AAL0/AAL5/AAL34 selection, and init failure unwinding across proto/PVC/SVC/proc/sysfs.
