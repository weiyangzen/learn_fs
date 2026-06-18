# Research: subset-b-006292

This grouped report covers the TLS and AF_UNIX source files assigned to `subset-b-006292`. Each section is source-tree aligned and wrapped for reconciliation into the corresponding per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_main.c -->
# sources/distributed-fs/ceph-client/net/tls/tls_main.c

## Purpose
`tls_main.c` is the central TCP ULP registration and configuration layer for kernel TLS. It registers the `tls` ULP, builds TLS-specific `struct proto` and `struct proto_ops` overlays on top of TCP, accepts `SOL_TLS` socket options, creates and frees `struct tls_context`, and coordinates software, device, and TOE record paths. It is the integration point that turns an established TCP socket into a kTLS socket and switches the socket's send/receive operations as TX and RX configurations move from base TCP to software or hardware TLS.

## Important APIs, Types, and Functions
- `tls_cipher_desc[]` describes supported TLS ciphers, their key/IV/salt/record-sequence offsets, AEAD algorithm names, and whether device offload may use them. Compile-time `CHECK_CIPHER_DESC` assertions keep UAPI crypto structures aligned with cipher constants.
- `update_sk_prot()` installs the selected TLS protocol and socket operation tables based on `ctx->tx_conf` and `ctx->rx_conf`.
- `wait_on_pending_writer()`, `tls_push_sg()`, `tls_push_partial_record()`, and `tls_free_partial_record()` handle lower TCP writes and recovery from partially transmitted encrypted records.
- `tls_process_cmsg()` supports `TLS_SET_RECORD_TYPE` ancillary data and forces pending open records out before the record type changes.
- `tls_ctx_create()`, `tls_ctx_free()`, `tls_sk_proto_close()`, and `tls_sk_proto_cleanup()` own context lifetime and restore the original TCP protocol callbacks.
- `do_tls_setsockopt_conf()` and `do_tls_getsockopt_conf()` implement `TLS_TX` and `TLS_RX` key/configuration exchange with userspace, including TLS 1.3 rekey support.
- `do_tls_setsockopt_tx_zc()`, `do_tls_setsockopt_no_pad()`, and `do_tls_setsockopt_tx_payload_len()` expose zero-copy sendfile, TLS 1.3 no-padding expectation, and max payload length controls.
- `build_protos()` and `build_proto_ops()` construct the protocol matrices for combinations of `TLS_BASE`, `TLS_SW`, `TLS_HW`, and `TLS_HW_RECORD`.
- `tls_init()`, `tls_update()`, `tls_get_info()`, and `tls_get_info_size()` implement the TCP ULP hooks.
- `tls_register()` and `tls_unregister()` register per-net TLS statistics/proc support, the TLS strparser workqueue, device TLS support, and the TCP ULP.

## Control Flow
On module init, per-net MIB/proc state is registered, the TLS strparser workqueue is created, device TLS is initialized, and the `tls` ULP is registered with TCP. When userspace attaches the ULP, `tls_init()` ensures the socket is established, optionally lets TOE bypass normal TLS setup, allocates `tls_context`, records the original TCP protocol, and installs the base TLS proto table entry. `setsockopt(SOL_TLS, TLS_TX/TLS_RX)` copies crypto info, validates version/cipher consistency, attempts device offload first, falls back to `tls_set_sw_offload()`, updates statistics, arms RX parsing when needed, and then switches protocol operations. TX/RX operations are then dispatched through software or device functions from `tls_sw.c` and device TLS code. Close cancels TX work, waits on pending writers, releases TX/RX resources, restores original callbacks, invokes the underlying TCP close, and frees context when no hardware side owns it.

## State and Persistence
State is in-memory per socket and per net namespace. `tls_context` stores original TCP callbacks, selected TX/RX configurations, crypto material, cipher contexts, partial-record state, and options such as `zerocopy_sendfile`, `rx_no_pad`, and `tx_max_payload_len`. Crypto key material is wiped with `memzero_explicit()` when configs fail or contexts are freed. Per-net TLS counters are allocated as percpu `linux_tls_mib` storage and exported through `/proc/net/tls_stat`. Protocol and ops matrices are process-global caches keyed by IPv4/IPv6 and TX/RX config, rebuilt when the underlying TCP proto pointer changes.

## Dependencies and Integration Points
This file depends on TCP ULP infrastructure, inet diag ULP info, net namespace pernet operations, proc/MIB support, `net/tls.h` UAPI definitions, software TLS in `tls_sw.c`, stream parsing in `tls_strp.c`, optional device TLS, and optional TOE support in `tls_toe.c`. It exposes `MODULE_ALIAS_TCP_ULP("tls")` and integrates with userspace through `SOL_TLS` socket options, cmsgs, netlink inet diagnostic attributes, and proc statistics.

## Risks and Edge Cases
The highest-risk areas are protocol pointer switching under lock/RCU rules, close-time ordering across software and hardware contexts, partial encrypted-record accounting, and rekey rules. `setsockopt` must reject mixed TLS versions/ciphers across directions and must not leave partially copied crypto material live on error. `tls_push_sg()` owns page references and memory charging while splicing pages into TCP; failures must preserve enough state to resume or free correctly. TLS 1.3 rekey is intentionally limited to same version/cipher and uses error counters on invalid attempts.

## Test Signals
Useful signals include kTLS selftests that attach `TCP_ULP=tls`, set TX/RX keys for each cipher, verify fallback from hardware to software, exercise TLS 1.3 rekey, cmsg record type changes, close with pending records, `TLS_TX_MAX_PAYLOAD_LEN`, `TLS_RX_EXPECT_NO_PAD`, inet diag ULP info, and `/proc/net/tls_stat` counter changes. Fault injection around crypto-info copy, device-offload failure, and low memory should leave no leaked keys, pages, or protocol overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_proc.c -->
# sources/distributed-fs/ceph-client/net/tls/tls_proc.c

## Purpose
`tls_proc.c` exports per-network-namespace kTLS statistics through `/proc/net/tls_stat` when `CONFIG_PROC_FS` is enabled. It is a small observability companion to `tls_main.c`.

## Important APIs, Types, and Functions
- `tls_mib_list[]` maps printed counter names to `LINUX_MIB_TLS*` indices.
- `tls_statistics_seq_show()` aggregates percpu TLS counters with `snmp_get_cpu_field_batch_cnt()` and prints a stable text table.
- `tls_proc_init()` creates `tls_stat` under a namespace's `proc_net`.
- `tls_proc_fini()` removes the proc entry during namespace teardown.

## Control Flow
`tls_main.c` allocates `net->mib.tls_statistics` and calls `tls_proc_init()` from pernet init. Reading the proc file invokes the seq callback, which batches all configured MIB counters and emits one line per counter. Namespace exit calls `tls_proc_fini()` before freeing the percpu MIB area.

## State and Persistence
The file owns no persistent state beyond the proc entry. The actual counters live in `net->mib.tls_statistics`; output is generated on demand and scoped to the active net namespace.

## Dependencies and Integration Points
It depends on procfs, seq_file, SNMP/MIB helpers, and `net/tls.h` counter definitions. It is compiled even without procfs, but the create/show logic is guarded by `CONFIG_PROC_FS`.

## Risks and Edge Cases
Counter list drift is the main maintenance risk: new TLS counters need a matching `SNMP_MIB_ITEM` to become visible. `tls_proc_fini()` calls `remove_proc_entry()` unconditionally; kernel proc removal tolerates absent entries, but init failure paths rely on this being safe.

## Test Signals
Attach kTLS sockets in TX/RX software and device modes, trigger decrypt/rekey/no-pad errors, then read `/proc/net/tls_stat` in the namespace and verify expected counters change. Namespace creation/destruction tests should show no proc entry leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_strp.c -->
# sources/distributed-fs/ceph-client/net/tls/tls_strp.c

## Purpose
`tls_strp.c` implements the kTLS receive stream parser used by software RX and device RX fallback. It assembles exactly one TLS record from the TCP receive queue into an anchor skb, supports zero-copy references to queued TCP skbs when safe, falls back to copy mode under short queues or mixed decrypted/encrypted data, and schedules process-context work when parsing cannot be completed in the data-ready path.

## Important APIs, Types, and Functions
- `tls_strp_abort_strp()` stops parsing and reports socket errors.
- `tls_strp_msg_load()`, `tls_strp_msg_done()`, `tls_strp_msg_detach()`, `tls_strp_msg_cow()`, and `tls_strp_msg_hold()` manage the current parsed TLS record.
- `tls_strp_copyin_frag()` and `tls_strp_copyin_skb()` copy incoming TCP data into either page frags or a frag_list-backed skb.
- `tls_strp_read_sock()`, `tls_strp_check_rcv()`, `tls_strp_data_ready()`, and `tls_strp_work()` drive parser progress from TCP readiness and workqueue contexts.
- `tls_strp_init()`, `tls_strp_stop()`, `tls_strp_done()`, `__tls_strp_done()`, `tls_strp_dev_init()`, and `tls_strp_dev_exit()` manage parser and global workqueue lifetime.

## Control Flow
RX setup initializes an empty anchor skb and arms `sk_data_ready` to call `tls_data_ready()` in `tls_sw.c`, which delegates to `tls_strp_data_ready()`. If the socket is user-owned, work is queued to avoid lock conflicts; otherwise the parser reads immediately. `tls_strp_read_sock()` checks `tcp_inq()`, maps the TCP queue directly into the anchor if a full contiguous record is available, asks `tls_rx_msg_size()` for the record length, and validates queue sequence/decryption consistency. If data is short, mixed, or memory pressure requires it, copy mode allocates page frags and pulls bytes with `tcp_read_sock()`. Once a full record is ready, `msg_ready` is set and upper TLS RX is notified. After decryption and consumption, `tls_strp_msg_done()` advances TCP copied sequence or flushes copied frags and immediately attempts to parse the next record.

## State and Persistence
Each `tls_strparser` stores the lower socket, anchor skb, current stream message offsets/length, `mark` content type, copy-mode and mixed-decryption flags, stop flag, message-ready flag, and a work item. Global state is only the `tls-strp` workqueue. The parser keeps skb/page references while a record is active and releases them when the record is consumed or the parser is torn down.

## Dependencies and Integration Points
The parser depends on TCP receive queue helpers, skb frag/frag_list mechanics, kTLS record-size validation in `tls_rx_msg_size()` from `tls_sw.c`, and the RX ready callback `tls_rx_msg_ready()`. Device TLS uses `skb->decrypted` state and `tls_strp_msg_detach()` to turn device-decrypted input into a delivered output skb.

## Risks and Edge Cases
Risk concentrates around skb ownership. Direct queue anchoring must not outlive TCP queue data; copy mode must correctly unref page frags and frag lists. Mixed decrypted status forces copy mode because device-offload records cannot be represented as a single consistent direct queue. `force_refresh` in `tls_strp_msg_load()` handles receive queue changes after the socket lock was released. Parser abort must set a positive `sk_err` and wake pollers.

## Test Signals
Receive tests should cover short headers, fragmented TLS records, coalesced records, low-memory fallback to workqueue, mixed device/software decrypted data, async decrypt holding records, parser abort on bad TLS length/version, and close/stop races. Instrumenting `tcp_read_done()` progress and skb refcounts is useful for leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_strp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_sw.c -->
# sources/distributed-fs/ceph-client/net/tls/tls_sw.c

## Purpose
`tls_sw.c` implements the software kTLS record datapath. On TX it builds TLS records from user data, optional splice pages, and BPF verdicts, encrypts with the kernel crypto API, and pushes encrypted scatterlists into TCP. On RX it waits for complete TLS records from `tls_strp.c`, decrypts in place or into user buffers/skbs, handles TLS 1.3 padding and key updates, integrates with sockmap/BPF stream parsing, and exposes recvmsg/splice/read_sock operations.

## Important APIs, Types, and Functions
- `tls_err_abort()` records fatal TLS errors on the socket and wakes waiters.
- TX helpers include `tls_get_rec()`, `tls_free_rec()`, `tls_tx_records()`, `tls_do_encryption()`, `tls_push_record()`, `bpf_exec_tx_verdict()`, `tls_sw_sendmsg_locked()`, `tls_sw_sendmsg()`, `tls_sw_splice_eof()`, `tx_work_handler()`, and `tls_sw_write_space()`.
- RX helpers include `tls_decrypt_sg()`, `tls_decrypt_sw()`, `tls_decrypt_device()`, `tls_rx_one_record()`, `tls_sw_recvmsg()`, `tls_sw_splice_read()`, `tls_sw_read_sock()`, and `tls_sw_sock_is_readable()`.
- Parser callbacks `tls_rx_msg_size()`, `tls_rx_msg_ready()`, and `tls_data_ready()` connect the strparser to the software RX path.
- Resource functions `tls_sw_cancel_work_tx()`, `tls_sw_release_resources_tx()`, `tls_sw_release_resources_rx()`, `tls_sw_strparser_done()`, `tls_sw_free_resources_rx()`, and context free helpers unwind crypto, skbs, work, and parser state.
- `init_prot_info()` and `tls_set_sw_offload()` initialize cipher parameters, AEAD transforms, IV/sequence state, async capability, and TLS 1.3 rekey updates.

## Control Flow
TX starts in `tls_sw_sendmsg()`, which serializes on `ctx->tx_lock` and the socket lock. It processes cmsgs, obtains or allocates an open record, calculates room based on `tx_max_payload_len`, allocates encrypted/plaintext `sk_msg` storage, then copies or zero-copies user pages. At record boundary or end-of-record, `bpf_exec_tx_verdict()` may pass, drop, or redirect plaintext. Passed records are prepared with TLS header/AAD/content type, encrypted asynchronously or synchronously, queued on `tx_list`, and transmitted in order by `tls_tx_records()` or delayed TX work. Partial TCP sends leave `tls_context->partially_sent_record` for later resume.

RX starts in `tls_sw_recvmsg()` or splice/read_sock variants. A single-reader lock prevents queue reordering. Pending decrypted `rx_list` records are drained first. Otherwise `tls_rx_rec_wait()` waits for a complete strparser record or sockmap data, `tls_rx_one_record()` selects device decrypt or software decrypt, sequence numbers advance, and records are copied, zero-copied, queued for async completion, or handed to sockmap/BPF. TLS 1.3 padding is trimmed and non-data record types are reported to userspace through `TLS_GET_RECORD_TYPE` cmsgs. KeyUpdate handshake records set `key_update_pending`, causing future reads to return `-EKEYEXPIRED` until userspace rekeys RX.

## State and Persistence
TX state includes open record, pending encrypted records, async crypto wait state, `encrypt_pending`, delayed work bits, AEAD send transform, and crypto sequence/IV state in `tls_context->tx`. RX state includes the strparser, `rx_list` for decrypted but undelivered records, `async_hold` references, `decrypt_pending`, AEAD receive transform, zero-copy and async capability flags, single-reader flags, and `key_update_pending`. All state is in-memory per socket. Crypto request memory and skb/page references must be released on completion, close, or error.

## Dependencies and Integration Points
The file depends on kernel crypto AEAD APIs, `sk_msg` helpers, TCP send/receive helpers, sockmap/BPF message verdict and stream parser integration, `tls_strp.c`, optional device TLS hooks, poll/read/splice socket operation hooks installed by `tls_main.c`, and MIB counters. It also uses tracepoints from generic sock tracing and reports TLS statistics through `TLS_INC_STATS`.

## Risks and Edge Cases
Major risks are async crypto ordering, page/sk_msg accounting, TLS 1.3 padding and content-type semantics, BPF verdict side effects, and close-time cleanup. Encryption completion may occur out of order, so transmission is allowed only when the list head is ready. Zero-copy decrypt is disabled for TLS 1.3 unless no-padding is expected or the tail confirms data content. BPF `bpf_msg_pop_data()` changes plaintext length and requires encrypted length trimming. Fatal crypto errors set `sk_err` and abort the connection. Reader locking prevents concurrent recvmsg/splice/read_sock from corrupting RX queues.

## Test Signals
Run kTLS selftests across TLS 1.2 and TLS 1.3, all supported ciphers, sync and async crypto drivers, sendmsg/splice/sendpage, cmsg record types, sockmap pass/drop/redirect, `MSG_PEEK`, `MSG_WAITALL`, partial reads, zero-copy RX, device-decrypted fallback, bad padding, bad tags, KeyUpdate and rekey completion, and close with pending async work. KASAN/KCSAN/refcount checks are particularly valuable around `sk_msg`, skb lists, and async request lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_sw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_toe.c -->
# sources/distributed-fs/ceph-client/net/tls/tls_toe.c

## Purpose
`tls_toe.c` supports TCP offload engines that handle TLS records outside the normal software/device kTLS paths. It maintains a registry of TOE devices, lets a device claim a socket during ULP initialization, and forwards hash/unhash events to registered devices.

## Important APIs, Types, and Functions
- Global `device_list` and `device_spinlock` protect registered `struct tls_toe_device` entries.
- `tls_toe_register_device()` and `tls_toe_unregister_device()` are exported for TOE drivers.
- `tls_toe_bypass()` scans devices, calls their `feature()` predicate, creates a TLS context, marks both directions `TLS_HW_RECORD`, swaps the socket destructor, and installs TOE proto operations.
- `tls_toe_hash()` and `tls_toe_unhash()` wrap the underlying TCP proto hash/unhash while invoking device callbacks under kref protection.
- `tls_toe_sk_destruct()` restores ULP data and frees the TLS context after the original destructor runs.

## Control Flow
During `tls_init()`, the TOE path can return `1` from `tls_toe_bypass()`, indicating the socket was claimed and normal kTLS context setup should be skipped. Later, when the socket is inserted or removed from TCP hashes, TLS proto operations call `tls_toe_hash()`/`tls_toe_unhash()`, which invoke all registered device callbacks and then delegate to the original protocol. On socket destruction, the saved destructor is called and the TOE TLS context is cleared.

## State and Persistence
The device registry is process-global and protected by a BH spinlock. Per-socket state is a normal `tls_context`, but configured as `TLS_HW_RECORD` in both directions and with saved destructor/proto callbacks. Device references are temporarily pinned with `kref_get()` while callbacks execute outside the registry lock.

## Dependencies and Integration Points
This file integrates with `tls_main.c` protocol matrices under `CONFIG_TLS_TOE`, `net/tls_toe.h` device driver contracts, inet connection socket ULP data, and TCP hash/unhash lifecycle.

## Risks and Edge Cases
The registry can change while callbacks execute, so the kref protocol is critical. `tls_toe_hash()` ORs callback errors and calls unhash on failure, so device callbacks must tolerate cleanup after partial success. `tls_toe_bypass()` currently returns `0` if context allocation fails, which lets normal TLS init continue rather than surfacing allocation failure from the TOE claim path.

## Test Signals
TOE driver tests should register/unregister devices, claim and reject sockets through `feature()`, force hash callback failures, race unregister with hash/unhash, and validate that socket destruction clears ULP data and frees TLS context exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/tls_toe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/trace.c -->
# sources/distributed-fs/ceph-client/net/tls/trace.c

## Purpose
`trace.c` instantiates the TLS tracepoints declared in `trace.h`. It is the translation unit that defines tracepoint storage and registration metadata for TLS device offload/resync events.

## Important APIs, Types, and Functions
- `CREATE_TRACE_POINTS` is defined before including `trace.h`.
- The include is skipped for sparse checker builds via `#ifndef __CHECKER__`.

## Control Flow
There is no runtime control flow in this file beyond compile-time tracepoint generation. Other TLS files include trace headers normally, while this file includes them in definition mode.

## State and Persistence
Tracepoint state is generated by the kernel tracing subsystem. This file owns no explicit variables beyond generated tracepoint objects.

## Dependencies and Integration Points
It depends on `<linux/module.h>` and `trace.h`. Build placement matters because `trace.h` sets `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace`.

## Risks and Edge Cases
The main risk is build-system or include-path breakage: exactly one C file should define `CREATE_TRACE_POINTS` for this trace system. Duplicate definitions or missing instantiation would break TLS trace event availability.

## Test Signals
Build with TLS tracing enabled and inspect `/sys/kernel/tracing/events/tls/`. Enabling each TLS device tracepoint while exercising hardware offload/resync paths should produce formatted events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/trace.h -->
# sources/distributed-fs/ceph-client/net/tls/trace.h

## Purpose
`trace.h` declares trace events for TLS device offload setup, device-decrypted records, RX resynchronization, and TX resynchronization. These events provide low-level observability for hardware kTLS behavior.

## Important APIs, Types, and Functions
- `TRACE_SYSTEM tls` names the trace event subsystem.
- `tls_device_offload_set` records socket, direction, TCP sequence, record number, and setup result.
- `tls_device_decrypted` records socket, TCP sequence, record number, record length, and encrypted/decrypted flags.
- `tls_device_rx_resync_send`, `tls_device_rx_resync_nh_schedule`, and `tls_device_rx_resync_nh_delay` describe RX resync activity.
- `tls_device_tx_resync_req` and `tls_device_tx_resync_send` describe TX resync requests and responses.
- `get_unaligned_be64()` converts record number bytes into printable `u64` values.

## Control Flow
Each `TRACE_EVENT` expands into static tracepoint metadata and helper code. Device TLS code calls the generated `trace_tls_*` functions at offload and resync points; formatting occurs when a trace consumer enables the event.

## State and Persistence
No persistent state is stored in the header. Trace entries capture transient socket pointers, TCP sequence numbers, record numbers, lengths, booleans, and return codes into ring buffers managed by ftrace/perf.

## Dependencies and Integration Points
The header integrates with the Linux tracepoint framework and is instantiated by `trace.c`. It is specifically oriented to TLS device offload code, not software-only kTLS.

## Risks and Edge Cases
Tracepoint ABI names and field layouts are consumed by debugging tools, so changes can break scripts. Socket pointers are printed with `%p` and are subject to kernel pointer hashing/security policy. Record-number pointers must reference at least 8 bytes when events are emitted.

## Test Signals
Enable events under `events/tls`, exercise TLS device offload setup and resync paths, and verify that expected fields appear with sane TCP sequence and record-number progression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/tls/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/Kconfig -->
# sources/distributed-fs/ceph-client/net/unix/Kconfig

## Purpose
This Kconfig file defines build-time options for Unix domain sockets, optional AF_UNIX out-of-band message support, and the UNIX sock_diag monitoring interface.

## Important APIs, Types, and Functions
- `config UNIX` enables core Unix domain socket support.
- `config AF_UNIX_OOB` enables `MSG_OOB` support for Unix stream sockets and defaults to `y` when UNIX is enabled.
- `config UNIX_DIAG` builds the netlink sock_diag interface used by tools such as `ss`.

## Control Flow
The selected symbols control Makefile object inclusion and conditional code in `af_unix.c`, `diag.c`, and related files. `UNIX` is a boolean core feature, while `UNIX_DIAG` is tristate and can be a module.

## State and Persistence
There is no runtime state. These symbols persist in kernel configuration and shape compiled code and modules.

## Dependencies and Integration Points
`AF_UNIX_OOB` and `UNIX_DIAG` both depend on `UNIX`. `UNIX_DIAG` maps to `unix_diag.o`, and `AF_UNIX_OOB` enables OOB queue handling and `SIOCATMARK` support in the main socket implementation.

## Risks and Edge Cases
Disabling `UNIX` removes functionality many userspace programs assume is present. Disabling `AF_UNIX_OOB` makes `MSG_OOB` return unsupported behavior. `UNIX_DIAG` defaults to `n` despite common tooling depending on it for diagnostics.

## Test Signals
Build matrix tests should cover `UNIX=y`, `AF_UNIX_OOB=y/n`, and `UNIX_DIAG=y/m/n`, verifying object inclusion, socket creation, OOB behavior, and `ss -x`/sock_diag behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/Makefile -->
# sources/distributed-fs/ceph-client/net/unix/Makefile

## Purpose
The Makefile maps Unix domain socket configuration symbols to kernel objects.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_UNIX) += unix.o` builds the core AF_UNIX object.
- `unix-y := af_unix.o garbage.o` always includes the main socket implementation and SCM_RIGHTS garbage collector in core UNIX support.
- `unix-$(CONFIG_SYSCTL) += sysctl_net_unix.o` adds sysctl support.
- `unix-$(CONFIG_BPF_SYSCALL) += unix_bpf.o` adds sockmap/BPF integration.
- `obj-$(CONFIG_UNIX_DIAG) += unix_diag.o` and `unix_diag-y := diag.o` build the diagnostic interface separately.

## Control Flow
Kbuild links selected component objects into `unix.o` and optionally `unix_diag.o`. Runtime init order is then controlled by initcalls and module init in the C files.

## State and Persistence
No runtime state is present. The file persists only build composition.

## Dependencies and Integration Points
It ties `Kconfig` symbols to `af_unix.c`, `garbage.c`, `sysctl_net_unix.c`, `unix_bpf.c`, and `diag.c`.

## Risks and Edge Cases
Build composition must keep `garbage.o` with `af_unix.o` because the main file calls SCM_RIGHTS GC hooks unconditionally. Optional `unix_bpf.o` must only be included when BPF syscall support provides sockmap helpers.

## Test Signals
Compile with and without `CONFIG_SYSCTL`, `CONFIG_BPF_SYSCALL`, and `CONFIG_UNIX_DIAG`; verify there are no unresolved symbols and the expected modules/objects appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/af_unix.c -->
# sources/distributed-fs/ceph-client/net/unix/af_unix.c

## Purpose
`af_unix.c` is the main Linux Unix domain socket implementation. It implements socket creation, binding, lookup, stream/seqpacket/datagram connect and accept, sendmsg/recvmsg/splice/read_skb, credentials and SCM_RIGHTS handling, poll/ioctl/shutdown behavior, procfs enumeration, BPF iterator support, and per-network-namespace AF_UNIX hash tables.

## Important APIs, Types, and Functions
- Global and per-net hash tables track unbound/abstract sockets, while separate BSD bind buckets map pathname socket inodes.
- Address helpers include `unix_validate_addr()`, `unix_mkname_bsd()`, `unix_bind_bsd()`, `unix_bind_abstract()`, and `unix_autobind()`.
- Lifecycle functions include `unix_create1()`, `unix_create()`, `unix_release()`, `unix_release_sock()`, `unix_sock_destructor()`, and `af_unix_init()`.
- Connection functions include `unix_dgram_connect()`, `unix_stream_connect()`, `unix_socketpair()`, `unix_accept()`, and `unix_getname()`.
- Datapath functions include `unix_dgram_sendmsg()`, `unix_stream_sendmsg()`, `unix_seqpacket_sendmsg()`, `__unix_dgram_recvmsg()`, `__unix_stream_recvmsg()`, `unix_stream_read_generic()`, `unix_stream_splice_read()`, and `unix_read_skb()`/`unix_stream_read_skb()`.
- SCM helpers include `unix_scm_to_skb()`, `unix_skb_to_scm()`, `unix_maybe_add_creds()`, `unix_attach_fds()`, `unix_detach_fds()`, `scm_stat_add()`, `scm_stat_del()`, and `unix_orphan_scm()`.
- Readiness and controls include `unix_poll()`, `unix_dgram_poll()`, `unix_ioctl()`, `unix_inq_len()`, `unix_outq_len()`, `unix_shutdown()`, and `unix_setsockopt(SO_INQ)`.
- Proc/BPF iterator support includes seq operations for `/proc/net/unix` and the `unix` BPF iterator target.

## Control Flow
Kernel init registers datagram and stream protos, registers the `PF_UNIX` family, registers per-net namespace state, builds BPF proto wrappers, and optionally registers a BPF iterator. Socket creation selects stream, datagram, raw-as-datagram, or seqpacket ops and inserts a new unbound socket into the per-net hash. Bind either creates a pathname socket inode and adds a BSD inode bucket entry or creates an abstract address and moves the socket to the abstract hash. Datagram connect finds a peer and updates `unix_peer()` with permission and flow-control checks. Stream connect creates an embryo socket, waits for listener backlog room, copies listener address/credentials, links peers, and queues the embryo skb on the listener. Accept dequeues that skb and grafts the embryo socket into the accepted socket.

Datagram send builds one skb, attaches credentials and optional file descriptors, resolves destination by name or connected peer, applies filters/security, waits on peer receive queue flow control, updates SCM accounting, queues to the peer, and wakes readers. Stream send chunks data into paged skbs, attaches SCM only to the first buffer, maintains `inq_len`, supports splice pages, and optionally queues a one-byte OOB skb. Receive paths serialize with `u->iolock`, honor peek offsets, copy credentials/file descriptors, update SCM graph accounting, manage OOB and `SCM_INQ`, and free or retain skbs depending on consumption and `MSG_PEEK`.

## State and Persistence
Per socket state lives in `struct unix_sock`: address/path, peer pointer, listener pointer for embryos, state lock, I/O and bind mutexes, peer wait/wake entries, SCM fd accounting, optional OOB skb, receive queue byte count, and `SO_INQ` setting. Per-net state includes `net->unx.table` buckets/locks and `sysctl_max_dgram_qlen`. Global state includes BSD inode buckets, lockdep comparison functions, and `unix_nr_socks`. Pathname bindings persist as filesystem socket nodes until unlinked by userspace; abstract bindings and queues are in-memory.

## Dependencies and Integration Points
The file depends on VFS path creation/lookup, LSM hooks, pidfs registration for peer credentials, SCM_RIGHTS helpers, `garbage.c` for inflight Unix fd graph management, sysctl registration, BPF cgroup hooks, sockmap/BPF proto replacement, procfs/seq_file, BPF iterators, and core socket/TCP-state conventions. It exports `unix_peer_get()`, `unix_inq_len()`, and `unix_outq_len()` for diagnostics and other kernel users.

## Risks and Edge Cases
This file is concurrency-sensitive. Correctness depends on hash bucket locks, `unix_state_lock()`, double-lock ordering, receive queue locks, `u->iolock`, and bind mutexes. Stream connect has subtle backlog waiting and embryo cleanup paths. SCM_RIGHTS must update the GC graph exactly when skb ownership changes, including peek, partial stream consumption, accept, and orphaning for BPF read_skb. Datagram asymmetric flow control uses peer wait relays to avoid stuck writers. OOB support must coordinate `oob_skb`, consumed lengths, `SIOCATMARK`, and inline vs non-inline reads. Pathname binds must unlink created filesystem nodes on late failure.

## Test Signals
Run AF_UNIX selftests for stream/datagram/seqpacket bind/connect/listen/accept/socketpair, abstract and pathname sockets, autobind, reconnect/disconnect, backlog blocking, poll readiness, shutdown propagation, `SIOCINQ`/`SIOCOUTQ`/`SIOCUNIXFILE`, `SO_INQ`/`SCM_INQ`, `SCM_CREDENTIALS`, pidfd credentials, SCM_RIGHTS pass/peek/partial receive, OOB send/recv/atmark, splice send/read, BPF cgroup hooks, sockmap insertion, `/proc/net/unix`, BPF iterator output, namespace teardown, and stress tests with concurrent close/send/recv.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/af_unix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/af_unix.h -->
# sources/distributed-fs/ceph-client/net/unix/af_unix.h

## Purpose
`af_unix.h` is the local header shared by AF_UNIX implementation files. It defines hash table sizing, skb control-block metadata, and cross-file prototypes for peer lookup, SCM_RIGHTS garbage collection, diagnostics, sysctl, and BPF sockmap integration.

## Important APIs, Types, and Functions
- `UNIX_HASH_MOD`, `UNIX_HASH_SIZE`, and `UNIX_HASH_BITS` define hash table layout.
- `struct unix_skb_parms` overlays `skb->cb` via `UNIXCB(skb)` and stores sender pid/uid/gid, passed file list, optional security ID, and consumed byte count.
- GC prototypes connect `af_unix.c` with `garbage.c`: `unix_add_edges()`, `unix_del_edges()`, `unix_update_edges()`, `unix_prepare_fpl()`, `unix_destroy_fpl()`, `unix_peek_fpl()`, and `unix_schedule_gc()`.
- Diagnostic helpers `unix_inq_len()` and `unix_outq_len()` are shared with `diag.c`.
- Sysctl registration has real or stub implementations based on `CONFIG_SYSCTL`.
- BPF hooks expose base protos and proto-update functions under `CONFIG_BPF_SYSCALL`.

## Control Flow
This header has no runtime flow, but its conditional declarations choose whether sysctl and BPF call sites compile to real functions or no-op stubs.

## State and Persistence
No state is allocated here. The notable state contract is `UNIXCB(skb)`, which persists per skb while queued and is consumed by receive, SCM, and GC paths.

## Dependencies and Integration Points
It depends on uid/gid types, SCM file pointer lists, `struct unix_sock`, `struct sk_psock`, and shared AF_UNIX internals. It is included by `af_unix.c`, `diag.c`, `garbage.c`, `sysctl_net_unix.c`, and `unix_bpf.c`.

## Risks and Edge Cases
`struct unix_skb_parms` must fit inside `skb->cb`; `af_unix.c` enforces this with `BUILD_BUG_ON`. Changes to the control block affect every send/receive and GC path. Conditional stubs must match real function signatures to avoid config-only build failures.

## Test Signals
Compile all relevant config combinations and run SCM_RIGHTS, diag, sysctl, and sockmap tests to validate the shared contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/af_unix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/diag.c -->
# sources/distributed-fs/ceph-client/net/unix/diag.c

## Purpose
`diag.c` implements the AF_UNIX `SOCK_DIAG` netlink monitoring interface. It lets userspace dump or query Unix sockets and request optional name, VFS, peer, pending-connection, queue-length, memory, shutdown, and UID attributes.

## Important APIs, Types, and Functions
- Attribute dumpers include `sk_diag_dump_name()`, `sk_diag_dump_vfs()`, `sk_diag_dump_peer()`, `sk_diag_dump_icons()`, `sk_diag_show_rqlen()`, and `sk_diag_dump_uid()`.
- `sk_diag_fill()` builds one `unix_diag_msg` netlink response and attaches requested attributes.
- `unix_diag_dump()` iterates all per-net AF_UNIX hash buckets for dump requests.
- `unix_lookup_by_ino()` and `unix_diag_get_exact()` support exact inode lookup and retry with larger skb sizes.
- `unix_diag_handler_dump()` dispatches dump versus exact query.
- `unix_diag_init()` and `unix_diag_exit()` register/unregister the sock_diag handler.

## Control Flow
Userspace sends `SOCK_DIAG_BY_FAMILY` for `AF_UNIX`. Dump requests iterate bucket/slot positions saved in netlink callback args and call `sk_diag_fill()` for matching socket states. Exact requests require `udiag_ino`, look up a socket by inode, validate the cookie, allocate a reply, retry with more attribute space if needed, and unicast the result.

## State and Persistence
The module stores only the registered `sock_diag_handler`. It reads live socket state from AF_UNIX hash tables, peer pointers, VFS path data, receive queues, and queue length helpers.

## Dependencies and Integration Points
It depends on AF_UNIX internals from `af_unix.h`, sock_diag, netlink, user namespace UID munging, TCP socket state values, and `unix_inq_len()`/`unix_outq_len()` from `af_unix.c`.

## Risks and Edge Cases
Attribute dumping must respect locking: name may be read under hash lock via acquire semantics, VFS path requires state lock, listener icons require receive queue lock, and peer lookup must hold a reference. Exact lookup scans all buckets and can race close, so cookie checks and references are important. Netlink response sizing is conservative but bounded by a page.

## Test Signals
Use `ss -x`, `ss -xl`, and direct unix_diag netlink tests against sockets in each state, with abstract/pathname names, listener queues, peers, SCM queues, namespaces, and exact inode/cookie queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/garbage.c -->
# sources/distributed-fs/ceph-client/net/unix/garbage.c

## Purpose
`garbage.c` implements garbage collection for AF_UNIX sockets passed through `SCM_RIGHTS`. It tracks in-flight Unix socket file descriptors as a directed graph and collects strongly connected components that are reachable only through their own queued file descriptors.

## Important APIs, Types, and Functions
- `struct unix_vertex` represents an in-flight Unix socket in the graph.
- `struct unix_edge` represents a passed Unix socket fd from predecessor to receiver.
- `unix_get_socket()` identifies AF_UNIX sockets from passed `struct file` objects.
- `unix_add_edges()`, `unix_del_edges()`, and `unix_update_edges()` maintain graph edges and per-user inflight counters as skbs are queued, removed, and accepted.
- `unix_prepare_fpl()`, `unix_destroy_fpl()`, and `unix_peek_fpl()` allocate graph metadata, tear it down, and invalidate GC decisions on `MSG_PEEK`.
- `unix_walk_scc()` and `__unix_walk_scc()` run iterative Tarjan SCC detection; `unix_walk_scc_fast()` rechecks known cyclic SCCs.
- `unix_gc()` collects dead SCC queues into a hitlist and purges them.
- `unix_schedule_gc()` decides when to queue or flush GC work.

## Control Flow
When AF_UNIX sends file descriptors, `unix_prepare_fpl()` allocates vertices/edges and schedules GC. When the skb is queued to a receiver, `unix_add_edges()` converts Unix socket files in the fd list into graph edges, updates receiver accounting, and increments `user->unix_inflight`. When the skb is consumed or destroyed, `unix_del_edges()` removes those edges and decrements counters. If graph state may be cyclic, `unix_gc()` walks SCCs under `unix_gc_lock`, decides whether each SCC is dead by checking outgoing edges and file reference counts, moves queued skbs from dead sockets/listener embryos to a hitlist, marks fd lists dead, and purges the hitlist outside the graph lock.

## State and Persistence
Global state includes `unix_gc_lock`, graph-state flags, unvisited/visited vertex lists, vertex index counters, cyclic SCC count, `gc_in_progress`, and a seqcount used to detect `MSG_PEEK` interference. Per fd-list state includes allocated vertices/edges, inflight/dead flags, owner user, and counts. Per socket state uses `unix_sock->vertex`, `listener`, and SCM stats.

## Dependencies and Integration Points
This file is tightly integrated with `af_unix.c` SCM accounting. It depends on `struct scm_fp_list`, socket files, skb queues, workqueues, TCP listen state values, and AF_UNIX listener embryo semantics. It also updates `user->unix_inflight`, which send-side limits read locklessly to enforce `RLIMIT_NOFILE`-based pressure.

## Risks and Edge Cases
Cycle collection is subtle. Embryo sockets are treated through their listener vertex because a listener indirectly holds embryo fd refs. `MSG_PEEK` can duplicate fd references while GC is in progress, so `unix_peek_seq` forces a later retry. Reference-count deadness requires `file_count == out_degree`; false positives would drop live sockets, and false negatives leak cycles. Locking must avoid holding the GC spinlock while freeing skbs because fd destruction can sleep or reenter socket logic.

## Test Signals
Stress tests should pass Unix sockets through each other to form self-cycles, multi-socket cycles, listener/embryo cycles, and non-cyclic chains; then close external references and verify GC frees only unreachable cycles. Include `MSG_PEEK` races, high inflight fd pressure, namespace teardown, accept after fd passing, and KASAN/refcount checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/garbage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/sysctl_net_unix.c -->
# sources/distributed-fs/ceph-client/net/unix/sysctl_net_unix.c

## Purpose
`sysctl_net_unix.c` registers the per-network-namespace sysctl interface for AF_UNIX. It exposes `net/unix/max_dgram_qlen`, the default datagram receive queue length limit used when new sockets are created.

## Important APIs, Types, and Functions
- `unix_table[]` defines the `max_dgram_qlen` sysctl entry with `0644` mode and `proc_dointvec`.
- `unix_sysctl_register()` installs the table for a net namespace, duplicating it for non-init namespaces so `.data` points to that namespace's `net->unx.sysctl_max_dgram_qlen`.
- `unix_sysctl_unregister()` unregisters the table and frees duplicated tables for non-init namespaces.

## Control Flow
`af_unix.c` initializes `net->unx.sysctl_max_dgram_qlen` to `10` and calls `unix_sysctl_register()` from pernet init. The sysctl handler then reads/writes the namespace-specific integer. Namespace exit unregisters and frees any duplicated table.

## State and Persistence
The sysctl value lives in `struct net`. The init namespace uses the static table directly; other namespaces allocate a copied `ctl_table`.

## Dependencies and Integration Points
It depends on sysctl infrastructure, net namespaces, and `af_unix.h`. `unix_create1()` reads the value to initialize `sk_max_ack_backlog` for new AF_UNIX sockets.

## Risks and Edge Cases
Registration failure must free duplicated tables. `unix_sysctl_unregister()` assumes `net->unx.ctl` is valid, matching the pernet init path that bails out on registration failure. There are no min/max bounds in the table, so extreme values depend on generic integer handling and downstream socket queue behavior.

## Test Signals
Create multiple net namespaces, set different `net.unix.max_dgram_qlen` values, create datagram sockets, and verify backlog/flow-control behavior differs by namespace. Exercise namespace teardown after sysctl writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/sysctl_net_unix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/unix_bpf.c -->
# sources/distributed-fs/ceph-client/net/unix/unix_bpf.c

## Purpose
`unix_bpf.c` integrates AF_UNIX sockets with BPF sockmap/sk_msg infrastructure. It replaces socket protos with BPF-aware wrappers that route recvmsg through psock queues, use sockmap close/unhash hooks, and restore original protocols when sockets leave maps.

## Important APIs, Types, and Functions
- `unix_bpf_recvmsg()` reads from BPF psock queues first and falls back to normal AF_UNIX recv paths when needed.
- `unix_msg_wait_data()` waits for data in the socket receive queue or psock ingress queues while temporarily releasing `u->iolock`.
- `unix_dgram_bpf_rebuild_protos()` and `unix_stream_bpf_rebuild_protos()` clone base protos and override close/recvmsg/readability and stream unhash.
- `unix_dgram_bpf_update_proto()` and `unix_stream_bpf_update_proto()` install or restore BPF proto wrappers.
- `__unix_recvmsg()` dispatches to the raw AF_UNIX datagram or stream receive functions.
- `__init unix_bpf_build_proto()` builds initial wrapper protos during AF_UNIX init.

## Control Flow
When sockmap attaches a psock, the proto update hook in `af_unix.c` calls the matching update function. Restore puts back saved write-space and proto. Attach rebuilds the BPF proto wrapper if the saved base proto changed, then replaces `sk_prot`. Stream sockets also pin their peer in `psock->sk_pair` once so sockmap redirection can safely reference it until final cleanup. `unix_bpf_recvmsg()` obtains the psock, serializes with `u->iolock`, prefers already queued AF_UNIX skbs when no psock data exists, otherwise drains `sk_msg` data, waits if necessary, and falls back to normal recv when socket data arrives.

## State and Persistence
Global cached BPF proto wrappers and saved base proto pointers are protected by spinlocks and release/acquire stores. Per socket state is in `sk_prot`, `sk_write_space`, and `sk_psock` fields, including `psock->sk_pair` for streams. No persistent storage exists outside socket lifetime.

## Dependencies and Integration Points
The file depends on BPF sockmap/skmsg helpers, `af_unix.h` raw recv functions, AF_UNIX `u->iolock`, psock ingress queues, and the proto update hooks configured in `unix_dgram_proto` and `unix_stream_proto`.

## Risks and Edge Cases
The wrapper must not recursively call itself, so it uses raw `__unix_*_recvmsg()` fallbacks. Waiting releases and reacquires `u->iolock`, so queue state is rechecked after wake. Stream peer references must be taken only once even if a psock is inserted into multiple maps. Restore intentionally delays peer ref release to sockmap cleanup after RCU and pending sends.

## Test Signals
Sockmap selftests should attach AF_UNIX datagram and stream sockets, send through psock queues, mix normal receive queue data with BPF ingress data, restore sockets from maps, close/unhash streams, and verify no recursive recv, peer ref leaks, or missed wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/unix_bpf.c -->
