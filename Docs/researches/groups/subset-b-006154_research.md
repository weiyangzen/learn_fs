# Research: subset-b-006154

Grouped code research for the requested ATM and BATMAN Advanced source files. Each source section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/common.h -->
# sources/distributed-fs/ceph-client/net/atm/common.h

## Purpose
`common.h` is the internal coordination header for the ATM socket core. It declares shared VCC socket operations used by both PVC and SVC protocol families, initialization/teardown hooks for ATM subcomponents, and the conditional procfs interface.

## Important APIs and Types
- Declares common socket lifecycle and data-plane functions: `vcc_create`, `vcc_release`, `vcc_connect`, `vcc_recvmsg`, `vcc_sendmsg`, `vcc_poll`, `vcc_ioctl`, `vcc_compat_ioctl`, `vcc_setsockopt`, `vcc_getsockopt`, and `vcc_process_recv_queue`.
- Declares protocol-family init/exit hooks: `atmpvc_init`, `atmpvc_exit`, `atmsvc_init`, `atmsvc_exit`, `atm_sysfs_init`, and `atm_sysfs_exit`.
- Declares procfs hooks behind `CONFIG_PROC_FS`; otherwise inline no-op versions let callers compile without procfs.
- Declares SVC-specific `svc_change_qos` and device cleanup helper `atm_dev_release_vccs`.

## Control Flow and Integration
PVC (`pvc.c`) and SVC (`svc.c`) install `proto_ops` that delegate most common behavior to the `vcc_*` functions declared here. `ioctl.c` supplies the common VCC ioctl handlers, `raw.c` supplies AAL protocol handlers consumed by `vcc_connect`, and `resources.c`/`proc.c` expose device and inspection hooks referenced by this header.

## State and Persistence
The header owns no storage. It defines access to persistent in-kernel ATM state: sockets/VCCs, registered devices, sysfs/procfs entries, and SVC signaling state. Compile-time state is represented by conditional inline no-ops for procfs.

## Dependencies
Depends on Linux socket and poll definitions (`linux/net.h`, `linux/poll.h`) and the ATM types made visible by including users. It is a private `net/atm` header, not a UAPI contract.

## Risks and Test Signals
Risks concentrate in ABI expectations: changes to prototypes ripple through PVC, SVC, raw AAL, ioctl, resource, sysfs, and procfs code. Test signals include successful builds with and without `CONFIG_PROC_FS`/`CONFIG_COMPAT`, PVC/SVC socket creation, common send/recv behavior, and module init/exit paths that call every declared initializer and cleanup function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/ioctl.c -->
# sources/distributed-fs/ceph-client/net/atm/ioctl.c

## Purpose
`ioctl.c` implements the common ATM socket ioctl dispatcher. It handles generic VCC queries, privileged signaling-daemon attachment, backend autoloading, registered backend/module ioctls, per-device ATM ioctls, and 32-bit compat translations.

## Important APIs and Functions
- `register_atm_ioctl` / `deregister_atm_ioctl`: exported registration API for backend modules such as PPPoATM and BR2684. Entries live in `ioctl_list` under `ioctl_mutex`.
- `do_vcc_ioctl`: primary dispatcher used by native and compat entry points.
- `vcc_ioctl`: native socket `proto_ops.ioctl` callback.
- `vcc_compat_ioctl`: compat callback when `CONFIG_COMPAT` is enabled.
- Compat helpers `do_atm_iobuf`, `do_atmif_sioc`, and `do_atm_ioctl` translate legacy 32-bit ioctl command numbers and pointer layouts.

## Control Flow
The dispatcher first handles socket-local commands (`SIOCOUTQ`, `SIOCINQ`, obsolete `ATM_SETSC`, and `ATMSIGD_CTRL`). `ATMSIGD_CTRL` requires both `CAP_NET_ADMIN` and `CAP_SYS_RAWIO`, rejects compat callers, then calls `sigd_attach` and marks the socket connected. Backend-setting commands request-load `pppoatm` or `br2684` based on the user-provided backend id, then fall through to registered ioctl handlers. Registered handlers are invoked under `ioctl_mutex` with `try_module_get`/`module_put`; the first response other than `-ENOIOCTLCMD` wins. If no backend handles the command, `ATM_GETNAMES` is routed to `atm_getnames`, while interface-specific commands are unpacked into `(buf, len, number)` and forwarded to `atm_dev_ioctl`.

## State and Persistence
Persistent state is the global registered ioctl handler list. User-visible effects include socket state changes for `ATMSIGD_CTRL`, possible module autoload requests, device metadata/stat changes through `atm_dev_ioctl`, and backend binding via registered handlers.

## Dependencies and Integration
Integrates with `resources.c` for device ioctls, `signaling.c` for `sigd_attach`, `pppoatm.c` through the exported registration API, module autoloading via `request_module`, Linux capability checks, and compat pointer helpers from `net/compat.h`.

## Risks and Test Signals
Main risks are user pointer handling, compat divergence, locking/module lifetime for registered handlers, and the intentionally dangerous signaling daemon pointer protocol. Test signals include native and 32-bit ioctl coverage for `ATM_GETNAMES` and `ATM_GETTYPE`, backend autoload/bind tests, permission tests for `ATMSIGD_CTRL` and admin-only device commands, and races where a backend unregisters while ioctls are in flight.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/pppoatm.c -->
# sources/distributed-fs/ceph-client/net/atm/pppoatm.c

## Purpose
`pppoatm.c` implements RFC 2364 PPP over ATM/AAL5. It binds an already connected ATM VCC to the generic PPP channel layer, installs ATM push/pop/release callbacks, encapsulates outbound PPP frames as VC-mux or LLC, and decapsulates inbound AAL5 PDUs back into PPP.

## Important APIs, Types, and Functions
- `struct pppoatm_vcc`: per-bound-VCC state containing the original ATM callbacks, encapsulation mode, PPP channel, inflight accounting, blocked bit, compression flags, and wakeup tasklet.
- `pppoatm_assign_vcc`: validates `struct atm_backend_ppp`, allocates state, registers a PPP channel, hooks the ATM VCC callbacks, takes module ownership, and replays queued receives with `vcc_process_recv_queue`.
- `pppoatm_push`: inbound ATM callback; handles VCC close notification, LLC/autodetect parsing, `atm_return`, `ppp_input`, and `ppp_input_error`.
- `pppoatm_send`: PPP `start_xmit`; applies protocol-field compression, adds LLC when needed, enforces ATM/socket readiness, accounts TX, and calls the ATM device send method.
- `pppoatm_may_send`, `pppoatm_pop`, and `pppoatm_release_cb`: flow-control loop that limits the queue to two packets and schedules `ppp_output_wakeup` from a tasklet.
- `pppoatm_ioctl`: ATM backend ioctl handler registered through `register_atm_ioctl`.

## Control Flow
Userspace issues `ATM_SETBACKEND` with `ATM_BACKEND_PPP`; `ioctl.c` may autoload the module, then the registered handler checks `CAP_NET_ADMIN`, connected socket state, and encapsulation options. On success, PPP owns the send path while ATM still owns device delivery. Outbound packets enter through the PPP channel, are optionally compressed/encapsulated, and are sent only when `atm_may_send` and the `inflight` counter permit. Completion calls the hooked ATM `pop` callback, decrements `inflight`, and wakes PPP if it was blocked. Inbound AAL5 packets enter `pppoatm_push`, are decoded by selected/autodetected encapsulation, and are delivered to `ppp_input`.

## State and Persistence
State persists in `atm_vcc->user_back`, replaced VCC callbacks, module owner, PPP channel registration, `inflight` atomic, `blocked` bit, and selected encapsulation. The special `NONE_INFLIGHT == -2` scheme allows `atomic_inc_not_zero` to enforce a maximum of two queued packets.

## Dependencies and Integration
Integrates with the ATM core callback model, the common ioctl registration list, PPP generic channel APIs, kernel tasklets, module refcounts, and `linux/atmppp.h` backend definitions.

## Risks and Test Signals
Important risks are callback restoration on close, tasklet lifetime, atomic flow-control races, skb ownership across reallocation/send failure, and incomplete RFC 2364 encapsulation-change detection noted by the file comment. Test signals include PPPoA session setup/teardown for VC and LLC modes, autodetection from LCP frames, blocked-output wakeups after ATM `pop`/`release_cb`, backend permission checks, and fault injection for `skb_realloc_headroom`, `ppp_register_channel`, and ATM send errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/pppoatm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/proc.c -->
# sources/distributed-fs/ceph-client/net/atm/proc.c

## Purpose
`proc.c` provides the ATM procfs inspection interface under `/proc/net/atm`. It lists ATM devices, PVCs, SVCs, all VCCs, and optional per-device driver proc data.

## Important APIs, Types, and Functions
- `atm_proc_init` / `atm_proc_exit`: create and remove the `/proc/net/atm` subtree and seq files.
- `atm_proc_dev_register` / `atm_proc_dev_deregister`: exported-style helpers used by `resources.c` to create per-device entries named `<type>:<number>`.
- Device seq operations use `atm_dev_seq_start`, `atm_dev_seq_next`, and `atm_dev_seq_stop` from `resources.c`.
- VCC seq traversal uses `struct vcc_state`, `vcc_seq_start`, `vcc_seq_next`, `vcc_seq_stop`, and `__vcc_walk` over `vcc_hash` under `vcc_sklist_lock`.
- Formatters `atm_dev_info`, `pvc_info`, `vcc_info`, and `svc_info` render state into seq files.

## Control Flow
Initialization creates `devices`, `pvc`, `svc`, and `vc` seq files. Device listing traverses the global `atm_devs` list under `atm_dev_mutex`. VCC listings traverse the global VCC hash table with a family filter stored as proc private data. Per-device proc entries call a driver-provided `dev->ops->proc_read`, copy one page to userspace, and advance the file position.

## State and Persistence
The proc root pointer `atm_proc_root` persists while procfs support is active. Per-device proc state is stored in `dev->proc_name` and `dev->proc_entry`. The file exposes live state only; it does not persist configuration.

## Dependencies and Integration
Depends on `resources.h` for device traversal, `common.h` for init prototypes, `signaling.h` to display SVC state involving `sigd`, Linux seq_file/proc APIs, and ATM socket/device internals.

## Risks and Test Signals
Risks include stale pointer exposure (mitigated by `%pK`), lock ordering during VCC traversal, per-device proc read length validation, and proc entry cleanup on device deregistration. Test signals are `/proc/net/atm/devices`, `pvc`, `svc`, and `vc` output under live sockets/devices, builds without `CONFIG_PROC_FS`, device register/deregister cleanup, and access checks for kernel pointer formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/protocols.h -->
# sources/distributed-fs/ceph-client/net/atm/protocols.h

## Purpose
`protocols.h` is the private declaration header for raw ATM adaptation layer initializers. It lets the common VCC connection code install the correct push/pop/send handlers for AAL0, AAL3/4, or AAL5.

## Important APIs
- `atm_init_aal0(struct atm_vcc *vcc)`: initializes raw AAL0 behavior, including the restricted send wrapper.
- `atm_init_aal34(struct atm_vcc *vcc)`: initializes raw AAL3/4 transport.
- `atm_init_aal5(struct atm_vcc *vcc)`: initializes raw AAL5 transport and is exported by `raw.c`.

## Control Flow and State
The header owns no state. Callers select one initializer after QoS/AAL negotiation; each initializer mutates the passed `atm_vcc` callback pointers.

## Dependencies and Integration
The declarations depend on `struct atm_vcc` from ATM core headers. Implementations live in `raw.c`; consumers are the common ATM VCC setup paths.

## Risks and Test Signals
The risk is callback contract drift: these functions must install complete and compatible VCC data-plane callbacks. Test signals include PVC/SVC connections using AAL0, AAL3/4, and AAL5, correct behavior with devices that provide `send_bh`, and successful builds when only raw AAL5 is used externally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/protocols.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/pvc.c -->
# sources/distributed-fs/ceph-client/net/atm/pvc.c

## Purpose
`pvc.c` implements the `PF_ATMPVC` socket family for permanent virtual circuits. It wraps common VCC operations with PVC-specific address validation and socket operation registration.

## Important APIs and Functions
- `pvc_bind` / `pvc_connect`: validate `sockaddr_atmpvc`, require QoS via `ATM_VF_HASQOS`, apply partial VPI/VCI state, and call `vcc_connect`.
- `pvc_getname`: returns the bound interface/VPI/VCI when the VCC has a device and address.
- `pvc_setsockopt` / `pvc_getsockopt`: lock the socket and delegate to common VCC options.
- `pvc_proto_ops`: socket operations table delegating release, poll, ioctl, sendmsg, and recvmsg to common functions.
- `atmpvc_init` / `atmpvc_exit`: register/unregister the protocol family.

## Control Flow
Socket creation is limited to `init_net`, assigns `pvc_proto_ops`, and calls `vcc_create` with `PF_ATMPVC`. Binding and connecting share the same path. Once QoS is configured, `vcc_connect` attaches the VCC to a device/VPI/VCI and subsequent send/receive use the common VCC data path.

## State and Persistence
PVC-specific state is stored in the underlying `atm_vcc`: selected device, VPI/VCI, QoS flags, address flag, and common socket queues. The file itself persists only the static `proto_ops` and `net_proto_family`.

## Dependencies and Integration
Depends on `common.h` for shared VCC behavior and `resources.h` for device/VCC resource context. It uses Linux socket family registration and rejects non-init network namespaces.

## Risks and Test Signals
Risks include incorrect acceptance of partial/unspecified VPI/VCI, missing socket lock coverage around shared VCC mutations, and namespace behavior. Test signals include creating `AF_ATMPVC` sockets, setting QoS before bind, bind/connect failure without QoS, `getsockname` after connect, compat/native ioctls through the PVC ops, and family unregister during module/core teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/pvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/raw.c -->
# sources/distributed-fs/ceph-client/net/atm/raw.c

## Purpose
`raw.c` installs raw AAL0, AAL3/4, and AAL5 VCC handlers. These handlers provide the default ATM data path: receive packets into the socket queue, account transmit completion, and use device send callbacks.

## Important Functions
- `atm_push_raw`: receive callback; queues non-NULL skbs to `sk_receive_queue` and signals `sk_data_ready`.
- `atm_pop_raw`: transmit-completion callback; returns TX accounting, frees the skb, and wakes writers.
- `atm_send_aal0`: AAL0 send wrapper that prevents unprivileged users from sending cells whose encoded VPI/VCI does not match the VCC.
- `atm_init_aal0`, `atm_init_aal34`, `atm_init_aal5`: set `push`, `pop`, `push_oam`, and `send` callbacks on the VCC.

## Control Flow
After VCC setup chooses an AAL, the corresponding initializer mutates the VCC callback table. Incoming packets enter `atm_push_raw` from drivers and become socket-readable data. Transmit completion enters `atm_pop_raw`, releases accounting, frees the skb, and notifies write waiters. AAL3/4 and AAL5 send directly through `dev->ops->send_bh` when available, otherwise `dev->ops->send`; AAL0 adds the capability/address check first.

## State and Persistence
The file stores no global state. Runtime state is VCC callback assignment, socket queues, skb ownership, and ATM accounting in the VCC/socket.

## Dependencies and Integration
Depends on ATM device ops, socket queues, skb APIs, capability checks, and `protocols.h` declarations. `atm_init_aal5` is exported for users outside the immediate file.

## Risks and Test Signals
Risks include skb ownership on send failures, accounting mismatch between `atm_account_tx` users and `atm_return_tx`, and AAL0 header validation with `_ANY`/`_UNSPEC` VPI/VCI. Test signals include raw AAL5 send/receive, write-space wakeups after completion, AAL0 permission rejection for mismatched cell headers, and device variants with and without `send_bh`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/raw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/resources.c -->
# sources/distributed-fs/ceph-client/net/atm/resources.c

## Purpose
`resources.c` manages registered ATM devices and device-level ioctl operations. It owns the global device list, registration/deregistration, device lookup, stats copying/zeroing, name enumeration, and procfs seq helpers.

## Important APIs and Functions
- Global state: `LIST_HEAD(atm_devs)` and `DEFINE_MUTEX(atm_dev_mutex)`.
- `atm_dev_lookup`: locked lookup by device number with refcount hold.
- `atm_dev_register`: allocates and initializes `struct atm_dev`, assigns a number, registers procfs/sysfs, and appends to `atm_devs`.
- `atm_dev_deregister`: marks removed, unlinks, releases VCCs, unregisters sysfs/procfs, and drops the registration reference.
- `atm_getnames`: implements `ATM_GETNAMES` by copying device numbers to userspace.
- `atm_dev_ioctl`: central device ioctl dispatcher for type/ESI/stats/address/loop/range/SONET and driver-specific commands.
- `atm_dev_seq_start`, `atm_dev_seq_next`, `atm_dev_seq_stop`: procfs device-list traversal under `CONFIG_PROC_FS`.

## Control Flow
Registration allocates a device with defaults (`ATM_PHY_SIG_UNKNOWN`, OC3 link rate, initialized address lists), then under `atm_dev_mutex` resolves its number, installs ops/flags/stats/refcount, registers proc and sysfs, and links the device. Deregistration sets `ATM_DF_REMOVED`, removes the list entry, releases active VCCs through `atm_dev_release_vccs`, and tears down sysfs/procfs. Ioctls first fetch the user-supplied buffer length, lookup/autoload the target device, handle core commands inline, and fall through to driver `ioctl`/`compat_ioctl` for device-specific or SONET commands.

## State and Persistence
The persistent state is the global registered device list, per-device stats, ESI, address lists, flags, link rate, proc/sysfs bindings, and device refcounts. Stats-zeroing is implemented by copying current atomics and subtracting them after a successful userspace copy.

## Dependencies and Integration
Integrates with `addr.h` address helpers, procfs hooks from `proc.c`, sysfs helpers declared in `resources.h`, device module autoloading via `try_then_request_module`, and common VCC cleanup via `atm_dev_release_vccs`.

## Risks and Test Signals
Risks include device number races, registration rollback after proc/sysfs failures, user-buffer length mistakes, admin capability enforcement, compat driver ioctl handling, and stats subtraction under concurrent updates. Test signals include registering duplicate and auto-numbered devices, `ATM_GETNAMES`, ESI set/get permission paths, address add/delete/get, stats get/zero, deregistration with open VCCs, and proc/sysfs cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/resources.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/resources.h -->
# sources/distributed-fs/ceph-client/net/atm/resources.h

## Purpose
`resources.h` declares the ATM device resource manager interface shared by the ATM core, procfs, ioctl, and sysfs code.

## Important APIs and State
- Exposes `atm_devs` and `atm_dev_mutex` for controlled traversal by procfs and related core code.
- Declares `atm_getnames` and `atm_dev_ioctl`, the device enumeration and ioctl dispatch APIs used by `ioctl.c`.
- Under `CONFIG_PROC_FS`, declares seq traversal helpers and per-device proc registration helpers. Without procfs, it provides no-op inline per-device proc hooks.
- Declares `atm_register_sysfs` and `atm_unregister_sysfs`.

## Control Flow and Integration
The header lets `resources.c` own the implementation while `proc.c` uses its seq helpers and `ioctl.c` uses its user-facing operations. The conditional procfs stubs keep device registration logic simple across builds.

## State and Persistence
The header itself owns no state, but it intentionally exposes the global ATM device list and lock. That makes lock ordering and iterator correctness important for all users.

## Dependencies
Depends on `linux/atmdev.h`, `linux/mutex.h`, and conditionally `linux/proc_fs.h`. It is an internal ATM core header.

## Risks and Test Signals
The main risk is misuse of exposed globals without `atm_dev_mutex` or mismatched procfs conditional behavior. Test signals include builds with and without `CONFIG_PROC_FS`, proc device listing while devices register/deregister, and ioctl enumeration using the declared API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/resources.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/signaling.c -->
# sources/distributed-fs/ceph-client/net/atm/signaling.c

## Purpose
`signaling.c` bridges kernel SVC sockets to a privileged userspace ATM signaling daemon (`atmsigd`). It queues requests to the daemon, receives daemon replies, updates VCC state, and purges SVCs if the daemon exits.

## Important APIs, Types, and Functions
- Global `struct atm_vcc *sigd`: current signaling daemon meta VCC.
- `sigd_attach`: attaches a privileged socket as the signaling daemon using a synthetic `sigd_dev`.
- `sigd_enq2` / `sigd_enq`: allocate `struct atmsvc_msg` skbs and enqueue requests to the daemon.
- `sigd_send`: device send callback for daemon replies; validates opaque VCC pointers via `find_get_vcc`, then handles `as_okay`, `as_error`, `as_indicate`, `as_close`, `as_modify`, `as_addparty`, and `as_dropparty`.
- `modify_qos`: invokes driver `change_qos` and reports success/failure back to the daemon.
- `sigd_close`: clears `sigd`, purges pending requests, and releases registered SVC VCCs.

## Control Flow
`ioctl.c` calls `sigd_attach` for `ATMSIGD_CTRL`. SVC operations enqueue messages with `sigd_enq*` and sleep on `ATM_VF_WAITING`. The daemon reads those skbs from its receive queue and writes replies through the synthetic device send path, which is `sigd_send`. Reply handling updates socket errors, VCC flags, local/remote/PVC/QoS fields, accept queues, or party status, then wakes waiting sockets with `sk_state_change`.

## State and Persistence
Persistent state includes the singleton daemon pointer, VCC flags (`META`, `READY`, `WAITING`, `REGIS`, `RELEASED`), socket errors, accept queues, session ids for point-to-multipoint connects, and queued `atmsvc_msg` skbs. The daemon protocol stores kernel VCC pointers as opaque tokens, which is why `sigd_send` revalidates pointers by scanning `vcc_hash`.

## Dependencies and Integration
Integrates tightly with `svc.c`, `ioctl.c`, the global VCC hash/list locks, ATM device callback semantics, and userspace atmsigd. It also calls `vcc_release_async` to tear down sockets.

## Risks and Test Signals
Risks are high because userspace carries opaque kernel pointers: privilege gating, pointer validation, socket lifetime, and reference balancing are critical. Additional risks include unbounded allocation retry loops, daemon disappearance while sockets wait, and accept queue handling for `as_indicate`. Test signals include daemon attach exclusivity, SVC bind/connect/listen/accept/release flows, daemon crash cleanup, invalid VCC pointer rejection, QoS modification replies, and add/drop party status propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/signaling.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/signaling.h -->
# sources/distributed-fs/ceph-client/net/atm/signaling.h

## Purpose
`signaling.h` declares the internal ATM SVC signaling interface between SVC sockets, common ioctl code, and the signaling daemon bridge.

## Important APIs and State
- Exposes `extern struct atm_vcc *sigd` so SVC code can detect daemon availability.
- Declares `sigd_enq2`, the full request builder for signaling messages with VCC, listen VCC, PVC/SVC addresses, QoS, and reply fields.
- Declares `sigd_enq`, a convenience wrapper for common message shapes.
- Declares `sigd_attach`, used by privileged ioctl handling to bind the daemon socket.

## Control Flow and Integration
`svc.c` calls `sigd_enq*` before sleeping on VCC flags; `ioctl.c` calls `sigd_attach` for `ATMSIGD_CTRL`; `proc.c` includes the header to inspect signaling-related state. The header formalizes the daemon queueing contract but leaves all storage and synchronization to `signaling.c`.

## State and Persistence
No local state is stored in the header. It exposes the daemon singleton and the message-enqueue API that mutates live VCC/socket state.

## Risks and Test Signals
Risks are ABI drift between message construction and daemon reply handling, and direct external checks of `sigd` racing with daemon close. Test signals include builds of all SVC/signaling/proc users, daemon attach/detach behavior, and SVC operations returning `-EUNATCH` when `sigd` is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/signaling.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/svc.c -->
# sources/distributed-fs/ceph-client/net/atm/svc.c

## Purpose
`svc.c` implements the `PF_ATMSVC` socket family for switched virtual circuits. It provides bind/connect/listen/accept, QoS changes, SVC-specific socket options, point-to-multipoint party management, and protocol family registration while delegating raw VCC data-plane behavior to common VCC functions.

## Important APIs and Functions
- `svc_bind`: binds a local ATM SVC address by asking atmsigd (`as_bind`) and waiting for a reply.
- `svc_connect`: validates QoS and remote address, sends `as_connect`, supports nonblocking `SS_CONNECTING`, handles signal abort with `as_close`, then calls `vcc_connect`.
- `svc_listen` / `svc_accept`: coordinate listen registration and incoming `as_indicate` messages through the socket receive queue and accept backlog.
- `svc_disconnect` / `svc_release`: close registered SVCs, reject queued indications, and release common VCC state.
- `svc_change_qos`: sends `as_modify` and waits for daemon/driver result.
- `svc_setsockopt` / `svc_getsockopt`: handle `SO_ATMSAP` and `SO_MULTIPOINT` before delegating common options.
- `svc_ioctl` / `svc_compat_ioctl`: implement `ATM_ADDPARTY` and `ATM_DROPPARTY`, delegate everything else to common ioctls.
- `atmsvc_init` / `atmsvc_exit`: register/unregister the family.

## Control Flow
All signaling actions set `ATM_VF_WAITING`, enqueue a message to `sigd`, and sleep until the flag clears or the daemon disappears. Connect transitions through `SS_UNCONNECTED`, optional `SS_CONNECTING`, and `SS_CONNECTED`; successful daemon replies fill PVC coordinates and QoS before `vcc_connect`. Listen sockets receive `as_indicate` skbs from `signaling.c`; accept creates a new SVC socket, copies message QoS/address/SAP, connects the new VCC, and sends `as_accept`.

## State and Persistence
Persistent state lives in `atm_vcc`: local/remote SVC addresses, SAP, QoS, VPI/VCI/interface, session/listen/bound/registered/waiting flags, and socket errors. The accept queue stores pending indication skbs that must be rejected on release. Point-to-multipoint status uses `ATM_VF_SESSION` and `sk_err_soft` for endpoint replies.

## Dependencies and Integration
Depends on `signaling.c` for daemon request/reply, `common.h` for VCC creation/data plane/options, `addr.h` for address semantics, and Linux socket locking/wait queues. It is init-net-only.

## Risks and Test Signals
Risks include sleep/wakeup races with daemon exit, signal abort cleanup in connect, accept backlog accounting, queued indication rejection on release, pointer lifetime between listen and accepted sockets, and compat ioctl command correction for `ATM_ADDPARTY`. Test signals include blocking and nonblocking connect, interrupted connect aborts, daemon absence returning `-EUNATCH`, listen backlog full rejection, accept success/failure paths, QoS modification, multipoint add/drop party, and release with pending indications.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/atm/svc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/Kconfig -->
# sources/distributed-fs/ceph-client/net/batman-adv/Kconfig

## Purpose
`Kconfig` defines the build-time feature surface for the B.A.T.M.A.N. Advanced mesh networking module and optional subfeatures.

## Important Configuration Symbols
- `BATMAN_ADV`: tristate module/core option; selects `CRC32`.
- `BATMAN_ADV_BATMAN_V`: enables BATMAN V, gated to avoid unsupported `CFG80211=m` with built-in batman-adv; default yes.
- `BATMAN_ADV_BLA`: bridge loop avoidance; depends on `INET`, selects `CRC16` and `NET_CRC32C`.
- `BATMAN_ADV_DAT`: distributed ARP table; depends on `INET`.
- `BATMAN_ADV_MCAST`: multicast optimization; depends on `INET` and avoids built-in/module bridge mismatch.
- `BATMAN_ADV_DEBUG` and `BATMAN_ADV_TRACING`: developer logging and trace integration.

## Control Flow and Integration
These options control which objects the Makefile includes and which inline stubs are active in headers like `bat_v.h`. The BATMAN V option directly controls inclusion of `bat_v.c`, `bat_v_elp.c`, and `bat_v_ogm.c`.

## State and Persistence
Kconfig stores compile-time decisions only. Runtime persistence is affected indirectly by whether optional protocol state exists in compiled code.

## Dependencies
Uses kernel networking and tracing dependency symbols. The CFG80211 and BRIDGE constraints prevent invalid built-in/module link combinations.

## Risks and Test Signals
Risks are bad dependency expressions causing link failures or unavailable runtime features despite selected config. Test signals include allmodconfig/allyesconfig, `BATMAN_ADV=y` with `CFG80211=m`, `BATMAN_ADV=y` with `BRIDGE=m`, minimal `BATMAN_ADV` without optional features, and trace/debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/Makefile -->
# sources/distributed-fs/ceph-client/net/batman-adv/Makefile

## Purpose
The Makefile assembles the `batman-adv.o` composite object from mandatory routing/core objects and optional feature objects controlled by Kconfig.

## Important Build Rules
- `obj-$(CONFIG_BATMAN_ADV) += batman-adv.o` builds the module/built-in object.
- Mandatory objects include `bat_algo.o`, `bat_iv_ogm.o`, `bitarray.o`, fragmentation, gateway, hard-interface, hash, main, mesh-interface, netlink, originator, routing, send, tp_meter, translation-table, and tvlv.
- BATMAN V objects are conditional on `CONFIG_BATMAN_ADV_BATMAN_V`: `bat_v.o`, `bat_v_elp.o`, `bat_v_ogm.o`.
- Optional feature objects are gated for BLA, DAT, DEBUG, MCAST, and TRACING.
- `CFLAGS_trace.o := -I$(src)` ensures trace compilation can include local generated/source headers.

## Control Flow and Integration
The object list must match Kconfig and header stubs. For example, `bat_v.h` provides no-op helpers when BATMAN V objects are omitted, while BATMAN IV remains mandatory and registers the default routing algorithm.

## State and Persistence
No runtime state is stored here. Build composition determines which runtime algorithms, packet handlers, netlink/debug paths, and optimizations exist.

## Risks and Test Signals
Risks include missing objects for symbols referenced from always-built code, optional-object ordering issues, and feature symbols not matching Kconfig guards. Test signals include building with each optional feature toggled, `CONFIG_BATMAN_ADV_BATMAN_V=n`, tracing builds, and module link checks for unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_algo.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/bat_algo.c

## Purpose
`bat_algo.c` manages routing algorithm registration, selection, module parameter validation, and generic netlink dumping of supported algorithms.

## Important APIs and Functions
- Global `batadv_routing_algo[20] = "BATMAN_IV"`: module parameter backing store and default algorithm name.
- `batadv_algo_init`: initializes the algorithm hlist.
- `batadv_algo_get`: searches registered `struct batadv_algo_ops` by name.
- `batadv_algo_register`: rejects duplicate names and validates required callbacks before inserting an algorithm.
- `batadv_algo_select`: assigns a registered algorithm to a mesh interface; intended only during mesh creation.
- `batadv_param_set_ra`: validates module parameter writes against registered algorithms.
- `batadv_algo_dump`: emits registered algorithm names through generic netlink.

## Control Flow
Subsystem init initializes the list, then algorithm implementations register themselves (`BATMAN_IV`, optionally `BATMAN_V`). Module parameter writes strip a trailing newline, verify the algorithm exists, and update `batadv_routing_algo`. Mesh creation calls `batadv_algo_select` to set `bat_priv->algo_ops`. Netlink dump walks the hlist using `cb->args[0]` as the skip cursor.

## State and Persistence
State persists in the global algorithm list and the routing algorithm module parameter. Per-mesh state is a pointer to selected `algo_ops`; this file explicitly does not deinitialize an old algorithm when selecting a new one.

## Dependencies and Integration
Depends on `struct batadv_algo_ops` from `main.h`, netlink family definitions, and algorithm providers in `bat_iv_ogm.c` and `bat_v.c`.

## Risks and Test Signals
Risks include registering incomplete algorithm ops, changing selection after mesh initialization, module parameter ordering before optional algorithm registration, and netlink dump truncation/cursor handling. Test signals include module parameter validation for `BATMAN_IV`/`BATMAN_V`/invalid names, duplicate registration failure, netlink algorithm dump with small skb, and mesh creation selecting configured algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_algo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_algo.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/bat_algo.h

## Purpose
`bat_algo.h` declares the routing algorithm management API used by batman-adv core code, netlink, and algorithm providers.

## Important APIs
- Exposes `batadv_routing_algo` module parameter storage.
- Declares initialization, lookup, registration, mesh selection, and netlink dump functions.

## Control Flow and Integration
Core initialization calls `batadv_algo_init`; algorithm implementations call `batadv_algo_register`; mesh-interface setup calls `batadv_algo_select`; netlink code calls `batadv_algo_dump`.

## State and Persistence
No state is stored in the header, but it exposes the global selected-name buffer and the registration API that populates the algorithm list.

## Risks and Test Signals
Risks are API signature drift with `bat_algo.c` and unintended external mutation of `batadv_routing_algo`. Test signals are compile coverage for BATMAN IV-only and BATMAN V-enabled builds, plus netlink routing algorithm dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_algo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_iv_ogm.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/bat_iv_ogm.c

## Purpose
`bat_iv_ogm.c` implements the BATMAN IV routing algorithm. It generates and forwards OGMv1 packets, computes transmission quality (TQ), maintains sequence-number windows, updates originator routes, provides neighbor/originator/gateway netlink dumps, and registers the `BATMAN_IV` algorithm.

## Important APIs, Types, and Functions
- `enum batadv_dup_status`: classifies OGM sequence handling as no duplicate, originator duplicate, neighbor duplicate, or protected.
- Interface ops: `batadv_iv_ogm_iface_enable`, `batadv_iv_ogm_iface_disable`, `batadv_iv_ogm_iface_update_mac`, `batadv_iv_ogm_primary_iface_set`, and `batadv_iv_iface_enabled`.
- OGM scheduling/forwarding: `batadv_iv_ogm_schedule_buff`, `batadv_iv_ogm_queue_add`, aggregation helpers, `batadv_iv_send_outstanding_bat_ogm_packet`, and `batadv_iv_ogm_receive`.
- Metric/routing: `batadv_iv_ogm_update_seqnos`, `batadv_iv_ogm_calc_tq`, `batadv_iv_ogm_orig_update`, and `batadv_iv_ogm_process_per_outif`.
- Netlink/gateway callbacks: neighbor/originator dump functions, `batadv_iv_gw_get_best_gw_node`, `batadv_iv_gw_is_eligible`, and `batadv_iv_gw_dump`.
- `batadv_iv_init`: registers the OGM packet handler and the algorithm ops.

## Control Flow
Enabling a hard interface allocates an OGM template, randomizes its sequence number, and initializes packet fields. The enabled callback starts periodic OGM scheduling. Primary-interface OGMs commit TT changes, append TVLVs, increment seqno, slide own broadcast windows, and queue cloned packets to all active lower interfaces; secondary OGMs are sent only on their own interface. Received OGM aggregates are unpacked and processed first for the default originator table and then for each active outgoing interface. Processing rejects self/echo/not-best packets, updates duplicate windows, computes bidirectional TQ from own rebroadcast counts and neighbor receive counts, updates routes when a neighbor is better, handles TVLVs, and forwards eligible packets with TTL and hop penalty adjustments.

## State and Persistence
State persists in per-hard-interface `bat_iv` OGM buffers, sequence atomics, mutexes, forward queues, per-originator `bat_iv` counters, per-originator-interface broadcast windows and last seqno/TTL, per-neighbor-interface TQ ring buffers and averages, gateway selection class, and the global receive handler/algorithm registration.

## Dependencies and Integration
Integrates with originator hash management, route updates, hard-interface state, `bitarray.c` sequence windows, send/forward queues, TVLV and translation-table code, gateway client code, generic netlink, workqueues, RCU, krefs, and debug logging.

## Risks and Test Signals
Risks include sequence-window protection around reboots, aggregation bounds, skb clone/copy ownership, route flapping from TQ ties, lock ordering across RCU/spinlocks/mutexes, forwarding loops, and per-interface state cleanup. Test signals include OGM send/receive counters, route convergence in multi-hop topologies, duplicate/reordered/old sequence injection, TVLV propagation, gateway reselection by TQ, aggregation on/off, interface activation/removal, and netlink dumps for neighbors/originators/gateways under small skb cursors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_iv_ogm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_iv_ogm.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/bat_iv_ogm.h

## Purpose
`bat_iv_ogm.h` exposes the BATMAN IV initialization entry point to the batman-adv core.

## Important API
- `batadv_iv_init(void)`: registers the BATMAN IV OGM receive handler and `BATMAN_IV` algorithm operations.

## Control Flow and Integration
Module initialization calls this header's single exported declaration. All other BATMAN IV implementation details remain private to `bat_iv_ogm.c`.

## State and Persistence
The header owns no state. Runtime state begins when `batadv_iv_init` registers handlers and algorithm ops.

## Risks and Test Signals
Risk is minimal and centers on init signature drift. Test signals include successful core initialization and BATMAN IV packet handler registration in builds with and without BATMAN V.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_iv_ogm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_v.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/bat_v.c

## Purpose
`bat_v.c` registers and coordinates the BATMAN V routing algorithm. It wires together ELP neighbor discovery, OGMv2 route propagation, throughput-based neighbor comparison, originator/neighbor/gateway netlink dumps, and per-hard-interface/mesh initialization.

## Important APIs and Functions
- Interface ops: `batadv_v_iface_activate`, `batadv_v_iface_enable`, `batadv_v_iface_disable`, `batadv_v_primary_iface_set`, and `batadv_v_iface_update_mac`.
- Neighbor ops: `batadv_v_hardif_neigh_init`, `batadv_v_neigh_cmp`, `batadv_v_neigh_is_sob`, and netlink neighbor dump helpers.
- Originator/gateway dumps and selection: `batadv_v_orig_dump`, `batadv_v_gw_get_best_gw_node`, `batadv_v_gw_is_eligible`, `batadv_v_gw_dump`.
- Lifecycle exports: `batadv_v_hardif_init`, `batadv_v_mesh_init`, `batadv_v_mesh_free`, and `batadv_v_init`.
- Static `batadv_batman_v` defines the algorithm callbacks registered with `batadv_algo_register`.

## Control Flow
Module init registers receive handlers for ELP and OGM2 before registering the algorithm. Hard-interface init sets throughput override to auto, default ELP interval to 500 ms, initializes aggregation queue state, and sets up the OGM aggregation delayed work. Enabling an interface starts ELP then OGMv2; failure rolls back ELP. Activation updates ELP originator fields from the selected primary interface and can mark the interface active immediately because BATMAN V has no BATMAN IV-style forward queue activation hazard. Mesh init/free allocate and release OGMv2 mesh resources through `bat_v_ogm.c`.

## State and Persistence
Persistent BATMAN V state includes per-hard-interface throughput override, ELP interval, ELP/OGM work items, OGM aggregation queue and length, per-neighbor EWMA throughput, per-neighbor-interface path throughput, gateway selection class, and per-mesh OGMv2 buffer state.

## Dependencies and Integration
Integrates with `bat_v_elp.c`, `bat_v_ogm.c`, algorithm registration, hard-interface/originator/gateway subsystems, generic netlink, and Kconfig guards through `bat_v.h`.

## Risks and Test Signals
Risks include inconsistent initialization order between ELP and OGMv2, stale primary MAC in protocol packets, throughput comparison overflow/units, gateway reselection threshold behavior, and dump cursor handling. Test signals include BATMAN V registration only when configured, interface enable rollback on ELP/OGM failure, throughput-visible neighbor/originator/gateway netlink dumps, gateway selection by effective throughput, and BATMAN V disabled builds using stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_v.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/bat_v.h

## Purpose
`bat_v.h` declares BATMAN V lifecycle hooks and provides no-op stubs when `CONFIG_BATMAN_ADV_BATMAN_V` is disabled.

## Important APIs
- Enabled builds declare `batadv_v_init`, `batadv_v_hardif_init`, `batadv_v_mesh_init`, and `batadv_v_mesh_free`.
- Disabled builds inline all four functions as harmless no-ops or success returns.

## Control Flow and Integration
Always-built core code can call BATMAN V setup functions unconditionally. Kconfig and Makefile decide whether real implementations from `bat_v.c` are linked or the inline stubs are used.

## State and Persistence
No header-local state. The stubs ensure no BATMAN V state is initialized when the feature is disabled.

## Risks and Test Signals
Risks are mismatches between conditional declarations and Makefile object inclusion. Test signals include builds with `CONFIG_BATMAN_ADV_BATMAN_V=y` and `n`, and runtime confirmation that `BATMAN_V` is absent from routing algorithm dumps when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_v.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_v_elp.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/bat_v_elp.c

## Purpose
`bat_v_elp.c` implements BATMAN V Echo Location Protocol. ELP discovers one-hop neighbors, sends periodic broadcast probes, optionally sends WiFi unicast probes to feed rate control, and updates per-neighbor throughput estimates used by OGMv2 routing.

## Important APIs, Types, and Functions
- `struct batadv_v_metric_queue_entry`: temporary list item for neighbor throughput updates outside RCU.
- `batadv_v_elp_iface_enable` / `batadv_v_elp_iface_disable`: allocate/free the per-interface ELP skb and start/cancel periodic work.
- `batadv_v_elp_iface_activate` and `batadv_v_elp_primary_iface_set`: keep ELP originator MAC aligned with the primary interface.
- `batadv_v_elp_periodic_work`: sends broadcast ELPs, probes neighbors, queues metric updates, and reschedules itself.
- `batadv_v_elp_get_throughput`: obtains throughput from user override, cfg80211 station data, ethtool link settings, or default fallback.
- `batadv_v_elp_packet_recv`: validates incoming ELPs and updates neighbor state via `batadv_v_elp_neigh_update`.

## Control Flow
Interface enable allocates an ELP template skb, randomizes ELP seqno, initializes duplex/default-warning flags, and starts a jittered periodic timer. The periodic worker skips inactive/removing/deactivating interfaces, clones and broadcasts the ELP skb with current seqno/interval, increments seqno, probes WiFi neighbors if recent unicast traffic is insufficient, then updates throughput metrics outside RCU because cfg80211/ethtool paths may sleep. Receive handling drops malformed/self/wrong-algorithm packets, requires a selected primary interface, creates/updates originator, neighbor, and hardif-neighbor records, and ignores old ELP seqnos unless the peer appears restarted.

## State and Persistence
State persists in per-hard-interface ELP skb, ELP seqno, interval, flags (`FULL_DUPLEX`, default-warning), neighbor latest seqno/interval, neighbor `last_seen`, and EWMA throughput.

## Dependencies and Integration
Integrates with BATMAN V OGM originator creation, hard-interface neighbor tables, cfg80211, ethtool, RTNL locking, workqueues, send helpers, route/originator state, and debug logging.

## Risks and Test Signals
Risks include RTNL deadlock avoidance (`rtnl_trylock`), stale/missing throughput data, default throughput warning behavior, WiFi probe allocation, RCU-to-sleeping context handoff, and old sequence acceptance after restart. Test signals include ELP broadcast cadence, neighbor discovery before OGM acceptance, throughput override, cfg80211 expected throughput path, ethtool full/half-duplex detection, default fallback warning once per enable, and cleanup canceling delayed work and freeing skb.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_v_elp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_v_elp.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/bat_v_elp.h

## Purpose
`bat_v_elp.h` declares the BATMAN V ELP interface lifecycle, primary-interface update, and packet receive API.

## Important APIs
- `batadv_v_elp_iface_enable` / `batadv_v_elp_iface_disable`
- `batadv_v_elp_iface_activate`
- `batadv_v_elp_primary_iface_set`
- `batadv_v_elp_packet_recv`

## Control Flow and Integration
`bat_v.c` calls the enable/disable/activate/primary hooks as part of algorithm interface ops. `batadv_v_init` registers `batadv_v_elp_packet_recv` as the handler for ELP packets.

## State and Persistence
No state is stored in the header; it exposes functions that mutate per-interface ELP state in `struct batadv_hard_iface`.

## Risks and Test Signals
Risks are signature drift with `bat_v_elp.c` and wrong call ordering from `bat_v.c`. Test signals include BATMAN V interface enable/disable and incoming ELP packet registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_v_elp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_v_ogm.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/bat_v_ogm.c

## Purpose
`bat_v_ogm.c` implements BATMAN V OGMv2 generation, aggregation, receive processing, throughput metric propagation, route updates, forwarding, and per-mesh OGMv2 resource management.

## Important APIs and Functions
- `batadv_v_ogm_orig_get`: retrieve or create originator entries.
- Mesh lifecycle: `batadv_v_ogm_init` and `batadv_v_ogm_free`.
- Interface lifecycle: `batadv_v_ogm_iface_enable`, `batadv_v_ogm_iface_disable`, `batadv_v_ogm_primary_iface_set`.
- Timers/work: `batadv_v_ogm_start_timer`, `batadv_v_ogm_send`, `batadv_v_ogm_aggr_work`, and queue timer helpers.
- Aggregation: `batadv_v_ogm_queue_on_if`, `batadv_v_ogm_aggr_send`, `batadv_v_ogm_aggr_list_free`, `batadv_v_ogm_len`, and `batadv_v_ogm_aggr_packet`.
- Routing: `batadv_v_forward_penalty`, `batadv_v_ogm_metric_update`, `batadv_v_ogm_route_update`, `batadv_v_ogm_forward`, and `batadv_v_ogm_process`.
- `batadv_v_ogm_packet_recv`: registered packet handler for OGM2.

## Control Flow
Mesh init allocates an OGM2 template with max throughput, TTL, version, random sequence number, delayed work, and mutex. Periodic send commits TT changes, appends TVLVs, stamps seqno/tvlv length, clones the skb to active lower interfaces, suppresses pointless broadcasts, and queues or sends per aggregation policy. Aggregation queues are flushed periodically or when a new packet would exceed MTU/aggregation byte limits. Receive validates algorithm and management packet shape, drops self-sourced frames, unpacks aggregates, and processes each OGM. Processing requires prior ELP neighbor discovery, creates originator/neighbor records, clamps advertised path throughput to the one-hop ELP throughput, updates default and per-outgoing-interface metrics, processes TVLVs for new default-table OGMs, updates routes when the neighbor is better or sufficiently newer, and forwards only from the best next hop.

## State and Persistence
State persists in the per-mesh OGM buffer/length/seqno/work/mutex, per-hard-interface aggregation queues and lengths, originator ifinfo last real/forwarded seqnos and TTL, neighbor ifinfo throughput and last seqno, hardif-neighbor ELP throughput, and route table next-hop selections.

## Dependencies and Integration
Depends on ELP-discovered hardif neighbors, originator hash, route update helpers, hard-interface broadcast suppression, TT/TVLV subsystems, workqueues, skb aggregation, RCU/krefs, and BATMAN V algorithm registration in `bat_v.c`.

## Risks and Test Signals
Risks include accepting OGMs before ELP state exists, aggregation length parsing, mutable skb data during per-aggregate processing, sequence reboot protection, forwarding loops, best-next-hop strictness, throughput unit/penalty errors, and cleanup of delayed work/queued skbs. Test signals include OGM2 send cadence, aggregation enabled/disabled, TVLV propagation, route convergence by throughput, suppression cases from `batadv_hardif_no_broadcast`, ELP-missing OGM drops, old/restarted sequence injection, and mesh/interface teardown with no delayed work leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_v_ogm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_v_ogm.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/bat_v_ogm.h

## Purpose
`bat_v_ogm.h` declares the BATMAN V OGMv2 APIs shared between `bat_v.c`, `bat_v_elp.c`, and the OGMv2 implementation.

## Important APIs
- Mesh lifecycle: `batadv_v_ogm_init`, `batadv_v_ogm_free`.
- Interface/aggregation lifecycle: `batadv_v_ogm_aggr_work`, `batadv_v_ogm_iface_enable`, `batadv_v_ogm_iface_disable`.
- Originator helper: `batadv_v_ogm_orig_get`, used by ELP and OGMv2 receive paths.
- Primary-interface update: `batadv_v_ogm_primary_iface_set`.
- Packet receive: `batadv_v_ogm_packet_recv`.

## Control Flow and Integration
`bat_v.c` calls lifecycle and primary hooks; `bat_v_elp.c` calls originator creation when an ELP names a peer originator; packet registration uses `batadv_v_ogm_packet_recv` for `BATADV_OGM2`.

## State and Persistence
No header-local state. Declared functions mutate per-mesh OGMv2 state, per-interface aggregation state, and originator tables.

## Risks and Test Signals
Risks are declaration/implementation drift and misuse of originator helper without reference release. Test signals include BATMAN V mesh init/free, ELP neighbor creation, OGM2 receive handler registration, and teardown with aggregation work canceled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bat_v_ogm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bitarray.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/bitarray.c

## Purpose
`bitarray.c` implements sequence-number receive-window movement for BATMAN IV. It tracks which recent OGMs were seen so duplicate detection and packet-count-based TQ calculations can work.

## Important Functions
- `batadv_bitmap_shift_left`: shifts a bitmap by a positive in-window delta.
- `batadv_bit_get_packet`: updates a sequence bitmap based on `seq_num_diff` and optionally marks the received packet.

## Control Flow
Slightly older packets within the local window are marked without moving the window. Slightly newer packets shift the window and mark bit zero. Much newer packets clear the window, log missed packets, and mark the new head. Much older packets or values outside expected range are treated as likely peer restart: the window is cleared and the new packet can be marked.

## State and Persistence
The file owns no global state. It mutates caller-owned bitmaps, typically per-neighbor/per-originator BATMAN IV receive windows. Debug logging uses the passed `bat_priv`.

## Dependencies and Integration
Used heavily by `bat_iv_ogm.c` for real receive windows and own-broadcast windows. Depends on bitmap helpers, BATMAN window constants, and debug logging.

## Risks and Test Signals
Risks include signed sequence-difference wrap behavior, off-by-one window shifts, and restart/missed-packet classification. Test signals include unit-style checks for older/newer/much-newer/much-older diffs, duplicate detection through `batadv_test_bit`, and BATMAN IV route behavior under reordered or skipped OGMs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bitarray.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bitarray.h -->
# sources/distributed-fs/ceph-client/net/batman-adv/bitarray.h

## Purpose
`bitarray.h` declares and partly implements bitmap helpers for BATMAN IV sequence tracking.

## Important APIs
- `batadv_test_bit`: returns whether `curr_seqno` is present in a receive window anchored at `last_seqno`, rejecting future or too-old values.
- `batadv_set_bit`: marks a relative sequence position if it is inside the local window.
- `batadv_bit_get_packet`: declared implementation for moving/marking windows.

## Control Flow and State
The inline helpers operate on caller-owned `unsigned long` bitmaps. They use signed differences to map sequence numbers to bit positions and silently ignore invalid relative positions.

## Dependencies and Integration
Used by BATMAN IV OGM duplicate detection and TQ packet-count logic. Depends on `BATADV_TQ_LOCAL_WINDOW_SIZE`, Linux bitops, and integer types.

## Risks and Test Signals
Risks include wraparound semantics and callers passing unprotected bitmaps without the relevant originator lock. Test signals include boundary tests for diff `-1`, `0`, `BATADV_TQ_LOCAL_WINDOW_SIZE - 1`, and out-of-window values, plus BATMAN IV duplicate suppression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/bitarray.h -->
