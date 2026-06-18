# Group Research: group_1356_open_iscsi_sources_virtualization_open_iscsi_usr_Makefile_sources_v_e8e3995d4fa6

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/Makefile -->
# File Research: sources/virtualization/open-iscsi/usr/Makefile

Builds the open-iscsi user tools `iscsid`, `iscsiadm`, and `iscsistart`. It selects Linux netlink IPC versus FreeBSD ioctl support, derives kernel netlink constants from `KSRC`, and injects database/config roots via `ISCSI_DB_ROOT` and `ISCSI_CONFIG_ROOT`.

The Makefile links a broad shared object set covering authentication, discovery, sysfs, transport helpers, flashnode, IPC, login, and firmware boot objects from `fwparam_ibft/`. `iscsid` additionally includes initiator/event-management objects and discovery daemon support; `iscsiadm` includes administrative discovery/session management; `iscsistart` includes early boot/login pieces.

Dependencies include `libopeniscsiusr`, `libkmod`, optional `libsystemd`, `libisns`, OpenSSL crypto, realtime, and mount libraries. The `FW_BOOT_OBJS` target delegates into `usr/fwparam_ibft`.

Notable risks: kernel version parsing assumes `$(KSRC)/Makefile` is readable and uses `SUBLEVEL`; `WARNFLAGS` includes `-Werror`, making toolchain/header drift build-breaking; `NO_SYSTEMD` only controls systemd flags, while iSNS is always enabled by `-DISNS_SUPPORTED` and link `-lisns` in this make path.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/actor.c -->
# File Research: sources/virtualization/open-iscsi/usr/actor.c

Implements a single-threaded deferred-work scheduler used by `iscsid`. It keeps two global lists: `pend_list` for delayed actors sorted by monotonic due time, and `ready_list` for runnable actors.

Core APIs initialize actors, schedule immediately at head/tail, schedule timers, modify timers, delete pending actors, and poll runnable work. Delayed scheduling uses `clock_gettime(CLOCK_MONOTONIC_COARSE)` plus process `alarm()`; the event loop receives `SIGALRM` through `signalfd` and calls `actor_poll()`.

`actor_poll()` moves expired pending entries to ready, rearms `alarm()` for the next pending actor, then executes callbacks until `ready_list` is empty. A `poll_in_progress` guard logs and ignores recursive polling.

Important invariants: actors move through `ACTOR_INVALID`, `ACTOR_NOTSCHEDULED`, `ACTOR_WAITING`, and `ACTOR_SCHEDULED`; callbacks run after state resets to not scheduled. The design assumes one event-loop thread and no locking. Deleting the first pending timer has a TODO for precise alarm reset, so delete/reschedule timing behavior depends on later `actor_poll()` calls.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/actor.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/actor.h -->
# File Research: sources/virtualization/open-iscsi/usr/actor.h

Declares the usermode actor scheduler interface and `actor_t` structure. Each actor stores a debug name, list linkage, current state, opaque callback data, callback function, and scheduled monotonic timestamp.

Exports initialization, deletion, immediate scheduling, delayed timer creation/modification, and polling. The `actor_init` and `actor_timer` macros populate the actor name from the callback symbol before calling the internal implementations.

This header is tightly coupled to `list.h`, `types.h`, and the single-threaded event-loop model in `event_poll.c`. Consumers must keep `actor_t` storage valid until callbacks are complete and should not call `actor_poll()` recursively.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/actor.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/auth.c -->
# File Research: sources/virtualization/open-iscsi/usr/auth.c

Implements iSCSI security negotiation and CHAP authentication for initiator and target roles. It manages AuthMethod, CHAP_A, CHAP_N, CHAP_R, CHAP_I, and CHAP_C keys using receive/send key blocks and a phase/state machine.

The main flow is `acl_recv_begin()` -> repeated `acl_recv_key_value()` / `acl_recv_transit_bit()` -> `acl_recv_end()` -> `acl_send_key_val()` / `acl_send_transit_bit()`. `acl_recv_end()` negotiates AuthMethod, runs local CHAP response generation, optionally challenges/authenticates the remote peer, enforces transit-bit sequencing, and returns pass/fail/continue status.

CHAP digest computation uses OpenSSL EVP for MD5, SHA1, SHA256, and optional SHA3-256. Challenges and identifiers are generated with `RAND_bytes()`. Binary CHAP fields are encoded/decoded as `0x` hex or `0b` base64-like text. `acl_init_chap_digests()` filters configured algorithms against what the crypto library actually permits.

Security behavior includes rejecting missing/duplicate/too-long keys, rejecting reflected challenges for target role, failing if local secrets are absent, enforcing a minimum 12-byte password when not authenticating the remote side and not using IPsec, and detecting identical local/remote CHAP passwords. Remote target authentication delegates expected incoming credentials to `session->username_in` and `session->password_in`.

State is stored in caller-provided buffers registered by `acl_init()`: the ACL object, receive/send string blocks, and receive/send large-binary challenge buffers. `acl_finish()` zeroes the ACL structure but not the separately supplied buffers. The module assumes one thread per ACL object and no locking.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/auth.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/auth.h -->
# File Research: sources/virtualization/open-iscsi/usr/auth.h

Defines the public authentication model for `auth.c`. It declares string/binary limits, CHAP response sizes, key IDs, option constants, roles, status codes, debug statuses, node types, phases, and local/remote CHAP state enums.

The central structure is `struct iscsi_acl`, which stores configured methods, CHAP algorithm lists, usernames/passwords, negotiated method/algorithm, current phase, debug status, key blocks, challenge buffers, and a session handle used for target authentication callbacks.

Exports ACL lifecycle, receive/send key APIs, transit-bit APIs, configuration setters, debug-status helpers, CHAP digest computation, target authentication request handling, and `acl_data()` password copy/decrypt shim. The enum ordering comments are important because text lookup tables in `auth.c` depend on matching order.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/auth.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/be2iscsi.c -->
# File Research: sources/virtualization/open-iscsi/usr/be2iscsi.c

Provides transport-specific connection adjustment for the `be2iscsi` offload driver. `be2iscsi_create_conn()` clamps negotiated data lengths and burst sizes to adapter limits, forces ERL 0, and enables InitialR2T.

It mutates `struct iscsi_conn` and its parent session directly. The helper is intentionally small and is likely called from transport setup code before creating or binding the connection.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/be2iscsi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/be2iscsi.h -->
# File Research: sources/virtualization/open-iscsi/usr/be2iscsi.h

Declares the `be2iscsi_create_conn(struct iscsi_conn *)` transport helper with a forward declaration for `struct iscsi_conn`. It is a narrow include guard wrapper for the implementation in `be2iscsi.c`.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/be2iscsi.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/config.h -->
# File Research: sources/virtualization/open-iscsi/usr/config.h

Defines the primary persistent/runtime configuration record types used by open-iscsi user tools. It groups authentication, connection timeouts, session timeouts, error timeouts, TCP options, connection operational parameters, session operational parameters, SendTargets discovery options, and iSNS discovery options.

Important top-level records are `conn_rec_t`, `session_rec_t`, `iface_rec_t`, `node_rec_t`, and `discovery_rec_t`. `node_rec_t` combines target identity, startup policy, one connection, interface binding, and discovery provenance. `iface_rec_t` is large and stores software/offload network, VLAN, IPv4/IPv6, TCP, digest, CHAP, discovery, and boot identity settings.

Enums define startup mode and discovery type, including SendTargets, iSNS, offload SendTargets, static, and firmware discovery. Constants set ISID OUI bytes, one connection per session, interface string limits, transport name length, and digest preference values.

This header is a shared schema layer for IDBM persistence, discovery, login setup, firmware boot conversion, and flashnode handling. Changes have broad compatibility impact because many modules copy or serialize these structs.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/config.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/cxgbi.c -->
# File Research: sources/virtualization/open-iscsi/usr/cxgbi.c

Provides a Chelsio `cxgb3i/cxgb4i` transport helper. `cxgbi_create_conn()` clamps `conn->max_recv_dlength` to 8192 bytes despite a comment noting the card can handle up to 15360 bytes.

The helper directly mutates the connection before use by the initiator/transport setup path.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/cxgbi.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/cxgbi.h -->
# File Research: sources/virtualization/open-iscsi/usr/cxgbi.h

Declares `cxgbi_create_conn(struct iscsi_conn *)` behind a simple include guard. It forward declares `struct iscsi_conn` and leaves all transport details to `cxgbi.c`.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/cxgbi.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/discovery.c -->
# File Research: sources/virtualization/open-iscsi/usr/discovery.c

Implements iSCSI discovery methods: iSNS discovery, firmware discovery, offload SendTargets requests, and software/kernel-assisted SendTargets. It converts discovery results into `node_rec_t` entries for later login/session management.

iSNS support builds libisns queries, optionally registers the initiator when the server requires it, extracts portal group objects, normalizes IPv4-mapped IPv6 addresses, and appends discovered target records. Firmware discovery calls `fw_get_targets()` and converts boot contexts through IDBM helpers. Offload SendTargets sends a management IPC command to `iscsid` with a resolved discovery address.

Software SendTargets creates a discovery session, logs in, sends `SendTargets=All` text PDUs, handles continuation with target transfer tags, buffers partial text data across PDUs, and emits complete target records. Address parsing supports IPv4, bracketed IPv6, DNS names, optional port, and optional portal group tag. Discovery session setup handles software transports without kernel text negotiation as well as kernel/offload transports with endpoint creation, session/connection creation, binding, parameter programming, login offload polling, redirects, retries, and cleanup.

Key dependencies include IDBM defaults/binding, iface records, sysfs transport lookup, IPC netlink operations, login/auth setup, timers, string buffers, and firmware boot context. Error paths return open-iscsi error codes and usually log portal-specific context.

Risk areas: SendTargets address parsing mutates response text in place; reconnection loops rely on `reopen_cnt`; global `initiator_name`/`initiator_alias` make this code unsuitable for concurrent independent discovery sessions; offload SendTargets does not retrieve discovered records and only asks the daemon/driver to act.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/discovery.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/discovery.h -->
# File Research: sources/virtualization/open-iscsi/usr/discovery.h

Declares the discovery entry points for iSNS, firmware, software SendTargets, and offload SendTargets. iSNS declarations are gated by `ISNS_SUPPORTED`.

The functions operate on `discovery_rec`, `iface_rec`, `node_rec`, `boot_context`, and `list_head` abstractions without including their full definitions. This keeps the header light while exposing discovery methods to `iscsiadm`, `iscsid`, and discovery daemon code.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/discovery.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/discoveryd.c -->
# File Research: sources/virtualization/open-iscsi/usr/discoveryd.c

Implements the background discovery daemon behavior for SendTargets polling and iSNS SCN/polling. It forks helper processes for configured discovery records, tracks those child PIDs for shutdown, and reconciles discovered portals against active sessions.

`update_sessions()` is the core reconciliation routine: it marks previously known targets stale when absent from new discovery results, logs into newly discovered portals if no session is running, preserves known targets, and logs out stale portals. `discoveryd_stop()` optionally logs out tracked targets when the daemon is stopping.

For SendTargets, the daemon repeatedly binds configured ifaces to discovery results and updates sessions at a configured poll interval. For iSNS, it builds initiator source nodes, registers entities/portals/storage nodes, handles registration refresh by EID query or rediscovery, registers for SCNs, receives SCN messages, and triggers targeted rediscovery on notifications.

The daemon uses `fork()`, `SIGTERM`, `reap_inc()`, and `shutdown_callback()` to integrate child lifecycle with the main event loop. It relies heavily on IDBM iteration over configured discovery records and iface binding.

Risk areas: much iSNS state is global (`isns_initiators`, `isns_refresh_list`, `isns_entity_id`, refresh interval flags), so helpers are process-isolated rather than thread-safe; polling helpers intentionally set `reopen_max = 0` and rely on the next poll for retry; list ownership transfers in `update_sessions()` require callers not to reuse records after the call.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/discoveryd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/discoveryd.h -->
# File Research: sources/virtualization/open-iscsi/usr/discoveryd.h

Declares `discoveryd_start(const char *def_iname)`, the entry point that starts configured background discovery helpers. The header is minimal and only exposes daemon startup to the rest of `iscsid`.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/discoveryd.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/ethtool-copy.h -->
# File Research: sources/virtualization/open-iscsi/usr/ethtool-copy.h

A local copy of Linux `ethtool.h` ABI definitions. It defines ethtool command structures, command IDs, advertised/supported link-mode bits, flow classification structs, reset flags, speed/duplex/port constants, Wake-on-LAN flags, and helper accessors for split 32-bit speed fields.

This file is a compatibility shim for userland code that needs ethtool ioctl structures even when system headers are unavailable or unsuitable. It contains declarations only, no runtime logic beyond inline speed helpers.

Maintenance risk is ABI drift: because it is copied, newer kernel ethtool definitions will not appear here unless manually synchronized. The structs include flexible zero-length arrays matching older kernel style.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/ethtool-copy.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/event_poll.c -->
# File Research: sources/virtualization/open-iscsi/usr/event_poll.c

Implements the main `iscsid` event loop and child-process reaping helpers. It polls the control device fd, management IPC fd, and a `signalfd` for masked `SIGALRM`; each loop first runs `actor_poll()` so scheduled work executes and alarms are updated.

Management IPC dispatch switches between legacy and default auth handling. Control fd readiness calls `ipc->ctldev_handle()`. `SIGALRM` readiness only drains the signalfd; scheduled actors are run at the next loop top.

The file also tracks forked helpers: `reap_inc()`, `reap_proc()`, reload-process callback tracking, shutdown callback PID lists, SIGTERM notification to children, and wait-for-child shutdown before writing the final management IPC response.

Important coupling: `actor.c` depends on process `alarm()`, while this file masks `SIGALRM` and receives it via `signalfd`; discovery daemon children register through `shutdown_callback()` and `reap_inc()`. The loop flushes sysfs cache after each iteration because kernel objects may change during event handling.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/event_poll.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/event_poll.h -->
# File Research: sources/virtualization/open-iscsi/usr/event_poll.h

Declares event-loop, process-reaping, reload tracking, shutdown callback, and event-loop exit functions. It forward declares `struct iscsi_ipc` and `struct queue_task`.

The typo in the parameter name `realod_proc_pid` is harmless but visible in the public prototype. Consumers use this header to integrate daemon helpers and management shutdown with the central `event_loop()`.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/event_poll.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/flashnode.c -->
# File Research: sources/virtualization/open-iscsi/usr/flashnode.c

Builds and prints firmware flashnode configuration records for offload-capable iSCSI hardware. `flashnode_info_print_flat()` emits a compact `transport: [idx] address:port,tpgt target` line with IPv6 bracket formatting.

Most of the file converts selected user parameter names into netlink attribute iovecs. Helpers allocate `iscsi_flashnode_param_info` netlink attributes for ISID bytes, IPv4/IPv6 addresses, uint8/uint16/uint32 values, and fixed-size strings. `flashnode_build_config()` walks a list of `user_param` names and appends matching attributes starting at `iovs + 2`, leaving slots 0 and 1 for netlink header/event metadata.

It supports many session and connection fields: discovery flags, entry enable, immediate data, InitialR2T, ordering, CHAP flags, ERL, timers, target name/alias, burst sizes, TPGT, discovery parent metadata, portal type, CHAP indexes, IP/port, digest flags, TCP options, redirect IP, segment sizes, traffic class, flow label, link-local IPv6, window scaling, and StatSN values.

Risks: `to_key()` uses a single global buffer and only formats index 0, matching the project’s one-connection limit; invalid IP conversion silently skips the attribute; callers own cleanup of allocated iovec bases.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/flashnode.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/flashnode.h -->
# File Research: sources/virtualization/open-iscsi/usr/flashnode.h

Defines flashnode session, connection, and combined record structures used for firmware/offload iSCSI boot entries. The fields mirror driver flashnode parameters: target identity, CHAP credentials/indexes, discovery parent data, ISID, portal type, burst and timeout parameters, enable/auth/order flags, IPv4/IPv6 connection addresses, TCP tuning, digest flags, sequence counters, and transport name.

Exports flat printing, logout by flashnode session id, and netlink configuration building. This header bridges IDBM-style names, auth/config limits, and kernel flashnode netlink attributes.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/flashnode.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/Makefile -->
# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/Makefile

Builds firmware boot parameter objects for iBFT/Open Firmware support: `fw_entry.o`, `fwparam_sysfs.o`, `prom_lex.o`, `prom_parse.tab.o`, and `fwparam_ppc.o`. It sets PIC CFLAGS, includes top-level `include`, `usr`, and `libopeniscsiusr`, and embeds `SBINDIR` and `ISCSI_VERSION_STR`.

Generated parser sources are checked in; lex/bison only run if generated outputs are missing. `clean` removes object files, bison output files, and dependency metadata. This supports systems without lex/bison during normal builds.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/fw_entry.c -->
# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/fw_entry.c

Provides the high-level firmware boot entry interface. It first tries PowerPC Open Firmware parsing, then sysfs/iBFT parsing for boot info and target lists. It also frees target lists and prints boot-context records in IDBM-style key/value format.

`fw_setup_nics()` walks firmware targets, configures software NICs with IPv4/IPv6 address, mask/prefix, gateway, VLAN, and target route, or configures offload interfaces via `iface_setup_from_boot_context()`. It avoids repeating bring-up work for the same interface.

`fw_print_entry()` prints initiator, network, and target sections between `ISCSI_BEGIN_REC` and `ISCSI_END_REC`, including iface name/MAC/transport, DHCP/static decision, addresses, DNS, VLAN, target portal, CHAP credentials, and boot LUN when present.

This file is the integration layer between raw firmware parsers, network setup utilities, iface records, and IDBM output naming.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/fw_entry.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/fwparam.h -->
# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/fwparam.h

Declares firmware boot parameter backends. It exposes sysfs/iBFT and PowerPC Open Firmware functions for retrieving one boot entry or a list of targets. It also defines `FILENAMESZ` as 1024 for path buffers.

This is the private backend interface used by `fw_entry.c`.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/fwparam.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/fwparam_ppc.c -->
# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/fwparam_ppc.c

Parses PowerPC Open Firmware device-tree bootpath data for iSCSI boot. It reads `/proc/device-tree/chosen/bootpath`, discovers iSCSI-capable NIC paths, parses Open Firmware boot parameters with the checked-in lexer/parser, locates local MAC addresses, and fills `struct boot_context`.

The parser support functions map qualifiers and parameters into `struct ofw_dev`: client/server/gateway/DHCP addresses, target and initiator IQNs, ports, LUN, ISID, CHAP IDs/passwords, and filename/retry strings. `fill_context()` converts an `ofw_dev` into open-iscsi boot fields, maps NIC paths to `ethN` based on sorted discovery order, and formats the MAC.

`fwparam_ppc_boot_info()` returns the boot-selected target from bootpath. `fwparam_ppc_get_targets()` currently adds only that boot target to the list, with comments noting lack of broader target enumeration.

Risks: uses global parser/device arrays and is explicitly not thread-safe; device-tree path assumptions are PowerPC-specific; memory cleanup frees top-level `ofw_dev` objects but parameter allocations are owned inside those objects without a deep free in this file.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/fwparam_ppc.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/fwparam_sysfs.c -->
# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/fwparam_sysfs.c

Reads iSCSI boot firmware data from sysfs. It supports the standard `/sys/firmware/ibft/` subsystem and low-level-driver-specific `/sys/firmware/iscsi_boot*` roots.

The scanner discovers `target*` and `ethernet*` directories, reads valid/boot-selected flags, associates targets with NICs via `nic-assoc` and NIC `index`, and fills `boot_context` with MAC, iface, boot NIC/target IDs, IP configuration, DNS, VLAN, origin, target name/address/port/LUN, CHAP credentials, initiator name/ISID, and boot root.

For standard iBFT, it tries to resolve a Linux netdev through firmware device links and falls back to MAC lookup. For LLD-specific roots, it records the SCSI host name instead. `fwparam_sysfs_boot_info()` returns the boot-selected pair; `fwparam_sysfs_get_targets()` appends all valid target/NIC pairs across iBFT and LLD roots.

Risks: static global target/NIC arrays cap discovery at 255 entries; partial firmware data may be skipped, but existing valid list entries can still be returned; sysfs naming assumptions must track kernel ABI changes.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/fwparam_sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/iscsi_obp.h -->
# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/iscsi_obp.h

Defines Open Firmware boot parameter parsing types for PowerPC iSCSI boot. It enumerates device types, boot qualifiers, and supported OBP parameters such as client/server addresses, gateway, subnet mask, initiator/target names, CHAP credentials, LUN, ISID, iSNS/SLP, retry counts, and timeout.

`struct ofw_dev` stores parser output: property path, device type, qualifiers, parameter pointers, config partition, device path, and binary MAC. The header declares parser helper callbacks used by lexer/parser code to add parameters and qualifiers.

This is a narrow schema layer between generated parser code and `fwparam_ppc.c`.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/iscsi_obp.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/meson.build -->
# File Research: sources/virtualization/open-iscsi/usr/fwparam_ibft/meson.build

Defines the Meson source list for firmware parameter support: `fw_entry.c`, `fwparam_ppc.c`, `fwparam_sysfs.c`, `prom_lex.c`, and `prom_parse.tab.c`.

It mirrors the Makefile object list at the source-file level and assumes generated parser C files are present in the tree.
<!-- END FILE RESEARCH: sources/virtualization/open-iscsi/usr/fwparam_ibft/meson.build -->