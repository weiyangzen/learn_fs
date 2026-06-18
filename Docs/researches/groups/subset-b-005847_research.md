# subset-b-005847 Research

Grouped source research for Ceph client protocol/client headers and adjacent Linux kernel support headers under `include/linux`. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/ceph_features.h -->
# sources/distributed-fs/ceph-client/include/linux/ceph/ceph_features.h

## Purpose

`ceph_features.h` defines the 64-bit Ceph feature negotiation bitspace used by clients and servers. It handles feature bit reuse through incarnation marker bits so an old meaning and a new meaning for the same numeric bit are not mistaken for each other during connection negotiation.

## Important APIs, Types, and Functions

Key macros are `CEPH_FEATURE_INCARNATION_1/2/3`, `DEFINE_CEPH_FEATURE`, `DEFINE_CEPH_FEATURE_DEPRECATED`, `DEFINE_CEPH_FEATURE_RETIRED`, and `CEPH_HAVE_FEATURE`. The file enumerates supported named feature constants such as `CEPH_FEATURE_MSG_AUTH`, `CEPH_FEATURE_SERVER_LUMINOUS`, `CEPH_FEATURE_MSG_ADDR2`, and `CEPH_FEATURE_CEPHX_V2`, then aggregates the client-advertised mask in `CEPH_FEATURES_SUPPORTED_DEFAULT`; `CEPH_FEATURES_REQUIRED_DEFAULT` is zero.

## Control Flow

There is no runtime control flow. Compile-time macro expansion creates feature constants and masks, while callers use `CEPH_HAVE_FEATURE(x, name)` to require both the bit and the correct incarnation marker.

## State and Persistence Behavior

The file owns no mutable state. Its constants become persistent wire-compatibility contracts because feature masks are exchanged during monitor, OSD, and messenger handshakes.

## Dependencies and Integration Points

It depends on kernel integer types and `__maybe_unused` availability through includers. Integration is with `msgr.h`, messenger negotiation, monitor session setup, and any protocol path that gates behavior on peer feature masks.

## Risks and Edge Cases

Feature bit reuse is the central risk. Testing only `(mask & bit)` is unsafe for reused bits; callers must use the mask form. The spelling `LUNINOUS` in a retired macro argument is inert but illustrates that retired macro arguments are not type checked. Adding a feature to the wrong supported/default mask can create false compatibility.

## Test Signals

Useful signals are build coverage of feature consumers, connection tests against clusters with old and new release feature masks, assertions that `CEPH_HAVE_FEATURE` rejects reused bits lacking incarnation markers, and protocol downgrade tests for optional features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/ceph_features.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/ceph_frag.h -->
# sources/distributed-fs/ceph-client/include/linux/ceph/ceph_frag.h

## Purpose

`ceph_frag.h` defines Ceph directory fragment encoding helpers. A fragment represents a subset of a 24-bit value space using a prefix length and value, packed into a 32-bit word with the high 8 bits holding the number of significant bits.

## Important APIs, Types, and Functions

Inline helpers are `ceph_frag_make`, `ceph_frag_bits`, `ceph_frag_value`, `ceph_frag_mask`, `ceph_frag_mask_shift`, `ceph_frag_contains_value`, `ceph_frag_make_child`, `ceph_frag_is_leftmost`, `ceph_frag_is_rightmost`, and `ceph_frag_next`. The external comparator `ceph_frag_compare()` sorts fragments in logical value-space order.

## Control Flow

Runtime flow is limited to arithmetic helpers. Callers create a fragment, test whether a hash belongs to it, split it into child fragments, advance to the next peer fragment, or compare fragments while traversing directory-fragment trees.

## State and Persistence Behavior

No state is stored here. Encoded fragments appear in CephFS wire structures such as `ceph_frag_tree_split` and MDS readdir/reply paths, so the bit layout is an ABI.

## Dependencies and Integration Points

It relies on `__u32` and `bool` from kernel headers included by users. It integrates with `ceph_fs.h` fragment tree records, directory hashing from `ceph_hash.h`, and MDS metadata layout.

## Risks and Edge Cases

Inputs assume `b <= 24`; larger values make shifts invalid. Numeric sorting of encoded fragments is explicitly wrong because the prefix length is stored in high bits. `ceph_frag_next()` can step past the rightmost fragment if callers do not check bounds.

## Test Signals

Tests should cover make/bits/value/mask round trips, child partition coverage without overlap, leftmost/rightmost detection, logical comparator ordering, and containment results for boundary hash values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/ceph_frag.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/ceph_fs.h -->
# sources/distributed-fs/ceph-client/include/linux/ceph/ceph_fs.h

## Purpose

`ceph_fs.h` is the shared CephFS client/server wire-format contract for filesystem protocols. It defines protocol revisions, inode constants, file and directory layouts, auth and connection modes, message type ids, MDS states and operations, request/reply wire structs, lease/capability records, snapshots, quotas, and file lock formats.

## Important APIs, Types, and Functions

Important types include `ceph_file_layout_legacy`, `ceph_file_layout`, `ceph_dir_layout`, `ceph_mon_request_header`, `ceph_statfs`, `ceph_mds_request_head`, `ceph_mds_reply_inode`, `ceph_mds_caps`, `ceph_mds_lease`, `ceph_mds_snap_realm`, and `ceph_mds_quota`. Important helpers declared here include `ceph_file_layout_is_valid()`, layout legacy conversion helpers, `ceph_auth_proto_name()`, `ceph_con_mode_name()`, `ceph_mds_state_name()`, `ceph_session_op_name()`, `ceph_mds_op_name()`, `ceph_flags_to_mode()`, `ceph_caps_for_mode()`, and cap/lease/snap op name helpers.

## Control Flow

This header encodes protocol flow through constants and packed structs. Monitor messages request maps/statfs/auth, MDS session ops open/renew/close sessions, MDS request heads carry operation-specific union arguments, replies carry dentry/inode/cap/lease payloads, and capability messages drive grant/revoke/flush/update cycles between MDS and clients.

## State and Persistence Behavior

Most structs are `packed` little-endian ABI records sent over the wire or stored in durable metadata. `ceph_file_layout` is the in-kernel normalized layout with an RCU `pool_ns` string, while legacy layout structs preserve older on-wire forms.

## Dependencies and Integration Points

It includes `msgr.h` and `rados.h`. Integration points include the messenger message layer, monitor client, MDS client, CephFS inode/capability code, directory fragmentation, layout mapping through `striper.h`, and RADOS pool/object naming.

## Risks and Edge Cases

Changing field order, endianness, packing, enum values, or message ids is wire-incompatible. Several variable-length structs are followed by arrays/strings/blobs, so decoders must validate bounds. Legacy and extended request heads must remain compatible, and capability masks must align with MDS lock semantics.

## Test Signals

Signals include compile coverage for all CephFS protocol users, decode/encode round trips for request/reply structs, mixed-version client/server tests, layout conversion tests, MDS op name/cap mapping tests, and fuzzing of variable-length reply decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/ceph_fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/ceph_hash.h -->
# sources/distributed-fs/ceph-client/include/linux/ceph/ceph_hash.h

## Purpose

`ceph_hash.h` declares Ceph string hash algorithms used to map names into directory fragments and object placement inputs.

## Important APIs, Types, and Functions

It defines hash ids `CEPH_STR_HASH_LINUX` and `CEPH_STR_HASH_RJENKINS`, declares algorithm implementations `ceph_str_hash_linux()` and `ceph_str_hash_rjenkins()`, and exposes dispatcher/name helpers `ceph_str_hash()` and `ceph_str_hash_name()`.

## Control Flow

Callers select a hash id from metadata layout, then call `ceph_str_hash()` to dispatch to the matching implementation. The result is used by directory-fragment containment and lookup paths.

## State and Persistence Behavior

There is no local state, but hash algorithm ids are persistent metadata semantics. Changing an implementation would remap names and break directory lookup compatibility.

## Dependencies and Integration Points

It integrates with `ceph_frag.h`, `ceph_fs.h` directory layouts, MDS lookup/readdir operations, and any code interpreting `dl_dir_hash`.

## Risks and Edge Cases

Unknown hash ids must be handled by implementation code. The algorithm must be stable across architectures and builds. Name length must be passed explicitly, so embedded NUL bytes and non-NUL-terminated names depend on correct caller length handling.

## Test Signals

Test known vectors for both hash algorithms, unknown type behavior, hash name formatting, directory fragment mapping consistency, and cross-architecture result stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/ceph_hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/cls_lock_client.h -->
# sources/distributed-fs/ceph-client/include/linux/ceph/cls_lock_client.h

## Purpose

`cls_lock_client.h` declares the client-side interface to Ceph's RADOS object-class lock operations. It lets kernel clients acquire, release, break, inspect, and assert object locks through OSD class calls.

## Important APIs, Types, and Functions

Types include `enum ceph_cls_lock_type`, `ceph_locker_id`, `ceph_locker_info`, and `ceph_locker`. APIs are `ceph_cls_lock()`, `ceph_cls_unlock()`, `ceph_cls_break_lock()`, `ceph_cls_set_cookie()`, `ceph_cls_lock_info()`, `ceph_free_lockers()`, and `ceph_cls_assert_locked()`.

## Control Flow

The call path is OSD-client driven: callers pass an `osdc`, object id, object locator, lock name, cookie, tag, and type; the implementation constructs class method requests against the target object. `ceph_cls_assert_locked()` adds a class assertion operation to an existing OSD request.

## State and Persistence Behavior

The header itself stores no state. Lock state persists in RADOS object-class metadata on the OSD side. Returned locker arrays and strings are caller-owned until released with `ceph_free_lockers()`.

## Dependencies and Integration Points

It includes `osd_client.h` and therefore integrates with OSD request allocation, object ids, locators, entity names, and messenger delivery.

## Risks and Edge Cases

Cookie/tag/name strings are trust boundaries and must be encoded with correct lengths. Breaking locks requires identifying the existing locker accurately. Memory ownership of `tag` and `lockers` returned from info queries is a likely leak/double-free risk.

## Test Signals

Exercise exclusive/shared lock acquisition, unlock, break-lock, cookie replacement, lock-info decoding, assert-locked operation composition, and cleanup of returned locker arrays on success and error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/cls_lock_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/debugfs.h -->
# sources/distributed-fs/ceph-client/include/linux/ceph/debugfs.h

## Purpose

`debugfs.h` declares libceph debugfs lifecycle hooks for global Ceph debugfs setup and per-client debugfs entries.

## Important APIs, Types, and Functions

The API consists of `ceph_debugfs_init()`, `ceph_debugfs_cleanup()`, `ceph_debugfs_client_init()`, and `ceph_debugfs_client_cleanup()`.

## Control Flow

Global init/cleanup are called when the Ceph support module initializes and exits. Per-client init/cleanup are called as `struct ceph_client` instances are created and destroyed.

## State and Persistence Behavior

This header owns no state. Runtime state is held by debugfs dentries in `struct ceph_client` under `CONFIG_DEBUG_FS`, including monmap, osdmap, options, and client directories.

## Dependencies and Integration Points

It includes Ceph types and uses forward-declared `struct ceph_client` from includer context. It integrates with `libceph.h` fields and debugfs implementation code.

## Risks and Edge Cases

Debugfs is optional. Callers and implementations must handle disabled debugfs, partially initialized clients, and cleanup order so dentries are not removed after the client storage is gone.

## Test Signals

Build with and without `CONFIG_DEBUG_FS`, create/destroy clients repeatedly, inspect expected debugfs files, and run teardown paths after failed client initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/decode.h -->
# sources/distributed-fs/ceph-client/include/linux/ceph/decode.h

## Purpose

`decode.h` provides low-level little-endian encode/decode primitives and bounds-checking helpers for Ceph wire buffers. It also handles encoded strings, timespec conversion, entity address encoding, and versioned encoding blocks.

## Important APIs, Types, and Functions

Important helpers include `ceph_decode_64/32/16/8`, `ceph_decode_copy`, `ceph_has_room`, `ceph_decode_*_safe`, skip macros for primitive/string/set/map forms, `ceph_extract_encoded_string()`, `ceph_decode_timespec64()`, `ceph_encode_timespec64()`, banner address helpers, `ceph_decode_entity_addr()`, `ceph_decode_entity_addrvec()`, `ceph_encode_entity_addr()`, `ceph_encode_*`, `ceph_encode_filepath()`, `ceph_encode_string()`, `ceph_start_encoding()`, and `ceph_start_decoding()`.

## Control Flow

Encode/decode flow is pointer-cursor based: functions read or write at `*p` and advance it. Safe macros check `end` and branch to caller-supplied error labels. Versioned decode reads current version, compatible version, and length before allowing unsafe field reads within the validated block.

## State and Persistence Behavior

No state is stored here. The helpers define how persistent and network Ceph records are serialized. Allocated strings from `ceph_extract_encoded_string()` become caller-owned heap state.

## Dependencies and Integration Points

It depends on unaligned access helpers, `ERR_PTR`, slab allocation, time types, and `ceph/types.h`. It is used by monitor map, OSD map, messenger address, and protocol decoder implementations.

## Risks and Edge Cases

Unsafe decode helpers do not check bounds. `ceph_encode_filepath()` and `ceph_encode_string()` use `BUG_ON` on overflow, making caller length calculation critical. Timespec encoding truncates seconds to 32 bits with a documented year-2106 overflow. String allocation must account for `len + 1` overflow risk in implementation assumptions.

## Test Signals

Fuzz truncated buffers, verify safe macros branch on short input, test version/compat rejection, round-trip entity addresses and strings, cover zero-length strings, and run endian/unaligned access tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/decode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/libceph.h -->
# sources/distributed-fs/ceph-client/include/linux/ceph/libceph.h

## Purpose

`libceph.h` is the central kernel libceph client interface. It defines mount/options state, the shared `ceph_client` object, snapshot contexts, common red-black-tree helper macros, slab/mempool globals, client lifecycle APIs, session APIs, and page-vector helpers.

## Important APIs, Types, and Functions

Key types are `ceph_options`, `ceph_client`, `ceph_snap_context`, and the generated RB helper macros `DEFINE_RB_*`. Important APIs include `ceph_alloc_options()`, `ceph_parse_mon_ips()`, `ceph_parse_param()`, `ceph_create_client()`, `ceph_destroy_client()`, `ceph_open_session()`, `ceph_wait_for_latest_osdmap()`, snap-context get/put/create helpers, `calc_pages_for()`, and page-vector allocation/copy/zero/release functions.

## Control Flow

Client setup flows from option parsing to `ceph_create_client()`, messenger/monitor/OSD client initialization, and `ceph_open_session()`. Runtime operations dispatch through monitor and OSD clients embedded in `ceph_client`; cleanup releases options, sessions, messenger state, caches, and debugfs entries.

## State and Persistence Behavior

`ceph_client` holds per-cluster client state: FSID, options, auth wait state, supported/required features, messenger, monitor client, OSD client, and debugfs dentries. `ceph_snap_context` is refcounted and attached to dirty pages to preserve write snapshot context.

## Dependencies and Integration Points

It includes Ceph messenger, msgpool, monitor, OSD, filesystem protocol, and string-table headers plus VFS/writeback/page-cache primitives. It is the integration root for CephFS and RBD-like kernel clients using libceph.

## Risks and Edge Cases

Option comparison only covers fields before the pointer section unless updated. Shared clients require mount option identity to be correct. Snap contexts are flexible-array refcounted objects and can leak or use-after-free if page ownership is wrong. RB macros `BUG()` on duplicate insertion when using strict insert helpers.

## Test Signals

Exercise option parsing/printing/comparison, shared-client reuse, failed session open unwinding, snap-context refcounting, page-vector boundary calculations, RB helper duplicate handling, and debugfs-enabled/disabled client lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/libceph.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/messenger.h -->
# sources/distributed-fs/ceph-client/include/linux/ceph/messenger.h

## Purpose

`messenger.h` defines libceph's in-kernel messaging runtime: connection callbacks, message payload abstractions, message objects, v1/v2 connection state, crypto framing state, ordered send/ack queues, and public connection/message APIs.

## Important APIs, Types, and Functions

Important types include `ceph_connection_operations`, `ceph_messenger`, `ceph_msg_data`, `ceph_msg_data_cursor`, `ceph_msg`, `ceph_connection_v1_info`, `ceph_connection_v2_info`, and `ceph_connection`. Public APIs cover connection flags, socket/session reset, data cursor iteration, CRC, address parsing/printing, messenger init/fini, connection open/close/send/keepalive, message allocation/refcounting/revocation, and data attachment helpers for pages, pagelists, bio, bvecs, and `iov_iter`.

## Control Flow

Connections transition through closed/preopen, v1 banner/connect or v2 banner/hello/auth/session states, then open/standby. Workqueue-driven read/write handlers process frames, allocate incoming messages through callbacks, dispatch messages, maintain ordered out queues and sent-but-unacked lists, and use reconnect sequence state to preserve lossless delivery unless the connection is marked lossy.

## State and Persistence Behavior

State is in `ceph_messenger` global sequence counters and each `ceph_connection`: peer identity/address/features, socket, flags, queues, sequence numbers, active messages, CRCs, keepalive timestamps, delayed work, backoff delay, and protocol-specific v1/v2 scratch state. No disk persistence is owned.

## Dependencies and Integration Points

It depends on networking, crypto, workqueues, block/bvec APIs, page/pagelist buffers, and `ceph/types.h`. It integrates with monitor and OSD clients through callback tables and with `msgr.h` wire headers.

## Risks and Edge Cases

Concurrency is high-risk: queue, refcount, socket, delayed work, and reconnect state must stay consistent. v2 secure mode adds GCM/HMAC nonce and buffer lifetime concerns. Data cursors must not overrun page/bio/bvec/iov boundaries. Lossless reconnection handling must discard only acknowledged or safely requeued messages.

## Test Signals

Run messenger v1/v2 connection tests, forced reconnect and peer reset tests, lossy channel behavior, keepalive expiry, payload cursor tests for every data type, CRC/signature failures, secure-mode crypto tests, and stress tests under socket close races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/messenger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/mon_client.h -->
# sources/distributed-fs/ceph-client/include/linux/ceph/mon_client.h

## Purpose

`mon_client.h` declares the monitor client that manages monitor maps, authentication, subscriptions, generic monitor requests, statfs/version queries, and monitor session hunting.

## Important APIs, Types, and Functions

Key types are `ceph_monmap`, `ceph_mon_request`, `ceph_mon_generic_request`, and `ceph_mon_client`. APIs include `ceph_monc_init()`, `ceph_monc_stop()`, `ceph_monc_reopen_session()`, map subscription helpers `ceph_monc_want_map()`, `ceph_monc_got_map()`, `ceph_monc_renew_subs()`, `ceph_monc_wait_osdmap()`, statfs/version/blocklist operations, `ceph_monc_open_session()`, and `ceph_monc_validate_auth()`.

## Control Flow

The monitor client opens a messenger connection to a selected monitor, hunts among monitor addresses on failures, authenticates, sends subscriptions for monmap/osdmap/fsmap/mdsmap, renews subscriptions, and tracks generic requests in an RB tree keyed by tid until replies complete.

## State and Persistence Behavior

Runtime state includes the current `ceph_monmap`, auth client and auth messages, pending auth flag, hunt state/backoff multiplier, current monitor index, subscription epochs, generic request tree, last tid, and per-client debugfs file. Persistent cluster identity comes from monitor maps and FSID validation.

## Dependencies and Integration Points

It includes `messenger.h` and works inside `ceph_client`. It drives OSD map freshness for `osd_client.h`, auth handshakes for messenger connections, and monitor wire structs from `ceph_fs.h`.

## Risks and Edge Cases

Hunt/backoff and subscription renewal can stall map progress if delayed work is mishandled. Generic request lifetime spans messages, completions, callbacks, and RB tree removal. Auth validation failures must wake waiters. Monitor maps with changing membership require safe reconnection.

## Test Signals

Exercise monitor failover, auth success/failure, subscription renewal, waiting for target OSD epochs, statfs/version synchronous and async requests, blocklist command construction, and request timeout/unwind behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/mon_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/msgpool.h -->
# sources/distributed-fs/ceph-client/include/linux/ceph/msgpool.h

## Purpose

`msgpool.h` defines a small wrapper around kernel mempools for preallocating Ceph messages that may be needed in receive or low-memory paths.

## Important APIs, Types, and Functions

`struct ceph_msgpool` records a pool name, backing `mempool_t`, preallocated message type, front length, and max data items. APIs are `ceph_msgpool_init()`, `ceph_msgpool_destroy()`, `ceph_msgpool_get()`, and `ceph_msgpool_put()`.

## Control Flow

Owners initialize a pool with message shape and size, get messages for matching incoming/outgoing paths, and return them when message processing is done. `ceph_msg` records its pool so put paths can return pooled allocations appropriately.

## State and Persistence Behavior

Runtime state is the mempool and its preallocated elements. There is no persistent state.

## Dependencies and Integration Points

It depends on `linux/mempool.h` and forward use of `struct ceph_msg`. It integrates with messenger allocation and OSD client `msgpool_op`/`msgpool_op_reply`.

## Risks and Edge Cases

Requested front length or data item count larger than the pool shape may require fallback allocation or fail depending on implementation. Pool destruction must happen after all borrowed messages are returned.

## Test Signals

Test init/destroy, get/put under allocation pressure, oversized request behavior, pool-backed `ceph_msg_put()` return paths, and OSD client shutdown with active pooled messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/msgpool.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/msgr.h -->
# sources/distributed-fs/ceph-client/include/linux/ceph/msgr.h

## Purpose

`msgr.h` defines Ceph messenger wire-level constants and packed message structures: banners, msgr2 feature bits, entity names and addresses, v1 connection tags, connect request/reply structs, message headers, priorities, and footers.

## Important APIs, Types, and Functions

Important definitions include `CEPH_BANNER`, `CEPH_BANNER_V2`, `CEPH_MSGR2_SUPPORTED_FEATURES`, `ceph_seq_t`, `ceph_seq_cmp()`, `ceph_entity_name`, `ceph_entity_addr`, `ceph_entity_inst`, `ceph_msg_connect`, `ceph_msg_connect_reply`, `ceph_msg_header_old`, `ceph_msg_header`, `ceph_msg_header2`, `ceph_msg_footer_old`, and `ceph_msg_footer`.

## Control Flow

Wire negotiation starts with banner exchange, then connect request/reply tags such as READY, RESETSESSION, RETRY_SESSION, RETRY_GLOBAL, FEATURES, or auth challenges. Message transfer uses headers, payload sections, and footers with CRC/signature flags.

## State and Persistence Behavior

No local mutable state exists. The constants are persistent network ABI. Sequence comparison is rollover-safe for 32-bit connection sequence numbers.

## Dependencies and Integration Points

It is included by `ceph_fs.h`, `decode.h`, `rados.h`, and `messenger.h`. It is the low-level contract consumed by messenger v1/v2 implementations and address encoding code.

## Risks and Edge Cases

Packed struct changes are wire breaks. Header old/new/header2 variants must be selected by protocol version correctly. `ceph_addr_equal_no_type()` ignores address type intentionally; callers needing msgr1/msgr2 distinction must not use it. CRC/signature flags must match payload handling.

## Test Signals

Validate banner parsing, connect tag handling, header/footer size and field offsets, sequence rollover comparisons, CRC/signature flag behavior, and mixed msgr1/msgr2 negotiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/msgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/osd_client.h -->
# sources/distributed-fs/ceph-client/include/linux/ceph/osd_client.h

## Purpose

`osd_client.h` declares the libceph OSD client: request construction, object targeting, OSD connection state, sparse-read handling, linger/watch/notify support, backoff tracking, map handling, and request lifecycle APIs.

## Important APIs, Types, and Functions

Key types include `ceph_sparse_extent`, `ceph_sparse_read`, `ceph_osd`, `ceph_osd_data`, `ceph_osd_req_op`, `ceph_osd_request_target`, `ceph_osd_request`, `ceph_osd_linger_request`, `ceph_hobject_id`, `ceph_osd_backoff`, and `ceph_osd_client`. APIs cover setup/init/stop, map handling, aborts, request/op allocation and data attachment, class/xattr/copy/alloc-hint helpers, request start/cancel/wait/sync, class calls, watch/unwatch/notify/list-watchers, and sparse extent helpers.

## Control Flow

Callers allocate a request with one or more ops, initialize target object and op payloads, allocate messages, and start the request. The OSD client maps object locators to PGs and acting OSDs using the current osdmap, sends over per-OSD messenger connections, tracks in-flight requests by tid, handles replies/completions, and remaps/resends across OSD map changes. Linger requests keep watch/notify registrations alive across reconnects.

## State and Persistence Behavior

State spans current `ceph_osdmap`, OSD connection RB trees/LRU, request and linger RB trees, map-check queues, request tid counters, mempools, workqueues, timeout work, sparse-read parse state, and backoff mappings. Persistent effects are RADOS object mutations and watch registrations on OSDs.

## Dependencies and Integration Points

It depends on OSD maps, messenger, msgpool, auth, pagelist, snap contexts, inodes, block APIs, and RADOS op constants. It is the data path used by CephFS, RBD-like users, class-lock helpers, and monitor map updates.

## Risks and Edge Cases

Request lifetime is complex: krefs, completions, callbacks, mempool ownership, snap contexts, and message refs must align. Sparse-read replies can force extent-array reallocation and endian conversion. Map changes, full/paused flags, redirects, backoffs, and linger reconnects can cause duplicate, lost, or indefinitely paused requests if state transitions are wrong.

## Test Signals

Run read/write/truncate/class/xattr/copy ops, map-remap and resend tests, OSD down/up failover, linger watch notify reconnects, sparse-read decoding including realloc, timeout/abort paths, mempool pressure, and race tests around request cancel versus reply.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/osd_client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/osdmap.h -->
# sources/distributed-fs/ceph-client/include/linux/ceph/osdmap.h

## Purpose

`osdmap.h` declares the in-kernel representation and mapping helpers for Ceph OSD maps. OSD maps describe cluster membership, pool settings, CRUSH placement, temporary/upmap overrides, OSD addresses, and epoch-based changes.

## Important APIs, Types, and Functions

Key types are `ceph_pg`, `ceph_spg`, `ceph_pg_pool_info`, `ceph_object_locator`, `ceph_object_id`, `workspace_manager`, `ceph_pg_mapping`, `ceph_osdmap`, `ceph_osds`, `crush_loc`, and `crush_loc_node`. APIs include PG/SPG comparison, object locator and object id lifecycle helpers, map allocation/decode/incremental-apply/destroy, OSD state helpers, PG decode, PG split and interval-change checks, object-to-PG mapping, PG-to-acting/up OSD mapping, CRUSH location parsing/comparison, and pool lookup helpers.

## Control Flow

Monitor-delivered maps are decoded as full maps or incremental updates. OSD client request targeting calls object locator to PG mapping, then CRUSH/upmap/temp mapping to up/acting sets and primary selection. Map change helpers decide whether a request is in a new interval and must be resent.

## State and Persistence Behavior

`ceph_osdmap` stores FSID, epoch, timestamps, flags, OSD state/weight/address arrays, pool RB tree, temp/upmap RB trees, primary affinity, CRUSH map, and workspace manager. Object locators may own `ceph_string` namespace refs, and object ids may use inline or allocated name storage.

## Dependencies and Integration Points

It depends on RB trees, Ceph decode helpers, Ceph types, and CRUSH. It integrates with monitor map handling and OSD client targeting/resend logic.

## Risks and Edge Cases

Map decoding is untrusted input and must validate bounds and versions. Object ids can contain embedded NULs and must use length, not C-string assumptions. Pool type controls OSD shifting; unknown types `BUG()`. Incremental maps must preserve epoch monotonicity and free replaced dynamic state.

## Test Signals

Decode full and incremental maps, fuzz truncated map data, test object id inline/external transitions, namespace ref lifecycle, CRUSH/upmap/temp mapping, PG split detection, interval-change decisions, pool lookup, and CRUSH location parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/osdmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/pagelist.h -->
# sources/distributed-fs/ceph-client/include/linux/ceph/pagelist.h

## Purpose

`pagelist.h` defines a refcounted page-backed append buffer used by Ceph message and OSD class-operation encoding paths.

## Important APIs, Types, and Functions

`struct ceph_pagelist` holds a page list, mapped tail pointer, total length, remaining room, reserve/free-list state, and refcount. APIs are `ceph_pagelist_alloc()`, `ceph_pagelist_release()`, `ceph_pagelist_append()`, `ceph_pagelist_reserve()`, `ceph_pagelist_free_reserve()`, and inline little-endian encoders for 64/32/16/8-bit values and strings.

## Control Flow

Callers allocate a pagelist, optionally reserve page capacity, append raw bytes or encoded primitives, attach the pagelist to a Ceph message, and release it when no longer referenced.

## State and Persistence Behavior

Runtime state is the list of allocated pages, mapped tail, current length, reserve pages, and refcount. No disk persistence is owned, but bytes become wire payloads for Ceph messages.

## Dependencies and Integration Points

It depends on list, refcount, byteorder, and kernel page allocation. It integrates with messenger `CEPH_MSG_DATA_PAGELIST`, OSD request data, monitor commands, and class method payload construction.

## Risks and Edge Cases

Append/reserve error handling is critical under memory pressure. String encoding takes a `char *` plus explicit length and does not imply NUL termination. Lifetime must outlive any message data cursor using the pagelist.

## Test Signals

Test append across page boundaries, reserve/free-reserve accounting, primitive endian encoders, zero-length and multi-page strings, refcount release, and message send paths that consume pagelists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/pagelist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/rados.h -->
# sources/distributed-fs/ceph-client/include/linux/ceph/rados.h

## Purpose

`rados.h` defines shared RADOS object-store wire constants and operation formats: FSIDs, snapshots, time encoding, placement/pool/OSD flags, stable PG modulo, object operation codes, op mode/type helpers, op flags, xattr/watch/copy/backoff enums, and packed OSD op payload structs.

## Important APIs, Types, and Functions

Important types are `ceph_fsid`, `ceph_timespec`, `ceph_pg_v1`, `ceph_object_layout`, `ceph_eversion`, and `ceph_osd_op`. Important helpers/macros include `ceph_fsid_compare()`, `ceph_stable_mod()`, `__CEPH_FORALL_OSD_OPS`, generated `CEPH_OSD_OP_*` enum values, op type/mode helper functions, `ceph_osd_op_name()`, and `ceph_osd_watch_op_name()`.

## Control Flow

There is little executable flow beyond classification helpers. OSD-client code selects opcodes and flags, fills `ceph_osd_op` union fields according to opcode class, then sends them in OSD request messages. Stable modulo controls PG remapping behavior as PG counts grow.

## State and Persistence Behavior

The file owns no mutable state. Constants and packed structs are durable wire/storage ABI. Snapshot sentinels such as `CEPH_NOSNAP` and pool/OSD flags are interpreted by OSDs and clients across releases.

## Dependencies and Integration Points

It includes `msgr.h` and integrates with `osd_client.h`, `osdmap.h`, CephFS layouts, RBD-like object users, and user-space librados-compatible operation semantics.

## Risks and Edge Cases

The warning against using raw opcodes matters because some op behavior was redefined and helpers special-case `CALL`. Packed union interpretation must match opcode. Stable modulo requires a power-of-two-minus-one mask. Error aliases like `EOLDSNAPC` and `EBLOCKLISTED` map Ceph semantics onto Linux errno values.

## Test Signals

Check opcode/name tables, op type/mode helpers including `CALL`, packed struct layout, stable modulo vectors across PG-count transitions, watch/copy/xattr flag encoding, and mixed-version OSD operation compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/rados.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/string_table.h -->
# sources/distributed-fs/ceph-client/include/linux/ceph/string_table.h

## Purpose

`string_table.h` declares a shared interned string table for Ceph strings, primarily used for pool namespaces and other repeated names.

## Important APIs, Types, and Functions

`struct ceph_string` contains a `kref`, an RB-tree node or RCU head union, length, and flexible string bytes. APIs are `ceph_find_or_create_string()`, `ceph_release_string()`, `ceph_strings_empty()`, `ceph_get_string()`, `ceph_put_string()`, `ceph_compare_string()`, and `ceph_try_get_string()`.

## Control Flow

Callers find or create an interned string, take/drop krefs as ownership changes, compare by length and bytes, and use `ceph_try_get_string()` to safely acquire an RCU-protected pointer unless its refcount is already zero.

## State and Persistence Behavior

The backing implementation owns a global RB tree of interned strings. Individual strings are refcounted and released through RCU-safe teardown. No disk persistence is owned.

## Dependencies and Integration Points

It depends on kref, RB trees, RCU, and kernel string helpers. It integrates with `ceph_file_layout.pool_ns`, `ceph_object_locator.pool_ns`, OSD maps, and request targeting.

## Risks and Edge Cases

RCU users must not dereference after dropping protection without a kref. `ceph_compare_string(NULL, "", 0)` intentionally treats NULL as empty. Embedded NUL bytes are compared by explicit length but `strncmp` still works only over the provided length.

## Test Signals

Test interning deduplication, get/put release, `ceph_strings_empty()` after cleanup, RCU try-get races with release, NULL/empty comparisons, and namespace lifecycle through object locator copies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/string_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/striper.h -->
# sources/distributed-fs/ceph-client/include/linux/ceph/striper.h

## Purpose

`striper.h` declares helpers that map logical Ceph file byte ranges to RADOS object extents and map object extents back to file ranges according to a `ceph_file_layout`.

## Important APIs, Types, and Functions

Types include `ceph_object_extent`, callback type `ceph_object_extent_fn_t`, and `ceph_file_extent`. APIs are `ceph_calc_file_object_mapping()`, `ceph_file_to_extents()`, `ceph_iterate_extents()`, `ceph_extent_to_file()`, `ceph_get_num_objects()`, plus helpers `ceph_object_extent_init()` and `ceph_file_extents_bytes()`.

## Control Flow

Callers provide a layout and file offset/length. The striper computes object number, object offset, and contiguous length for each stripe/object piece, optionally allocates/list-links extents, invokes a callback for each mapped stripe unit, or reverses an object extent into file extents.

## State and Persistence Behavior

The header owns no state. `ceph_object_extent` instances are caller-allocated list nodes; mapping results reflect persistent file layout fields.

## Dependencies and Integration Points

It depends on list/types and forward-declared `ceph_file_layout` from `ceph_fs.h`. It integrates with CephFS read/write paths and OSD request construction.

## Risks and Edge Cases

Layout validation must happen before mapping. Arithmetic over large offsets, lengths, stripe counts, and object sizes can overflow if implementations are careless. Callback allocation failure must unwind partially built extent lists.

## Test Signals

Test stripe-unit boundaries, multi-object ranges, zero-length behavior, large offsets, reverse mapping, total byte accounting, invalid layout rejection by callers, and callback failure unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/striper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/types.h -->
# sources/distributed-fs/ceph-client/include/linux/ceph/types.h

## Purpose

`types.h` is a small umbrella for core Ceph kernel types that must be available before including `ceph_fs.h`.

## Important APIs, Types, and Functions

It includes foundational kernel and Ceph headers, then defines `struct ceph_vino` with inode and snapshot id, and `struct ceph_cap_reservation` with reserved and used capability counts.

## Control Flow

There is no runtime flow. The types are embedded in higher-level CephFS inode/capability code.

## State and Persistence Behavior

`ceph_vino` identifies a Ceph inode version in a snapshot context; it is value state copied through lookup and inode paths. `ceph_cap_reservation` tracks transient reservation accounting.

## Dependencies and Integration Points

It includes Linux networking/types/fcntl/string plus `ceph_fs.h`, `ceph_frag.h`, and `ceph_hash.h`. It is a common include for libceph and CephFS source files.

## Risks and Edge Cases

Include ordering is the main concern because the file exists partly to break dependency cycles. Snapshot sentinel values come from `rados.h` via `ceph_fs.h` and must be interpreted consistently.

## Test Signals

Build coverage for include order, inode lookup tests involving snapshot ids, and capability reservation accounting tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ceph/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cfag12864b.h -->
# sources/distributed-fs/ceph-client/include/linux/cfag12864b.h

## Purpose

`cfag12864b.h` declares the public interface for the Crystalfontz CFAG12864B 128x64 LCD driver.

## Important APIs, Types, and Functions

It defines geometry constants `CFAG12864B_WIDTH`, `HEIGHT`, `CONTROLLERS`, `PAGES`, `ADDRESSES`, and computed `CFAG12864B_SIZE`. It declares global framebuffer pointer `cfag12864b_buffer` and lifecycle/status functions `cfag12864b_enable()`, `cfag12864b_disable()`, and `cfag12864b_isinited()`.

## Control Flow

Clients check initialization, enable refreshing to claim/use the LCD, write pixels into `cfag12864b_buffer`, and disable refreshing when finished.

## State and Persistence Behavior

The global buffer is live driver state blitted to the LCD; its size is fixed by the geometry macros. Enable/disable manages runtime refresh ownership, not persistent storage.

## Dependencies and Integration Points

This header has no includes. It integrates with the LCD driver implementation and any auxiliary framebuffer or display clients using this specific panel.

## Risks and Edge Cases

`cfag12864b_buffer` is global mutable memory, so users must respect ownership from `enable()`. Buffer bounds are exactly `CFAG12864B_SIZE`; geometry assumptions are hard-coded. Return comments for `enable()` are easy to misread because nonzero means busy/failure.

## Test Signals

Test module initialization, enable/disable exclusivity, buffer size assumptions, refresh after writes to first/last bytes, and behavior when clients call APIs before initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cfag12864b.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cfi.h -->
# sources/distributed-fs/ceph-client/include/linux/cfi.h

## Purpose

`cfi.h` declares Clang Control Flow Integrity support hooks for reporting CFI failures, reading function type hashes, identifying trap sites, and finalizing module CFI metadata.

## Important APIs, Types, and Functions

Under `CONFIG_CFI`, it exposes `cfi_warn`, `report_cfi_failure()`, `report_cfi_failure_noaddr()`, `cfi_get_offset()`, `cfi_get_func_hash()`, and BPF hash symbols `cfi_bpf_hash` and `cfi_bpf_subprog_hash`. Under `CONFIG_ARCH_USES_CFI_TRAPS`, it declares `is_cfi_trap()` and possibly `module_cfi_finalize()`. Fallback stubs return neutral values when features are disabled.

## Control Flow

When an indirect-call CFI check fails, architecture trap or bug handling calls the report helpers. Hash lookup reads the compiler-emitted KCFI type id located before a function entry, with architecture overrides allowed for nondefault prefix offsets. Module load may finalize CFI trap metadata.

## State and Persistence Behavior

Runtime state includes `cfi_warn` policy, read-only type hash symbols, and module CFI metadata. No filesystem persistence is owned.

## Dependencies and Integration Points

It includes bug handling, module declarations, and architecture CFI hooks. It integrates with compiler-emitted KCFI metadata, BPF indirect call checks, module loading, and architecture exception handling.

## Risks and Edge Cases

`cfi_get_func_hash()` reads memory before a function pointer and returns zero on fault; wrong architecture offset breaks hash matching. Disabled-config stubs must compile away safely. Module finalization is architecture-dependent.

## Test Signals

Build with and without `CONFIG_CFI`, test deliberate CFI failures in warn/panic modes, validate BPF type hashes, load/unload modules with CFI traps, and check hash reads for valid and invalid function pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cfi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cfi_types.h -->
# sources/distributed-fs/ceph-client/include/linux/cfi_types.h

## Purpose

`cfi_types.h` provides macros for annotating assembly functions and exporting CFI type identifiers so Clang KCFI can validate indirect calls involving assembly or special call targets.

## Important APIs, Types, and Functions

For assembly, it defines `__CFI_TYPE`, `SYM_TYPED_ENTRY`, `SYM_TYPED_START`, and `SYM_TYPED_FUNC_START`. For C under `CONFIG_CFI`, `DEFINE_CFI_TYPE(name, func)` emits a read-only-after-init `u32` initialized from `__kcfi_typeid_<func>` and forces the function to be addressable.

## Control Flow

There is no normal runtime flow. The macros affect assembly symbol layout and C object emission at compile/link time so runtime CFI checks can compare type ids.

## State and Persistence Behavior

The generated type-id objects live in `.data..ro_after_init`. Assembly annotations place a 4-byte type id before typed entry points when CFI is enabled.

## Dependencies and Integration Points

Assembly mode includes `linux/linkage.h`. C mode depends on compiler-generated `__kcfi_typeid_*` symbols and `__ADDRESSABLE`. It integrates with low-level architecture entry code, BPF, and other indirectly called assembly routines.

## Risks and Edge Cases

Missing annotations on indirectly called assembly functions can trigger CFI failures. Symbol names must match compiler-visible declarations. Section and alignment changes can break architecture expectations.

## Test Signals

Build assembly-heavy configurations with `CONFIG_CFI`, inspect emitted type ids, run indirect-call paths into annotated assembly, and test disabled-CFI builds where macros should reduce to normal symbol starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cfi_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cgroup-defs.h -->
# sources/distributed-fs/ceph-client/include/linux/cgroup-defs.h

## Purpose

`cgroup-defs.h` contains the core cgroup data model: subsystem ids, flags, cgroup roots, per-subsystem state, css sets, recursive statistics state, freezer state, controller file definitions, controller callback tables, and socket cgroup data.

## Important APIs, Types, and Functions

Key types include `cgroup_subsys_state`, `css_set`, `css_rstat_cpu`, `cgroup_rstat_base_cpu`, `cgroup_freezer_state`, `cgroup`, `cgroup_root`, `cftype`, `cgroup_subsys`, `cgroup_file`, `sock_cgroup_data`, and `cgroup_of_peak`. Important constants cover CSS flags, cgroup flags, root flags, cftype flags, attach lock modes, max name sizes, and subsystem enumeration generated from `cgroup_subsys.h`. Inline helpers manage threadgroup change locking and socket cgroup fields.

## Control Flow

The header describes cgroup lifecycle flow rather than implementing it: css allocation/online/offline/free callbacks, task migration attach callbacks, fork/exit callbacks, controller file read/write callbacks, recursive stat propagation, and freezer accounting. Threadgroup change helpers acquire global and optional per-threadgroup read semaphores.

## State and Persistence Behavior

Runtime state is extensive: hierarchy topology, kernfs nodes, task css sets, subsystem states, per-cpu stats, freezer timing, BPF storage, PSI files, pidlists, release-agent work, and socket classification fields. Userspace-visible persistence is the cgroupfs hierarchy while mounted; kernel objects are RCU/refcount managed.

## Dependencies and Integration Points

It depends on lists, IDR, wait queues, RCU, refcounts, percpu refs/rwsems, sched, stats sync, workqueues, BPF cgroup definitions, and PSI. It is included by `cgroup.h` and every controller implementation.

## Risks and Edge Cases

Locking is subtle: fields are variously protected by `cgroup_mutex`, `css_set_lock`, RCU, percpu refs, or subsystem locks. Flexible arrays and embedded root cgroup layout constrain allocation. Controller callbacks must honor online/offline and threaded/default hierarchy rules. Socket fields compile differently by config.

## Test Signals

Run cgroup v1/v2 hierarchy creation/removal, task migration, controller enable/disable, recursive stats flush, freezer operations, BPF attachment, socket classid/prio tests, lockdep, KASAN, and config-matrix builds with controllers disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cgroup-defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cgroup.h -->
# sources/distributed-fs/ceph-client/include/linux/cgroup.h

## Purpose

`cgroup.h` is the public kernel interface to cgroup core. It declares controller registration/file APIs, task migration and fork/exit hooks, css/cgroup iteration and lookup helpers, refcount accessors, path/name helpers, recursive accounting hooks, freezer hooks, socket cgroup hooks, and disabled-config stubs.

## Important APIs, Types, and Functions

Important APIs include `cgroup_on_dfl()`, css lookup/get helpers, cgroup get-from-path/fd/id helpers, attach/transfer functions, cftype add/remove and file notification helpers, fork/cancel/post/exit/dead/release/free hooks, init functions, task iterators, descendant iteration macros, `cgroup_css()`, css online/dying tests, `task_css*` helpers, `task_get_css()`, ancestry helpers, cgroup path/name helpers, rstat/accounting functions, freezer functions, BPF ref helpers, and `task_get_cgroup1()`.

## Control Flow

Kernel lifecycle flow calls cgroup hooks during fork, post-fork, exit, task release, and free. Controllers iterate tasksets and css descendants under documented locking. Accounting paths charge CPU time through cpuacct and default hierarchy stats. Freezer paths enter/leave frozen state and migrate freezer accounting during task movement.

## State and Persistence Behavior

The header manipulates state declared in `cgroup-defs.h`: css refs, task css_set pointers, default hierarchy membership, kernfs ids, recursive stats, freezer flags, and BPF refs. Disabled `CONFIG_CGROUPS` stubs return neutral behavior.

## Dependencies and Integration Points

It includes scheduler, nodemask, kernfs, namespaces, notifier, user namespace, stats, and cgroup definition/namespace headers. It is used by controllers, scheduler, fork/exit code, procfs, networking, BPF, and namespace code.

## Risks and Edge Cases

Many helpers require `cgroup_mutex`, RCU, or task locks; misuse can produce stale css pointers. Iterators may see offline or not-yet-online csses unless controllers synchronize. `task_get_css()` can return offline css for exiting tasks by design. Disabled-config stubs can hide missing coverage if code assumes real hierarchy behavior.

## Test Signals

Use lockdep-enabled task migration and controller attach tests, css iterator tests under concurrent cgroup deletion, fork/exit hook tests, CPU accounting validation, namespace path tests, freezer migration tests, BPF refcount tests, and builds with `CONFIG_CGROUPS=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cgroup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cgroup_api.h -->
# sources/distributed-fs/ceph-client/include/linux/cgroup_api.h

## Purpose

`cgroup_api.h` is a compatibility shim that simply includes `linux/cgroup.h`.

## Important APIs, Types, and Functions

It declares no independent symbols. All visible API is inherited from `cgroup.h`.

## Control Flow

There is no control flow. Including this header is equivalent to including the main cgroup interface.

## State and Persistence Behavior

No state is owned here.

## Dependencies and Integration Points

Its only dependency and integration point is `linux/cgroup.h`. It likely preserves include compatibility for code that still includes `cgroup_api.h`.

## Risks and Edge Cases

The risk is include indirection: changes to `cgroup.h` affect all users, and removing this shim can break out-of-tree or older in-tree includes.

## Test Signals

Compile users that include `cgroup_api.h` directly, both with cgroups enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cgroup_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cgroup_dmem.h -->
# sources/distributed-fs/ceph-client/include/linux/cgroup_dmem.h

## Purpose

`cgroup_dmem.h` declares device-memory cgroup accounting hooks for registering memory regions, charging/uncharging allocations, and choosing eviction targets when a cgroup limit is hit.

## Important APIs, Types, and Functions

Opaque types are `dmem_cgroup_region` and `dmem_cgroup_pool_state`. Enabled APIs are `dmem_cgroup_register_region()`, `dmem_cgroup_unregister_region()`, `dmem_cgroup_try_charge()`, `dmem_cgroup_uncharge()`, `dmem_cgroup_state_evict_valuable()`, and `dmem_cgroup_pool_state_put()`. Disabled stubs return success or neutral values.

## Control Flow

Device-memory providers register a region, try-charge a size before allocation, optionally receive pool/limit-pool state for eviction decisions, uncharge on free, and release pool-state references.

## State and Persistence Behavior

Implementation state is opaque and per cgroup/device-memory pool. The disabled path stores no state and sets returned pool pointers to NULL.

## Dependencies and Integration Points

It depends on types and lockless lists. It integrates with the cgroup subsystem when `CONFIG_CGROUP_DMEM` is enabled and with device drivers managing nonstandard/device memory.

## Risks and Edge Cases

Callers must handle enabled and disabled configurations identically. On disabled builds, `dmem_cgroup_state_evict_valuable()` returns true, so eviction policy must not assume real accounting. Returned pool references require matching put calls only when non-NULL.

## Test Signals

Build with and without `CONFIG_CGROUP_DMEM`, test charge/uncharge balance, region unregister with outstanding pools, limit-pool eviction decisions including low-protection hits, and disabled-stub behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cgroup_dmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cgroup_namespace.h -->
# sources/distributed-fs/ceph-client/include/linux/cgroup_namespace.h

## Purpose

`cgroup_namespace.h` defines cgroup namespace state and APIs for copying, referencing, freeing, and rendering cgroup paths relative to a namespace root.

## Important APIs, Types, and Functions

`struct cgroup_namespace` embeds `ns_common`, `user_namespace`, `ucounts`, and root `css_set`. APIs include `to_cg_ns()`, `free_cgroup_ns()`, `copy_cgroup_ns()`, `cgroup_path_ns()`, `get_cgroup_ns()`, and `put_cgroup_ns()`, with stubs when cgroups are disabled.

## Control Flow

Namespace copy occurs during clone/unshare depending on flags. Reference helpers increment/decrement namespace refs, freeing when the last ref drops. Path rendering converts a cgroup to a namespace-relative string.

## State and Persistence Behavior

Runtime namespace state records the user namespace, ucounts, and css_set root that defines visibility. It persists for the lifetime of namespace references.

## Dependencies and Integration Points

It depends on `ns_common` and integrates with user namespaces, nsproxy, cgroup core, procfs path display, and clone/unshare code.

## Risks and Edge Cases

Reference handling must pair `get_cgroup_ns()` and `put_cgroup_ns()`. Disabled cgroup stubs return the old namespace and do no ref work. Path rendering must enforce namespace boundaries.

## Test Signals

Test clone/unshare cgroup namespace, namespace-relative `/proc/*/cgroup` paths, refcounted teardown, disabled-cgroup builds, and interactions with user namespace lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cgroup_namespace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cgroup_rdma.h -->
# sources/distributed-fs/ceph-client/include/linux/cgroup_rdma.h

## Purpose

`cgroup_rdma.h` declares RDMA controller accounting for HCA handles and HCA objects per cgroup.

## Important APIs, Types, and Functions

Resource ids are `RDMACG_RESOURCE_HCA_HANDLE`, `RDMACG_RESOURCE_HCA_OBJECT`, and `RDMACG_RESOURCE_MAX`. Under `CONFIG_CGROUP_RDMA`, types include `rdma_cgroup` and `rdmacg_device`, with APIs `rdmacg_register_device()`, `rdmacg_unregister_device()`, `rdmacg_try_charge()`, and `rdmacg_uncharge()`.

## Control Flow

RDMA devices register with the controller. RDMA/IB allocation paths call `rdmacg_try_charge()` before creating resources and call `rdmacg_uncharge()` on release.

## State and Persistence Behavior

Runtime state is per-cgroup `rdma_cgroup` css and per-device resource pools. No disk persistence is owned; limits and usage are exposed through cgroup controller files in implementation code.

## Dependencies and Integration Points

It includes `cgroup.h` and integrates with the RDMA/IB stack and cgroup controller core.

## Risks and Edge Cases

The header declares APIs only when enabled; callers must be config-guarded. Device unregister must coordinate with outstanding charged resources. Resource type indexes must remain aligned with controller files.

## Test Signals

Build with `CONFIG_CGROUP_RDMA`, register/unregister mock devices, charge/uncharge both resource types, test limit failures, and verify callers compile out or guard use when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cgroup_rdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cgroup_refcnt.h -->
# sources/distributed-fs/ceph-client/include/linux/cgroup_refcnt.h

## Purpose

`cgroup_refcnt.h` provides inline or debug-overridable reference helpers for `struct cgroup_subsys_state`.

## Important APIs, Types, and Functions

It defines `css_get()`, `css_get_many()`, `css_tryget()`, `css_tryget_online()`, `css_put()`, and `css_put_many()` using `percpu_ref` operations unless `CSS_NO_REF` is set. `CGROUP_REF_FN_ATTRS` and `CGROUP_REF_EXPORT` are supplied by the includer.

## Control Flow

Callers acquire references when they already hold or can safely access a css. Try-get helpers either acquire a live/offline-tolerant ref or report failure. Put helpers release one or more refs.

## State and Persistence Behavior

The helpers mutate the css percpu refcount. `CSS_NO_REF` csses skip reference accounting and always succeed for try-get.

## Dependencies and Integration Points

It is included from `cgroup.h` when `CONFIG_DEBUG_CGROUP_REF` is off; debug builds provide out-of-line versions. It depends on `cgroup_subsys_state`, CSS flags, and percpu ref APIs.

## Risks and Edge Cases

`css_tryget()` can succeed for offline csses; callers needing online state must use `css_tryget_online()`. The caller must ensure pointer accessibility, typically through RCU or an existing ref. Mispaired many/get puts corrupt lifetime.

## Test Signals

Use refcount debug builds, RCU lookup races, online/offline try-get tests, CSS_NO_REF subsystem behavior, and leak detection during cgroup deletion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cgroup_refcnt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cgroup_subsys.h -->
# sources/distributed-fs/ceph-client/include/linux/cgroup_subsys.h

## Purpose

`cgroup_subsys.h` is the authoritative macro list of cgroup subsystems compiled into the kernel. It is included with `SUBSYS(name)` defined to generate enum entries, extern declarations, and static keys.

## Important APIs, Types, and Functions

It conditionally emits `SUBSYS()` for cpuset, cpu, cpuacct, io, memory, devices, freezer, net_cls, perf_event, net_prio, hugetlb, pids, rdma, misc, dmem, and debug based on Kconfig options.

## Control Flow

There is no runtime flow. Preprocessor inclusion expands the subsystem list for different declaration contexts.

## State and Persistence Behavior

The generated order determines subsystem ids in `enum cgroup_subsys_id`, so it is a kernel-internal ABI for arrays sized by `CGROUP_SUBSYS_COUNT`.

## Dependencies and Integration Points

It is included by `cgroup-defs.h` and `cgroup.h`. It integrates all controller implementations with the cgroup core.

## Risks and Edge Cases

The file explicitly warns not to add subsystems without cgroup maintainer approval. Ordering changes affect subsystem ids and per-subsystem arrays. Some subsystems are not supported on the default hierarchy.

## Test Signals

Build config matrices with each controller enabled/disabled, verify `CGROUP_SUBSYS_COUNT`, controller registration, static keys, and cgroup v1/v2 exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cgroup_subsys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/circ_buf.h -->
# sources/distributed-fs/ceph-client/include/linux/circ_buf.h

## Purpose

`circ_buf.h` provides the kernel's simple power-of-two circular buffer struct and arithmetic macros.

## Important APIs, Types, and Functions

`struct circ_buf` contains `buf`, `head`, and `tail`. Macros are `CIRC_CNT()`, `CIRC_SPACE()`, `CIRC_CNT_TO_END()`, and `CIRC_SPACE_TO_END()`.

## Control Flow

Producers and consumers update head/tail externally, while macros compute used bytes, free bytes, and contiguous ranges before wraparound. One slot is intentionally left unused to distinguish full from empty.

## State and Persistence Behavior

State is only the caller-owned buffer pointer and head/tail indexes. There is no synchronization or persistence built in.

## Dependencies and Integration Points

It has no external dependencies. It is used by drivers and subsystems needing lightweight ring-buffer arithmetic.

## Risks and Edge Cases

`size` must be a power of two. Macros do not enforce memory barriers or locking; concurrent users must provide ordering. Full capacity is `size - 1`, not `size`. Head/tail expressions in `_TO_END` variants are carefully evaluated once; callers should preserve that property if wrapping.

## Test Signals

Test empty/full/one-less-than-full states, wraparound count/space, nonconcurrent producer/consumer behavior, and lockless users with required memory barriers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/circ_buf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cleanup.h -->
# sources/distributed-fs/ceph-client/include/linux/cleanup.h

## Purpose

`cleanup.h` implements scope-based cleanup, resource ownership transfer, and guard/lock helper macros using compiler cleanup attributes. It is intended to reduce goto-based unwind bugs and enforce LIFO cleanup ordering.

## Important APIs, Types, and Functions

Major macros are `DEFINE_FREE`, `__free`, `no_free_ptr`, `return_ptr`, `retain_and_null_ptr`, `DEFINE_CLASS`, `EXTEND_CLASS`, `CLASS`, `CLASS_INIT`, `scoped_class`, `DEFINE_GUARD`, `DEFINE_GUARD_COND`, `guard`, `ACQUIRE`, `ACQUIRE_ERR`, `scoped_guard`, `scoped_cond_guard`, `DEFINE_LOCK_GUARD_0/1`, `DEFINE_LOCK_GUARD_1_COND`, `DECLARE_LOCK_GUARD_*_ATTRS`, and `WITH_LOCK_GUARD_1_ATTRS`.

## Control Flow

Variables annotated with cleanup destructors run their cleanup at scope exit in reverse definition order. Guard macros acquire locks at declaration/construction and release them at cleanup. Scoped guard/class macros use a single-iteration `for` loop to bind lifetime to the following compound statement. Conditional guards skip or fail when acquisition does not succeed.

## State and Persistence Behavior

The macros create automatic variables, destructor wrappers, lock-class typedefs, and optional context-analysis aliases. They own no global state. Ownership transfer helpers null local variables so cleanup destructors do not free returned or consumed resources.

## Dependencies and Integration Points

It depends on compiler cleanup support, error-pointer helpers, argument-counting macros, and kernel type inference extensions. It integrates broadly with kernel resource-management patterns, locks, RCU/preempt guards, and static analysis annotations.

## Risks and Edge Cases

Definition order is semantic: resources acquired later are cleaned first. Mixing goto jumps with cleanup scopes can bypass intended structure and is discouraged. Top-of-function `__free(...)=NULL` can produce wrong lock/free order. Conditional guard error encoding must match `ACQUIRE_ERR()` expectations.

## Test Signals

Compile macro users under GCC and Clang, inspect generated cleanup ordering, test `return_ptr()` and `retain_and_null_ptr()` leak prevention, lockdep for guard scopes, conditional guard failure paths, and static analysis/context annotation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/cleanup.h -->
