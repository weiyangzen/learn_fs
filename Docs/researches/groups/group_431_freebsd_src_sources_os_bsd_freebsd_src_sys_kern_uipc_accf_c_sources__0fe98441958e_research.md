# Group Research: group_431_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_uipc_accf_c_sources__0fe98441958e

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_accf.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_accf.c

## Summary
Implements FreeBSD accept-filter registration and the socket-option plumbing for attaching accept filters to listening sockets. Accept filters can hold newly accepted connections on the incomplete listen queue until a filter callback decides they are ready for `accept(2)`.

## Main Responsibilities
- Maintains the global singly linked list of registered `struct accept_filter` entries.
- Handles generic module load/unload events for accept-filter KLDs.
- Implements `accept_filt_getopt()` and `accept_filt_setopt()` for querying, installing, and removing filters from listen sockets.
- Moves connections blocked solely by a removed accept filter from `sol_incomp` to `sol_comp`.

## Key APIs
- `accept_filt_add()`, `accept_filt_del()`, `accept_filt_get()`.
- `accept_filt_generic_mod_event()`.
- `accept_filt_getopt()`, `accept_filt_setopt()`.

## Important Behavior
`accept_filt_add()` accepts a malloc-owned filter definition. If a name already exists but has a `NULL` callback from a prior unload, the old list entry is reused and the new allocation is freed.

Filter unload is intentionally disabled unless `net.accf.unloadable` is set. Deletion only clears `accf_callback`; the list node is leaked/reused to reduce dangling callback risk after module unload.

Installing a filter requires a listening socket and refuses to replace an existing filter with `EBUSY`. If the filter supplies `accf_create`, that callback runs while the socket mutex is held and must not block.

Removing a filter clears per-socket filter state, calls `accf_destroy` if present, frees the saved filter string, clears `SO_ACCEPTFILTER`, and promotes queued child sockets whose `SO_ACCEPTFILTER` bit kept them incomplete.

## State and Synchronization
The global filter list is protected by `accept_filter_mtx`. Per-socket state uses socket/listen locks. The remove path relies on the listen socket queue invariants while walking and moving sockets between incomplete and complete queues.

## Risks
The unload model is deliberately conservative because callback lifetime is not refcounted. Enabling `net.accf.unloadable` can expose stale callback hazards if sockets still reference unloaded code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_accf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_debug.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_debug.c

## Summary
Provides DDB-only debugger display commands for sockets, socket buffers, protocol switches, and protocol domains.

## Main Responsibilities
- Pretty-prints socket types, socket options, socket state bits, listen queue state, sockbuf state, sockbuf flags, protocol flags, domains, and protosw fields.
- Defines DDB `show socket`, `show sockbuf`, `show protosw`, and `show domain` commands.
- Recursively expands related structures, such as printing a socket's `so_proto` and that protocol's domain.

## Key APIs
- DDB commands: `db_show_socket`, `db_show_sockbuf`, `db_show_protosw`, `db_show_domain`.
- Internal printers: `db_print_socket()`, `db_print_sockbuf()`, `db_print_protosw()`, `db_print_domain()`.

## Important Behavior
All implementation is compiled only under `DDB`. The commands require an address argument and then treat it as the requested kernel structure pointer.

`db_print_socket()` distinguishes listen sockets from established/queued sockets. For listen sockets it prints incomplete/complete queue heads and queue lengths. For non-listen sockets it prints queue state, listener pointer, timeout/error fields, signal/oob state, and both receive and send sockbufs.

`db_print_sockbuf()` exposes mbuf chain pointers, accounting fields, low-water/timeouts, flags, and AIO queue head. The flag printers use a simple comma separator state and omit unknown bits.

## State and Synchronization
This is debugger inspection code and does not acquire socket, sockbuf, domain, or protocol locks. It is intended for DDB contexts where direct inspection is acceptable.

## Risks
The printers dereference live kernel pointers without validation beyond the user-provided address. Output can be stale or inconsistent if structures are changing, and invalid addresses can fault in debugger context.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_domain.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_domain.c

## Summary
Manages the global protocol domain list and protocol switch registration for FreeBSD networking. It also installs default protocol operation handlers for unsupported or generic operations.

## Main Responsibilities
- Provides default `EOPNOTSUPP` or `ENOPROTOOPT` protocol methods.
- Initializes `struct protosw` entries with generic socket operations and not-supported stubs.
- Adds and removes protocol domains.
- Finds domains and protocols by address family, socket type, and protocol number.
- Dynamically registers and unregisters protocol switch entries inside an existing domain.

## Key APIs
- `domain_add()`, `domain_remove()`, `pffinddomain()`, `pffindproto()`.
- `protosw_register()`, `protosw_unregister()`.
- `pr_listen_notsupp()` is exported; other not-supported handlers are private.

## Important Behavior
`pr_init()` requires every protocol to provide `pr_attach`, assigns the owning domain, fills generic send/receive/poll/sockbuf/AIO/kqueue methods, and fills missing protocol operations with not-supported stubs.

`domain_add()` only runs in the default VNET, honors an optional `dom_probe`, initializes all non-NULL protocol slots, asserts unique domain families under `INVARIANTS`, and inserts the domain into the global list.

`domain_remove()` only removes domains marked `DOMF_UNLOADABLE`. `domainfinalize()` records that early domain initialization has completed via `domain_init_status`.

`pffindproto()` matches a protocol when type matches and either registered protocol or requested protocol is zero, or both protocol numbers match.

## State and Synchronization
The global `domains` list and dynamic protocol slot updates are protected by `dom_mtx`. Lookup helpers walk without taking `dom_mtx`, relying on domain/protosw lifetime rules and the fact that most domains are not unloadable.

## Risks
Protocol removal assumes the caller has already shut down sockets and released all protocol-owned references. Dynamic registration modifies `dom_protosw` slots in place, so consumers rely on strict lifetime discipline outside this file.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_domain.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_ktls.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_ktls.c

## Summary
Implements FreeBSD kernel TLS (KTLS) session setup, software crypto scheduling, ifnet/TOE offload selection, RX record assembly/decryption, TX framing/encryption, offload reset, and KTLS statistics/sysctls.

## Main Responsibilities
- Validates and deep-copies userspace `tls_enable` parameters.
- Creates, clones, references, destroys, and exports KTLS sessions.
- Starts per-CPU KTLS worker threads and optional per-domain reclaim threads.
- Selects TOE, ifnet, or software TLS for TX/RX.
- Frames outbound TLS records into `M_EXTPG` mbufs.
- Queues software encryption work and marks records ready when crypto completes.
- Converts inbound encrypted byte streams into decrypted TLS record control messages.
- Handles route/interface changes by resetting send/receive TLS tags.
- Disables ifnet TLS when retransmission behavior makes inline offload inefficient.

## Key APIs
- Setup/cleanup: `ktls_copyin_tls_enable()`, `ktls_cleanup_tls_enable()`, `ktls_enable_rx()`, `ktls_enable_tx()`.
- Mode/query/control: `ktls_get_rx_mode()`, `ktls_get_tx_mode()`, `ktls_set_tx_mode()`, `ktls_get_rx_sequence()`.
- RX path: `ktls_pending_rx_info()`, `ktls_check_rx()`, `ktls_input_ifp_mismatch()`.
- TX path: `ktls_seq()`, `ktls_frame()`, `ktls_enqueue()`, `ktls_enqueue_to_free()`, `ktls_output_eagain()`.
- Lifetime/export: `ktls_destroy()`, `ktls_disable_ifnet()`, `ktls_session_to_xktls_onedir()`, `ktls_session_copy_keys()`.

## Important Behavior
Supported protocol versions are TLS 1.0 through TLS 1.3. Supported ciphers are AES-GCM, AES-CBC, and ChaCha20-Poly1305 with version-specific IV, auth-key, and trailer rules. AES-CBC can be disabled by `kern.ipc.tls.cbc_enable`.

KTLS initialization is lazy. The first session creation starts per-CPU worker queues and, when the software buffer cache is enabled, reclaim threads that try to recover contiguous `ktls_maxlen` buffers per NUMA domain.

TX setup requires TCP and, for TX, unmapped external-page mbufs. The selection order is TOE, ifnet TLS, then software TLS. RX first creates an OCF-capable software session, marks existing receive-buffer bytes as not-ready TLS data, then prefers TOE, ifnet RX TLS, or software mode.

`ktls_frame()` adds TLS headers/trailers to each outbound `M_EXTPG` record, assigns the session pointer, emits TLS 1.2 GCM explicit nonces and TLS 1.1+ CBC IVs, encodes TLS 1.3 as application-data records, and marks software records `M_NOTREADY`.

Software TX encryption is queued by workqueue index selected from RSS or flowid/NUMA information. TLS 1.0 CBC sessions require sequential encryption, so out-of-order sendfile completions are held in `pending_records` until their sequence number is next.

RX uses `sb_mtls` as a chain of not-ready encrypted bytes. Once a full TLS record is present, a worker detaches that record, decrypts or recrypts as needed, trims header/trailer, creates a `TLS_GET_RECORD` control mbuf, and appends the decrypted payload as a socket-buffer record.

If a NIC-decrypted RX stream falls out of sync or software had to decrypt a record, `ktls_resync_ifnet()` updates the hardware receive tag with the next TLS header sequence. Route or interface changes schedule reset tasks for send/receive tags.

## State and Synchronization
Session lifetime uses refcounts and UMA allocation. TX sessions hold an inpcb reference. Work queues are protected by per-queue mutexes and processed by bound kernel threads. Socket buffer transitions use socket I/O locks and sockbuf locks; inpcb write locks protect TX mode changes and send-tag pointers read by output paths.

## Risks
Lifetime and lock ordering are complex: sessions can be referenced by sockets, mbufs, taskqueue jobs, OCF callbacks, send tags, and pending TLS 1.0 queues. Error paths can drop TCP connections for failed TX tag reset or crypto failures. RX accepts direct mbuf-chain manipulation and must maintain socket buffer accounting precisely across encrypted, decrypted, detached, and discarded records.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_ktls.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_mbuf.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_mbuf.c

## Summary
Implements core FreeBSD mbuf chain manipulation: packet-header setup, external storage sharing, copying, splitting, trimming, pullup/copyup, device/uio conversion, defragmentation, unmapped external-page support, writable unsharing, and optional profiling/stress helpers.

## Main Responsibilities
- Maintains maximum link/protocol header sizing and exposes sysctls.
- Duplicates and releases external mbuf storage references.
- Moves, duplicates, and demotes packet headers and packet tags.
- Copies, appends, trims, splits, concatenates, and linearizes mbuf chains.
- Handles mapped and unmapped (`M_EXTPG`) mbufs for copy/apply/uio paths.
- Builds mbufs from device buffers or `uio` data.
- Defragments or collapses chains to satisfy fragment limits.
- Creates writable copies of shared external buffers.
- Provides optional mbuf stress fragmentation and profiling.

## Key APIs
- Header/storage: `mb_dupcl()`, `m_pkthdr_init()`, `m_move_pkthdr()`, `m_dup_pkthdr()`, `m_demote_pkthdr()`, `m_demote()`.
- Chain copy/edit: `m_prepend()`, `m_copym()`, `m_copypacket()`, `m_dup()`, `m_cat()`, `m_catpkt()`, `m_adj()`, `m_adj_decap()`.
- Linearization/splitting: `m_pullup()`, `m_copyup()`, `m_split()`, `mc_split()`, `m_collapse()`, `m_defrag()`.
- Data movement: `m_copydata()`, `m_copyback()`, `m_append()`, `m_apply()`, `m_devget()`, `m_uiotombuf()`, `mc_uiotomc()`, `m_mbuftouio()`, `m_unmapped_uiomove()`.
- Utility/debug: `m_getptr()`, `m_print()`, `m_fixhdr()`, `m_length()`, `m_sanity()`, `m_unshare()`.

## Important Behavior
`mb_dupcl()` shares `M_EXT` or `M_EXTPG` backing storage and increments the appropriate embedded or external refcount. `M_EXTPG` copies both the external-page metadata and the smaller `m_ext` portion needed for refcount/free handling.

`m_copym()` and `m_copypacket()` create read-only shared-storage copies when external storage is present. `m_dup()` creates a writable deep copy. `m_unshare()` replaces non-writable external buffers with writable clusters and opportunistically coalesces adjacent data.

`m_pullup()` ensures a leading region is contiguous in one mbuf and may copy extra header bytes up to `max_protohdr`. `m_pulldown()` lives in `uipc_mbuf2.c` and handles contiguous regions at arbitrary offsets.

`m_split()` and `mc_split()` can produce tails sharing external storage with the head. Callers that need to modify the result must check writability.

`m_uiotombuf()` dispatches to unmapped external-page allocation when `M_EXTPG` is requested; otherwise it uses `mc_uiotomc()`. `m_unmapped_uiomove()` walks an external-page mbuf's header, physical pages, and trailer.

`m_defrag()` creates a shortest practical chain and frees the original only after success. `m_collapse()` tries in-place coalescing first, then replaces adjacent mbufs with clusters while preserving the first mbuf and packet header.

## State and Synchronization
Most functions operate on caller-owned mbuf chains and assume external synchronization. External storage sharing uses atomic refcounting when needed. VM page allocation/free paths wire anonymous pages and require the matching external free routine.

## Risks
Many helpers free the input chain on failure while others leave it unchanged; callers must know each contract. Packet-header length and socket/send-tag references must stay consistent when moving or duplicating headers. `M_EXTPG` paths require special handling because data may live in header bytes, physical pages, and trailer bytes rather than a single mapped buffer.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_mbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_mbuf2.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_mbuf2.c

## Summary
Adds mbuf helpers from KAME/WIDE heritage: arbitrary-offset pulldown for contiguous data access and packet tag allocation/copy/delete routines.

## Main Responsibilities
- Implements `m_pulldown()` to make a byte range contiguous within an mbuf chain.
- Provides a local `m_dup1()` helper for copying a slice into a new mbuf.
- Allocates, frees, finds, deletes, and copies packet tags.
- Handles MAC framework special cases for MAC label packet tags.

## Key APIs
- `m_pulldown()`.
- `m_tag_alloc()`, `m_tag_free_default()`, `m_tag_delete()`, `m_tag_delete_chain()`.
- `m_tag_delete_nonpersistent()`, `m_tag_locate()`, `m_tag_copy()`, `m_tag_copy_chain()`.

## Important Behavior
`m_pulldown()` ensures `[off, off + len)` is contiguous. If `offp` is `NULL`, it may split or copy so the returned mbuf starts the target at offset zero; if `offp` is non-NULL, it can return a nonzero offset through `*offp`.

The function handles easy cases by extending into trailing space or leading space when the target mbuf is considered writable, and otherwise allocates a new mbuf or cluster. On error it frees the original chain.

The writability test is intentionally conservative and historically imperfect: regular non-external mbufs are treated as writable, but external storage requires an `EXT_CLUSTER` and `M_WRITABLE()`.

Packet tags are malloc-backed `struct m_tag` objects with data stored immediately after the tag header. Chain copy preserves order and deletes any destination tags before copying.

## State and Synchronization
Packet tag operations assume the caller owns or has locked the mbuf packet header tag list. Tag memory uses the `M_PACKET_TAGS` malloc type. MAC label tags call MAC framework init/copy/destroy hooks.

## Risks
`m_pulldown()` frees the input chain on malformed or too-short input and on allocation failure. Consumers must not continue using the original chain after a `NULL` return. Packet tag copying can fail partway and leaves the destination tag chain empty.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_mbuf2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_mbufhash.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_mbufhash.c

## Summary
Computes FNV-based packet hashes over selected L2, L3, and L4 fields for Ethernet and InfiniBand mbufs.

## Main Responsibilities
- Initializes per-consumer hash seeds for Ethernet and InfiniBand TCP/IP hashing.
- Safely reads headers from potentially non-contiguous mbuf chains.
- Hashes Ethernet source/destination addresses and VLAN tags when requested.
- Hashes InfiniBand hardware addresses when requested.
- Hashes IPv4/IPv6 addresses, IPv4 transport ports, and IPv6 flow labels according to flags.

## Key APIs
- `m_ether_tcpip_hash_init()`, `m_infiniband_tcpip_hash_init()`.
- `m_ether_tcpip_hash()`, `m_infiniband_tcpip_hash()`.

## Important Behavior
`m_common_hash_gethdr()` returns a direct pointer when the requested header is contiguous in the first mbuf; otherwise it copies the header into a caller-supplied stack buffer. It rejects reads beyond `m_pkthdr.len`.

For Ethernet, `m_ether_tcpip_hash()` starts after the Ethernet header, optionally hashes L2 addresses, handles hardware VLAN tags from `M_VLANTAG`, and parses in-frame VLAN headers before dispatching to IP hashing.

For IPv4, L3 hashing covers source/destination addresses. L4 hashing covers the first four bytes of TCP, UDP, or SCTP headers after validating the IPv4 header length. For IPv6, L3 hashing covers source/destination addresses and L4 hashing uses the flow label rather than walking extension headers.

InfiniBand hashing reads `ib_protocol`, optionally hashes the hardware address, and then reuses the same TCP/IP hash helper.

## State and Synchronization
The functions are pure readers of the mbuf chain and return an updated hash accumulator. Seed initialization uses `arc4random()` and FNV over the random seed.

## Risks
The parser is intentionally shallow. IPv6 L4 hashing does not inspect transport ports, and IPv4 options or fragmented/truncated packets can limit L4 contribution. Callers must choose hash flags that match their load-balancing semantics.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_mbufhash.c -->