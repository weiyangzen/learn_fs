# Group Research: group_1374_openbsd_src_sources_os_bsd_openbsd_src_sbin_isakmpd_monitor_fdpass__b7f3f82d5e9e

Scope verified against `Docs/research_subset_a.md`. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/monitor_fdpass.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/monitor_fdpass.c

This file implements descriptor passing helpers for isakmpd monitor/process separation.

Key APIs:
- `mm_send_fd(int socket, int fd)`: sends one file descriptor over a Unix-domain socket using `sendmsg(2)` with `SCM_RIGHTS`.
- `mm_receive_fd(int socket)`: receives one descriptor using `recvmsg(2)` and returns the passed fd.

Behavior and integration:
- Uses `struct msghdr`, `struct cmsghdr`, `CMSG_SPACE`, `CMSG_LEN`, and a one-byte iovec payload because ancillary data requires a real message payload.
- Depends on `log_error()` for failure reporting and `monitor.h` for exported declarations.
- Validates send/receive byte count is exactly one and checks that received control message type is `SCM_RIGHTS`.

Risk notes:
- `mm_receive_fd()` checks `cmsg_type` but does not explicitly validate `cmsg_level == SOL_SOCKET` or `cmsg_len`; malformed local control messages could be rejected less strictly than ideal.
- This code assumes a trusted local IPC channel between isakmpd processes.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/monitor_fdpass.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/nat_traversal.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/nat_traversal.c

This file implements IKEv1 NAT traversal negotiation and keepalive scheduling.

Key APIs:
- `nat_t_init()`: precomputes NAT-T vendor ID MD5 hashes.
- `nat_t_add_vendor_payloads(struct message *)`: appends supported NAT-T vendor payloads unless NAT-T is disabled.
- `nat_t_check_vendor_payload(struct message *, struct payload *)`: detects peer NAT-T support from vendor payload hashes and marks payloads consumed.
- `nat_t_exchange_add_nat_d(struct message *)`: adds NAT-D payloads for remote then local addresses.
- `nat_t_exchange_check_nat_d(struct message *)`: compares received NAT-D payloads against local/remote address hashes and sets NAT-T enable/keepalive flags.
- `nat_t_setup_keepalive(struct sa *)`: schedules UDP encapsulation keepalives for a phase 1 SA when applicable.

Behavior and integration:
- `disable_nat_t` globally disables NAT-T support, set by command-line handling elsewhere.
- Supports draft NAT-T and RFC 3947 markers through `isakmp_nat_t_cap`.
- NAT-D hashes are computed as `HASH(CKY-I | CKY-R | IP | Port)` using the negotiated phase 1 hash.
- Payload type switches between RFC `ISAKMP_PAYLOAD_NAT_D` and draft `ISAKMP_PAYLOAD_NAT_D_DRAFT` based on exchange flags.
- Keepalives send through the encapsulated transport inside `struct virtual_transport`; interval comes from `General/NAT-T-Keepalive`, defaulting to 20 seconds.

Risk notes:
- `nat_t_setup_hashes()` allocates persistent hash buffers and is intended to run once; there is no corresponding teardown.
- NAT detection depends on exact sockaddr address/port data from transport methods, so transport address normalization matters.
- Keepalive callback assumes `sa->transport` is a virtual transport with an active `encap` member.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/nat_traversal.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/nat_traversal.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/nat_traversal.h

This header defines the public NAT traversal interface for isakmpd.

Key declarations:
- NAT-T VID identifiers: `VID_DRAFT_V2`, `VID_DRAFT_V2_N`, `VID_DRAFT_V3`, `VID_RFC3947`.
- `struct nat_t_cap`: describes one NAT-T capability marker, including flags, source text, generated hash, and hash length.
- Global `disable_nat_t`.
- Function prototypes for initialization, vendor payload handling, NAT-D generation/checking, and keepalive setup.

Integration:
- Consumed by exchange/message processing code to advertise and detect NAT-T support.
- Depends on `struct message`, `struct payload`, and `struct sa` definitions from other isakmpd headers.

Risk notes:
- The header exposes only the high-level NAT-T operations; capability storage is private to `nat_traversal.c`.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/nat_traversal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/pf_key_v2.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/pf_key_v2.c

This file is isakmpd’s OpenBSD PF_KEY v2 integration layer. It opens the kernel PF_KEY socket, constructs and parses PF_KEY messages, installs/deletes kernel SAs and flows, handles ACQUIRE and EXPIRE notifications, and creates dynamic on-demand configuration entries.

Major internal structures:
- `struct pf_key_v2_node`: one PF_KEY message segment/extension with type, size, flags, and ownership marker.
- `TAILQ_HEAD(pf_key_v2_msg, pf_key_v2_node)`: message container used for scatter/gather `writev(2)` and parsed incoming extensions.
- `PF_KEY_V2_ROUND()` and `PF_KEY_V2_CHUNK`: enforce PF_KEY 64-bit extension alignment.

Core PF_KEY message helpers:
- `pf_key_v2_msg_new()`, `pf_key_v2_msg_add()`, `pf_key_v2_msg_free()`: build and destroy segment queues.
- `pf_key_v2_seq()`: monotonically allocates request sequence IDs.
- `pf_key_v2_write()`: writes a queued PF_KEY message with version, pid, sequence, and computed length.
- `pf_key_v2_read()`: reads one PF_KEY packet, parses extensions, and filters by sequence/pid for synchronous replies.
- `pf_key_v2_call()`: write request and wait for matching reply.
- `pf_key_v2_find_ext()`: returns a parsed extension node by extension type.

Public operations:
- `pf_key_v2_open()`: opens `socket(PF_KEY, SOCK_RAW, PF_KEY_V2)` and registers for ESP, AH, and IPCOMP notifications.
- `pf_key_v2_get_spi()`: sends `SADB_GETSPI` for ESP/AH/IPCOMP and returns allocated SPI/CPI bytes.
- `pf_key_v2_get_kernel_sa()`: fetches kernel SA state with `SADB_GET` into a static `struct sa_kinfo`.
- `pf_key_v2_set_spi()`: installs or updates an SA, including algorithm mapping, replay window, lifetimes, UDP encapsulation, keys, identities, flow selectors, pf tag, and ipsec interface metadata.
- `pf_key_v2_enable_sa()` / `pf_key_v2_disable_sa()`: add or remove bidirectional policy flows for an established phase 2 SA.
- `pf_key_v2_delete_spi()`: deletes one kernel SA and removes dynamic configuration if appropriate.
- `pf_key_v2_connection_check()`: starts an exchange for dynamically created on-demand connections.
- `pf_key_v2_handler()`: main-loop readable-fd handler for asynchronous PF_KEY notifications.
- `pf_key_v2_group_spis()`: groups multiple protocol SAs via OpenBSD `SADB_X_GRPSPIS`.

Important control flow:
- Outbound install path: negotiated `struct sa` and `struct proto` data are translated into PF_KEY `SADB_ADD`/`SADB_UPDATE`, key extensions, address extensions, identity extensions, flow selectors, optional UDP encapsulation, optional tag, and optional interface extension.
- Flow path: `pf_key_v2_flow()` emits OpenBSD `SADB_X_ADDFLOW` or `SADB_X_DELFLOW` messages with source/destination flow, masks, transport protocol, identity extensions, and direction.
- Expire path: `pf_key_v2_notify()` dispatches `SADB_EXPIRE` to `pf_key_v2_expire()`, which looks up the matching isakmpd SA, may renegotiate on soft/hard lifetime events, and frees hard-expired SAs.
- Acquire path: `pf_key_v2_acquire()` handles kernel `SADB_ACQUIRE`, asks the kernel for matching policy, derives phase 1 peer, phase 2 local/remote IDs, defaults suites, dynamic config sections, reference counts, and then records/checks the passive connection.

Dependencies:
- Kernel PF_KEY headers: `<net/pfkeyv2.h>`, `<netinet/ip_ipsp.h>`.
- isakmpd subsystems: `conf`, `connection`, `exchange`, `ipsec`, `sa`, `timer`, `transport`, `ui`, `util`, `policy`, `udp_encap`.
- Uses OpenBSD-specific PF_KEY extensions such as flows, policies, tags, UDP encapsulation, ipsec interfaces, and grouped SPIs.

Risk notes:
- The file relies on many OpenBSD PF_KEY extension layouts and is not portable PF_KEY-only code.
- `pf_key_v2_read()` queues unexpected synchronous messages by scheduling immediate `pf_key_v2_notify` timer callbacks, so timer processing is part of PF_KEY notification delivery.
- `pf_key_v2_get_kernel_sa()` appears to assign `ssa = (struct sadb_sa *)ext` rather than `ext->seg` after finding `SADB_EXT_SA`; that is a suspicious cast in a state-extraction path.
- Dynamic config creation in `pf_key_v2_acquire()` is large and branch-heavy; failures must unwind allocated IDs, peer names, config transactions, and message objects.
- Identity conversion only supports FQDN/user FQDN and address/prefix forms; ranges, ASN.1 names, and key IDs are intentionally not converted for PF_KEY identity extensions.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/pf_key_v2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/pf_key_v2.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/pf_key_v2.h

This header exports the PF_KEY v2 interface used by the rest of isakmpd.

Key declarations:
- Global `pf_key_v2_socket`.
- Kernel SA lifecycle operations: `pf_key_v2_get_spi`, `pf_key_v2_set_spi`, `pf_key_v2_enable_sa`, `pf_key_v2_disable_sa`, `pf_key_v2_delete_spi`, `pf_key_v2_group_spis`.
- Kernel query: `pf_key_v2_get_kernel_sa`.
- Event handling: `pf_key_v2_open`, `pf_key_v2_handler`.
- On-demand connection hook: `pf_key_v2_connection_check`.
- Legacy/manual helper: `pf_key_v2_enable_spi`.

Integration:
- Forward declares `struct proto`, `struct sa`, `struct sockaddr`, and `struct kernel_sa`.
- Public API is consumed by DOI/IPsec code to allocate SPIs and install/delete negotiated SAs.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/pf_key_v2.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/policy.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/policy.c

This file implements KeyNote policy integration and KeyNote credential handling for isakmpd.

Global policy state:
- `policy_asserts`, `policy_asserts_num`: loaded KeyNote policy assertions.
- `ignore_policy`: bypass switch.
- `policy_exchange`, `policy_sa`, `policy_isakmp_sa`: current exchange/SA context used by `policy_callback()`.

Main policy callback:
- `policy_callback(char *name)` is the central KeyNote callback provider.
- On `KEYNOTE_CALLBACK_INITIALIZE` or cleanup, it resets cached static strings and allocated filters/IDs.
- On first real lookup after reset, it populates a large cached environment from negotiated phase 2 protocols, chosen transforms, phase 1 SA identity, phase 2 local/remote IDs, transport addresses, PFS, encapsulation, lifetimes, algorithms, ports, protocol numbers, and initiator role.
- Returns KeyNote attribute strings for names such as `esp_present`, `ah_present`, `remote_filter`, `local_filter`, `remote_id`, `phase_1`, `GMTTimeOfDay`, `LocalTimeOfDay`, `pfs`, `initiator`, `phase1_group_desc`, algorithm names, lifetimes, ECN flags, and negotiation addresses.

Policy initialization:
- `policy_init()` checks `General/Use-Keynote`, opens the configured policy file through `monitor_open`, verifies file secrecy, reads the whole file, parses assertions with `kn_read_asserts`, and replaces the global assertion array.

Credential helpers:
- `keynote_cert_init()`: no-op success.
- `keynote_cert_get()`: copies raw credential bytes to a NUL-terminated string.
- `keynote_cert_validate()`: parses assertions and verifies signatures.
- `keynote_cert_insert()`: adds parsed credential assertions to a KeyNote session.
- `keynote_cert_free()`: frees credential memory.
- `keynote_certreq_validate()`: validates a KeyNote public key request by decoding it.
- `keynote_certreq_decode()` and `keynote_free_aca()`: stubs.
- `keynote_cert_obtain()`: locates credential files under `KeyNote/Credential-directory` by IPv4/IPv6 address or FQDN/user FQDN ID and reads them.
- `keynote_cert_get_key()`: extracts an RSA/X509 licensee public key from credentials.
- `keynote_cert_dup()`, `keynote_serialize()`, `keynote_printable()`, `keynote_from_printable()`: string duplication/serialization wrappers.
- `keynote_ca_count()`: returns 0 because trusted CAs are treated elsewhere.

Dependencies:
- KeyNote library: `kn_read_asserts`, `kn_verify_assertion`, `kn_add_assertion`, `kn_get_licensees`, `kn_decode_key`.
- OpenSSL RSA duplication for credential key extraction.
- isakmpd subsystems: configuration, exchange, IPsec DOI structures, transport address decoding, monitor file access, secrecy checks, X.509 DN formatting.

Risk notes:
- `policy_callback()` relies on global current-context pointers and static cached buffers, making it single-context and not reentrant.
- The callback contains repeated ID formatting logic for IPv4/IPv6 address, range, subnet, FQDN, user FQDN, ASN.1 DN, and key ID forms; consistency bugs are easy here.
- Several Key ID hex conversion loops use the first byte expression repeatedly rather than indexing by loop counter, which is suspicious for non-printable Key IDs.
- `keynote_cert_insert()` adds assertions but does not free the parsed assertion strings after insertion in the visible code path.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/policy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/policy.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/policy.h

This header exports KeyNote policy and credential support.

Key definitions:
- Credential file names: `CREDENTIAL_FILE` and `PRIVATE_KEY_FILE`.
- Global policy variables: `ignore_policy`, `policy_asserts_num`, `policy_asserts`, `policy_exchange`, `policy_sa`, `policy_isakmp_sa`.

Exported APIs:
- Policy lifecycle and callback: `policy_init()`, `policy_callback()`.
- KeyNote credential hooks: init, get, validate, insert, free, certreq validate/decode, ACA free, cert obtain, subject extraction, key extraction, duplication, serialization, printable conversion, and CA count.

Integration:
- Used by authentication, certificate, and policy-decision code to bridge isakmpd’s internal SA/exchange state into KeyNote.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/policy.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/prf.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/prf.c

This file implements isakmpd’s pseudo-random function abstraction, currently as HMAC over an existing hash implementation.

Key APIs:
- `prf_alloc(enum prfs type, int subtype, unsigned char *shared, unsigned int sharedsize)`: allocates a `struct prf`, binds it to a hash subtype, initializes HMAC state with shared key material, stores reusable HMAC contexts, and installs function pointers.
- `prf_free(struct prf *)`: releases PRF contexts and wrapper.
- `prf_hash_init()`, `prf_hash_update()`, `prf_hash_final()`: adapter functions making the PRF look like the hash interface.

Behavior and integration:
- Only `PRF_HMAC` is supported.
- Uses `hash_get(subtype)` and the hash object’s `HMACInit`/`HMACFinal` functions.
- Saves both HMAC internal contexts so `Init` can reset the reusable hash object before each PRF operation.

Risk notes:
- `prf_free()` assumes a non-null, fully initialized PRF.
- The PRF context references the shared hash object and copies hash internals; correctness depends on the hash implementation’s context ownership model.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/prf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/prf.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/prf.h

This header defines the PRF abstraction.

Key declarations:
- `enum prfs`: currently only `PRF_HMAC`.
- `struct prf`: PRF type, opaque context, output block size, and `Init`/`Update`/`Final` function pointers.
- `struct prf_hash_ctx`: hash pointer plus saved HMAC contexts.
- Public allocation/free functions: `prf_alloc()` and `prf_free()`.

Integration:
- Used by IKE key derivation paths that need a hash-like PRF interface independent of the selected hash subtype.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/prf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/sa.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/sa.c

This file implements in-memory security association management for isakmpd.

Core data structure:
- A hash table of `struct sa` lists, indexed by XOR-folded cookies and message ID.
- Initial bucket count uses `INITIAL_BUCKET_BITS`; resize code exists but is disabled.

Lookup and creation:
- `sa_init()`: allocates and initializes SA buckets.
- `sa_find()`: generic predicate scan across all buckets.
- `sa_lookup_from_icookie()`, `sa_lookup_by_name()`, `sa_lookup_by_peer()`, `sa_isakmp_lookup_by_peer()`, `sa_lookup_isakmp_sa()`, `sa_lookup_by_header()`, `sa_lookup()`: lookup SAs by cookies, message ID, peer address, name, phase, or ISAKMP SPI.
- `sa_create()`: allocates an SA from an exchange, copies cookies/message ID/DOI, initializes DOI-specific storage and proto queue, inserts into hash table, and links into the exchange SA list.
- `sa_isakmp_upgrade()`: rehashes phase 1 SA after responder cookie is known and binds transport.

Reference and lifetime management:
- `sa_enter()`, `sa_remove()`, `sa_reference()`, `sa_release()`, `sa_free()`, `sa_delete()`: manage hash membership, reference counts, protocol cleanup, timers, cert/key storage, KeyNote session, transport references, and allocated strings.
- `sa_setup_expirations()`: schedules randomized soft expiration and hard expiration timers.
- `sa_soft_expire()` and `sa_hard_expire()`: renegotiate stayalive SAs, mark fading SAs, or delete expired SAs.

Protocol/transform handling:
- `sa_add_transform()`: registers the selected transform into a protocol entry. Responders allocate a new `struct proto`; initiators validate a responder-selected transform against proposals previously sent.
- `sa_validate_proto_xf()` and `sa_validate_xf_attrs()`: compare transform IDs and attributes between offered and selected proposals.
- `proto_free()`: releases SPIs, DOI protocol data, transform-attribute copies, and invokes DOI SPI deletion hooks.

Reporting:
- `sa_dump()`, `sa_report()`: debug/report-channel summaries.
- `sa_report_all()` and helpers print user-oriented SA status, protocol transforms, algorithms, SPIs, lifetimes, cookies, and phase information.

Other operations:
- `sa_teardown_all()`: tears down phase 2 SAs during shutdown.
- `sa_reinit()`: on configured HUP behavior, soft-expires active phase 2 SAs without active exchanges.
- `sa_flag()`: maps textual SA flags such as `active-only`, `__ondemand`, and `ikecfg`.
- `sa_mark_replaced()` / `sa_replace()`: mark old SAs replaced, remove DPD timers, and re-enable DPD on replacement SAs.

Dependencies:
- `doi`, `exchange`, `message`, `timer`, `transport`, `cert`, `key`, `policy`, `ipsec`, `dpd`, and `connection`.
- Uses KeyNote session close via `kn_close()` when policy sessions are attached.

Risk notes:
- Reference counting and timer callbacks are tightly coupled; timers hold SA references and manually clear pointers before releasing.
- `sa_free()` removes active timers and adjusts refcounts before `sa_remove()`, so misuse can underflow/over-release if called on partially managed SAs.
- Proposal validation requires all returned attributes to be present and checked, which may reject peers with non-identical but semantically compatible attribute encoding.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/sa.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/sa.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/sa.h

This header defines the central isakmpd SA and protocol structures.

Key structures:
- `struct proto`: one protocol proposal/selection inside an SA, including protocol number, SPIs for outgoing/incoming directions, chosen transform, transform ID, DOI-specific data, and stored proposal transform attributes.
- `struct proto_attr`: stored transform attribute blob used for responder-selection validation.
- `struct sa`: phase 1 or phase 2 security association with name, transport, cookies, message ID, protocol list, DOI, keystate, IDs, initiator flag, policy data, cert/key material, lifetimes, kernel acquire sequence, timers, NAT-T keepalive timer, DPD state, pf tag, and optional interface unit.
- `struct sa_kinfo`: kernel SA telemetry used mostly by DPD, including lifetimes, byte/allocation counters, addresses, SPI, UDP encapsulation port, and replay window.

Flags:
- Readiness and lifecycle: `SA_FLAG_READY`, `SA_FLAG_STAYALIVE`, `SA_FLAG_ONDEMAND`, `SA_FLAG_REPLACED`, `SA_FLAG_FADING`, `SA_FLAG_ACTIVE_ONLY`.
- Feature flags: `SA_FLAG_IKECFG`, `SA_FLAG_DPD`, `SA_FLAG_NAT_T_ENABLE`, `SA_FLAG_NAT_T_KEEPALIVE`, `SA_FLAG_IFACE`.

Exported APIs:
- SA lifecycle, lookup, reporting, transform add/free, replacement, expiration setup, and flag parsing.

Integration:
- This is a shared contract across exchange negotiation, IPsec DOI code, PF_KEY installation, NAT traversal, DPD, policy, and transport handling.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/sa.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/sysdep/openbsd/sysdep.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/sysdep/openbsd/sysdep.c

This OpenBSD-specific file provides socket policy bypass setup for isakmpd control traffic.

Key API:
- `sysdep_cleartext(int fd, int af)`: forces communication on a socket to bypass IPsec policy so IKE/key-management packets travel in cleartext.

Behavior and integration:
- No-ops when `app_none` is set.
- Supports `AF_INET` and `AF_INET6`.
- Applies `IPSEC_LEVEL_BYPASS` through monitored `setsockopt` calls for auth, ESP transport, ESP network, and optionally IPCOMP levels.
- Uses `monitor_setsockopt()` rather than direct `setsockopt`, consistent with privilege separation.

Risk notes:
- Unsupported address families fail with logging.
- IPCOMP option absence is tolerated only for `ENOPROTOOPT`; other errors fail setup.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/sysdep/openbsd/sysdep.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/timer.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/timer.c

This file implements a small monotonic-clock timer queue for isakmpd.

Key APIs:
- `timer_init()`: initializes the global event queue.
- `timer_next_event(struct timespec **timeout)`: computes the timeout until the first event for the main loop.
- `timer_handle_expirations()`: executes and frees all expired events in order.
- `timer_add_event(char *name, void (*func)(void *), void *arg, struct timespec *expiration)`: allocates and inserts an event sorted by expiration time.
- `timer_remove_event(struct event *)`: removes and frees a scheduled event.
- `timer_report()`: logs all scheduled events and remaining seconds.

Behavior and integration:
- Uses `CLOCK_MONOTONIC`, `TAILQ`, and OpenBSD timespec macros.
- Event callbacks run synchronously from `timer_handle_expirations()`.
- Used throughout isakmpd for retransmissions, SA expiration, DPD, NAT-T keepalives, and queued PF_KEY notifications.

Risk notes:
- Callback execution happens before freeing the event structure; callbacks must not assume the event pointer remains registered.
- The queue is single-threaded and not protected by locks, matching isakmpd’s event-loop model.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/timer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/timer.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/timer.h

This header defines the timer event structure and timer queue API.

Key declarations:
- `struct event`: queue link, event name, callback, callback argument, and absolute monotonic expiration.
- Timer lifecycle and queue functions: init, next timeout calculation, expiration handling, add/remove event, and reporting.

Integration:
- Shared by retransmission, SA lifetime, DPD, NAT-T, and PF_KEY notification paths.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/timer.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/transport.c -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/transport.c

This file implements common transport registration, reference counting, select-loop integration, send queues, and retransmission scheduling.

Key APIs:
- `transport_init()`: initializes global transport instance and method lists.
- `transport_method_add()`: registers a transport vtable such as UDP or UDP encapsulation.
- `transport_setup()`: initializes top-level virtual transports or inserts concrete transports into the global list.
- `transport_reference()` / `transport_release()`: manage transport lifetimes and call method `remove` on final release.
- `transport_reinit()`: calls registered method reinitializers.
- `transport_fd_set()` and `transport_pending_wfd_set()`: build read/write fd sets for listening transports and queued outbound messages.
- `transport_handle_messages()`: dispatches readable transports to virtual transport message handlers.
- `transport_send_messages()`: sends queued messages, schedules retransmissions, runs post-send hooks, and frees messages no longer needed.
- `transport_prio_sendqs_empty()`, `transport_report()`, `transport_create()`.

Behavior and integration:
- Maintains `transport_list` for concrete transports and `transport_method_list` for registered methods.
- Virtual transports own normal and priority send queues; priority queue is used for important messages such as DELETE notifications.
- Retransmission delay is simple linear/backoff-like `msg->xmits * 2 + 5`; limit comes from `General/retransmits`, default 10.
- Uses `message_send_expire`, `message_post_send`, `message_free`, and exchange `last_sent`/`in_transit` state to coordinate retransmissions.

Risk notes:
- Multiple transports may share a socket; `transport_send_messages()` clears the fd bit after one send, so earlier list entries can be favored.
- Transport references are raised before send-loop iteration so virtual transports are not removed while being used.
- The retransmission logic is explicitly called delicate in comments and is tied to exchange lifetime semantics.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/transport.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/transport.h -->
# File Research: sources/os/bsd/openbsd-src/sbin/isakmpd/transport.h

This header defines isakmpd’s transport abstraction.

Key structures:
- `struct transport_vtbl`: transport method interface with create/reinit/remove/report, fd-set helpers, input handling, message sending, source/destination address accessors, ID decoding, cloning, and queue selection.
- `struct transport`: concrete or virtual transport instance with list link, vtable, normal and priority send queues, flags, reference count, and parent virtual transport pointer.
- `struct transport_list` and exported `transport_list`.

Flags:
- `TRANSPORT_LISTEN`: transport should be included in read fd sets.
- `TRANSPORT_MARK`: mark-and-sweep garbage collection marker.

Exported APIs:
- Transport creation, initialization, method registration, fd-set construction, message handling/sending, priority queue status, reporting, reinit, setup, reference, and release.

Integration:
- Used by UDP, UDP encapsulation, virtual transports, NAT-T, SA tracking, exchange/message retransmission, and the main event loop.
<!-- END FILE RESEARCH: sources/os/bsd/openbsd-src/sbin/isakmpd/transport.h -->