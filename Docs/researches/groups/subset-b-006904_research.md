# Research: subset-b-006904

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Client.h -->
# sources/distributed-fs/ceph/src/client/Client.h

## Purpose
`Client.h` declares the main libcephfs client object, its public POSIX-like API, the lower-level ll_* API, metadata request/session/capability machinery, directory read state, client lifecycle state machines, and fscrypt-aware read/write helpers. It is the central integration point between callers, MDS metadata operations, OSD object IO, local metadata cache objects, snapshot realms, delegation state, and admin/perf interfaces.

## Important APIs, Types, and Functions
The public `Client` API mirrors filesystem syscalls: mount/unmount, path traversal, directory iteration, file open/read/write/fsync/fallocate/locks, xattrs, snapshots, stat/statx, layout queries, quota/auth checks, and MDS/OSD map exposure. The ll_* family exposes inode/file-handle oriented operations for FUSE and low-level users. `dir_result_t` stores readdir cursor state, cached entries, hash/frag ordering, and fdopendir linkage. `SubvolumeMetricTracker` maps inodes to subvolume IDs and aggregates IO metrics. `MDSCommandOp` extends `CommandOp` with MDS targeting. Nested context classes coordinate async read/write completion, nonblocking fsync, encrypted write read-modify-write, and finisher locking. `StandaloneClient` owns objecter setup around the base client.

## Control Flow
External operations enter through public wrappers, acquire lifecycle `RWRef` state checks, resolve paths through `walk`/`path_walk`, build `MetaRequest` instances for MDS operations, and update local cache/capability state from replies. File IO flows through `Fh` and `Inode` capability checks, `Filer`/`ObjectCacher`, `ObjecterWriteback`, and completion contexts. Directory iteration advances a `dir_result_t` across fragments, local cache, and MDS readdir requests. Mount/init and unmount/shutdown are serialized through `initialize_state` and `mount_state`, then drain sessions, requests, caps, finishers, and cache entries.

## State and Persistence Behavior
The header declares most in-memory client state: root/cwd refs, inode and fd maps, fake inode maps, MDS sessions, outstanding metadata requests, cap flush tids, snap realm map, metrics counters, timers, finishers, fscrypt object, pool permission cache, reclaim state, and dentry/cap/open metrics. Persistence is external: metadata and capabilities are authoritative on MDS, data lives in OSD objects, while this class holds transient cache, leases, dirty cap queues, writeback state, and request replay/reclaim bookkeeping. The `client_lock` protects most client/cache state; `timer_lock` protects timers, and `command_lock` protects MDS admin commands.

## Dependencies and Integration Points
This file depends on Ceph common utilities, messenger dispatch, mon/objecter/filer/object cacher, MDS message/types, low-level CephFS types, and client cache model classes (`Inode`, `Dentry`, `Dir`, `Fh`, `MetaRequest`, `MetaSession`, `SnapRealm`). Linux builds integrate `FSCrypt`. Admin socket commands, perf counters, FUSE callbacks, interrupt/remount callbacks, capability renewal, MDS map/session handling, and OSD map full-flag handling all converge here.

## Risks and Edge Cases
The class has high concurrency risk: lifecycle state, client_lock, timer_lock, finishers, callbacks, and async contexts must agree on ownership and completion order. Cache/cap code risks use-after-free if refs are not balanced across dentries, inodes, Fhs, snap realms, and requests. Readdir offsets encode frag/hash state and can regress if ordering assumptions change. Encrypted writes require block-aligned RMW and may need read caps during write. Unmount/reclaim paths must drain unsafe requests and release caps without losing dirty metadata. Fake inode mapping is sensitive on 32-bit ino_t clients.

## Test Signals
Useful coverage includes mount/unmount races with active IO, ll_* lifecycle refusal during mounting/unmounting, readdir cache and hash-order seeks, MDS failover/reconnect and unsafe request replay, cap grant/revoke/flush/snap flush, objecter writeback errors reflected through `Fh::async_err`, fscrypt reads/writes and name wrapping, callback invalidation paths, delegation timeout behavior, and admin/perf dump stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/ClientSnapRealm.cc -->
# sources/distributed-fs/ceph/src/client/ClientSnapRealm.cc

## Purpose
`ClientSnapRealm.cc` implements the client-side snapshot realm helpers declared in `ClientSnapRealm.h`. A `SnapRealm` collects the snapshots that affect a subtree by combining local snapshots, prior parent snapshots, and current parent realm snapshots.

## Important APIs, Types, and Functions
`SnapRealm::build_snap_context()` builds `cached_snap_context` from `prior_parent_snaps`, parent `SnapContext` entries newer than `parent_since`, and `my_snaps`, selecting the maximum sequence from the realm and parent. `SnapRealm::dump()` emits realm identity, refs, parentage, snapshot lists, and child realm IDs to a `Formatter`.

## Control Flow
The build path starts with a sorted `set<snapid_t>`, inserts prior parent snaps, optionally asks `pparent->get_snap_context()` for inherited snaps, filters inherited snaps by `parent_since`, inserts local snaps, then writes the output vector in descending order. `get_snap_context()` in the header calls this lazily when the cached sequence is zero.

## State and Persistence Behavior
The implementation only maintains transient client cache. Snapshot authority and realm update messages come from the MDS; this code materializes the currently known effective context for cap snapshots and data IO. Cache invalidation is explicit through `invalidate_cache()` in the header.

## Dependencies and Integration Points
It depends on `SnapContext` from common snapshot types and `Formatter` for diagnostics. `Client` snapshot update code owns parent/child relationships and invalidation; `Inode` cap-snap logic consumes the resulting contexts.

## Risks and Edge Cases
Missing invalidation after parent changes would leave stale inherited snapshots. Parent recursion depends on a valid realm tree without cycles. The descending snapshot order is deliberate; callers expecting Ceph snap context order would break if changed. Filtering by `parent_since` is the key correctness boundary for moved realms.

## Test Signals
Exercise parent realm changes, realm-local snapshots, prior parent snapshots, cache invalidation, dump output, and snap context ordering after MDS snap trace updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/ClientSnapRealm.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/ClientSnapRealm.h -->
# sources/distributed-fs/ceph/src/client/ClientSnapRealm.h

## Purpose
`ClientSnapRealm.h` defines `SnapRealm`, the client cache record for a snapshot realm. It tracks realm identity, parentage, snapshot membership, child realms, change attributes, snapdir visibility, and inodes whose caps are attached to the realm.

## Important APIs, Types, and Functions
The main type is `SnapRealm`. Fields include `ino`, `nref`, `created`, `seq`, `parent`, `parent_since`, `prior_parent_snaps`, `my_snaps`, `pparent`, `pchildren`, `last_modified`, `change_attr`, `is_snapdir_visible`, and `inodes_with_caps`. `get_snap_context()` lazily returns a cached `SnapContext`; `build_snap_context()` and `dump()` are implemented in the cc file. `operator<<` prints compact debug state.

## Control Flow
Client snap handling obtains or creates realms, links them into a parent/child tree, invalidates caches on updates, and asks `get_snap_context()` when cap snapshots or file IO need the effective snap context. The cached context is rebuilt only when its sequence is zero.

## State and Persistence Behavior
All state is volatile client metadata cache derived from MDS snap traces. The authoritative snapshot tree is not persisted here. `nref` and `inodes_with_caps` support local lifetime and cap flush interactions; parent/child pointers express the current client view of the realm tree.

## Dependencies and Integration Points
It depends on Ceph `types.h`, `snap_types.h`, `xlist`, and `Inode` forward declarations. `Client` owns the map of realms and updates, while `Inode` references a `SnapRealm` and links into `inodes_with_caps`.

## Risks and Edge Cases
The raw pointer parent/child graph requires disciplined unlinking. Cached context invalidation must propagate to children when inherited snapshots change. `is_snapdir_visible` affects user-visible namespace behavior and should track MDS policy exactly.

## Test Signals
Tests should inspect snap context cache rebuild, parent switches, child invalidation, snapdir visibility propagation, and no dangling `inodes_with_caps` links on inode release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/ClientSnapRealm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Delegation.cc -->
# sources/distributed-fs/ceph/src/client/Delegation.cc

## Purpose
`Delegation.cc` implements file delegation support. A delegation holds capability references on behalf of an application until the delegation is recalled, then enforces eventual return via a client timer.

## Important APIs, Types, and Functions
`ceph_deleg_caps_for_type()` maps `CEPH_DELEGATION_RD` and `CEPH_DELEGATION_WR` to required Ceph caps. `Delegation` construction/destruction gets and puts those cap refs on the inode. `reinit()` updates type/callback/private data. `recall()` invokes the application callback once and arms a timeout. `arm_timeout()` and `disarm_timeout()` schedule/cancel `C_Deleg_Timeout`.

## Control Flow
`Inode::set_deleg()` creates or reinitializes a `Delegation` after checking open conflicts and caps. Later conflicting opens or explicit recalls call `Delegation::recall()`. The callback is responsible for returning the delegation through client APIs; if not, `C_Deleg_Timeout::finish()` forcibly unmounts the client.

## State and Persistence Behavior
Delegation state is in-memory only: file handle pointer, private callback token, type, recall timestamp, and timer context. Capability refs are persistent only in the sense that they pin client-held MDS caps until released.

## Dependencies and Integration Points
The implementation depends on `Client`, `Inode`, `Fh`, `Timer`, and Ceph cap constants. It uses `client->timer_lock` and `client->timer`, and calls `Client::_unmount(false)` on timeout.

## Risks and Edge Cases
The timeout context stores a raw `Delegation*`; destruction must always cancel the timer before object lifetime ends. Recall callbacks run synchronously from recall path and can reenter upper layers. Timeout-triggered forced unmount is intentionally harsh and must only occur for enabled delegation timeouts. `ceph_deleg_caps_for_type()` aborts on unknown types.

## Test Signals
Cover read/write cap mapping, read-delegation skip behavior, reinit type changes, timer cancellation on return, timeout unmount, and conflicts with open-for-write/open-count logic in `Inode::set_deleg()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Delegation.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Delegation.h -->
# sources/distributed-fs/ceph/src/client/Delegation.h

## Purpose
`Delegation.h` declares the client-side delegation container and public delegation constants fallback. Delegations let applications rely on a set of caps until the client recalls them.

## Important APIs, Types, and Functions
The file defines `CEPH_DELEGATION_NONE`, `CEPH_DELEGATION_RD`, and `CEPH_DELEGATION_WR` when the public header has not already done so. `ceph_deleg_caps_for_type()` exposes cap calculation. `Delegation` exposes `get_fh()`, `get_type()`, `is_recalled()`, `is_write_delegated()`, `reinit()`, and `recall()`.

## Control Flow
Instances are owned by `Inode::delegations`. The inode creates them for successful delegation requests, invokes `recall()` on conflicting activity, and erases them on unset. The private timer helpers are used by `recall()` and the destructor.

## State and Persistence Behavior
The class stores only volatile process state: `Fh*`, callback private pointer, type, recall callback, recall time, and timeout event pointer. The associated cap refs are managed in the implementation and reflected in inode cap state.

## Dependencies and Integration Points
It depends on Ceph time/timer context and `ceph_ll_client.h` for callback and delegation command ABI. `Inode` and `Client` provide ownership and timer/cap integration.

## Risks and Edge Cases
The file does not own `Fh`; callers must ensure the file handle outlives the delegation. Callback and timeout lifetimes are tightly coupled. Tests should ensure duplicate declarations stay compatible with public headers.

## Test Signals
Compile-time ABI compatibility, delegation callback invocation, write delegation detection, recalled-state transition, and object lifetime under unset/close paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Delegation.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Dentry.cc -->
# sources/distributed-fs/ceph/src/client/Dentry.cc

## Purpose
`Dentry.cc` implements debug/dump/refcount glue for client metadata-cache dentries.

## Important APIs, Types, and Functions
`Dentry::dump()` emits name, parent dir inode, target inode, refcount, offset, lease data, and cap shared generation. `Dentry::print()` formats a compact debug representation including alternate encrypted name and rename state. `intrusive_ptr_add_ref()` and `intrusive_ptr_release()` adapt `Dentry` to `boost::intrusive_ptr`.

## Control Flow
Dump/print read current dentry fields without modifying state. Intrusive pointer add/release call `get()`/`put()`, which are defined inline in `Dentry.h` and handle LRU pinning and deletion.

## State and Persistence Behavior
No persistent state is written. This file surfaces volatile cache state: lease TTL/gen/seq, link target, refcount, and cap shared generation for diagnostics.

## Dependencies and Integration Points
It depends on `Dentry.h`, `Dir.h`, `Inode.h`, `Formatter`, and string escaping helpers. `DentryRef.h` relies on these intrusive pointer functions.

## Risks and Edge Cases
Debug code assumes `dir` and `dir->parent_inode` are valid while dumping. Printing binary/encrypted names uses bounded escaping, which is important for fscrypt alternate names.

## Test Signals
Use cache dump/admin output, intrusive pointer ref balance, formatted encrypted alternate names, and negative dentries with null inode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Dentry.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Dentry.h -->
# sources/distributed-fs/ceph/src/client/Dentry.h

## Purpose
`Dentry.h` defines the client metadata-cache dentry object that links a parent `Dir` name to an optional `Inode`, tracks leases and ordering offsets, and participates in the LRU cache.

## Important APIs, Types, and Functions
`Dentry` derives from `LRUObject`. Constructor inserts into `Dir::dentries` and starts as a null dentry. `get()`/`put()` manage refs and LRU pinning. `link()` attaches an `InodeRef` and links into the inode dentry xlist. `unlink()` detaches the inode and updates null counts. `mark_primary()`, `detach()`, `make_path_string()`, `dump()`, and `print()` support cache maintenance and diagnostics. Fields include `lease_mds`, `lease_ttl`, `lease_gen`, `lease_seq`, `cap_shared_gen`, `alternate_name`, and `is_renaming`.

## Control Flow
Client lookup/readdir paths create dentries, link them to inode traces, touch or trim them through LRU, and unlink/detach them on invalidation or cache eviction. Directory inodes pin their parent dentry while `inode->dir` or `ll_ref` is held, preventing directory ancestry from disappearing unexpectedly.

## State and Persistence Behavior
Dentries are transient cache entries. Lease fields cache MDS dentry lease validity and sequencing. Offset supports readdir ordering. `alternate_name` carries encrypted long-name backing data when fscrypt name wrapping needs a separate MDS field.

## Dependencies and Integration Points
It depends on `Dir`, `Inode`, `InodeRef`, MDS types, xlist, and LRU. `Client` owns link/unlink/trim policy and lease updates. `DentryRef` supplies intrusive pointer ownership.

## Risks and Edge Cases
Refcount transitions must match LRU pin/unpin expectations: `ref==1` means cached only, `ref>1` pinned. `unlink()` assumes an inode is present and its xlist link is still attached. `detach()` only applies after inode unlink. Directory dentry pinning must mirror `Inode::open_dir()` and ll refs or leaks/asserts can result.

## Test Signals
Lookup/link/unlink cycles, negative dentry trimming, directory open/close pin accounting, rename invalidation, dentry lease hit/miss behavior, encrypted alternate-name path reconstruction, and LRU eviction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Dentry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/DentryRef.h -->
# sources/distributed-fs/ceph/src/client/DentryRef.h

## Purpose
`DentryRef.h` defines the intrusive smart-pointer alias used for `Dentry` references.

## Important APIs, Types, and Functions
It forward-declares `Dentry`, declares `intrusive_ptr_add_ref(Dentry*)` and `intrusive_ptr_release(Dentry*)`, and aliases `DentryRef` to `boost::intrusive_ptr<Dentry>`.

## Control Flow
Any code that stores a `DentryRef` increments the embedded dentry refcount through the functions implemented in `Dentry.cc`; releasing the ref calls `Dentry::put()` and may delete the dentry.

## State and Persistence Behavior
No state is declared beyond ownership semantics. The referenced dentry remains an in-memory cache object.

## Dependencies and Integration Points
It depends only on Boost intrusive pointer. `MetaRequest`, `Client::walk_dentry_result`, and cache code use `DentryRef` to pin dentries across async request flow.

## Risks and Edge Cases
Because ownership uses dentry-internal refcounts, all raw-pointer users must avoid creating untracked lifetimes. The add/release functions must stay consistent with `Dentry::get()`/`put()`.

## Test Signals
Build/link tests for intrusive pointer symbols, request lifetime tests that pin dentries, and cache trim tests with outstanding `DentryRef`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/DentryRef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Dir.h -->
# sources/distributed-fs/ceph/src/client/Dir.h

## Purpose
`Dir.h` defines the small per-directory cache container owned by a directory inode.

## Important APIs, Types, and Functions
`Dir` stores `parent_inode`, an unordered map from names to `Dentry*`, `num_null_dentries`, and a `readdir_cache` vector. The constructor records the parent inode. `is_empty()` tests whether the dentry map is empty.

## Control Flow
`Inode::open_dir()` allocates `Dir` lazily for directory inodes. `Dentry` construction inserts into `dentries`, link/unlink updates null counts, and client readdir/cache paths use `readdir_cache` for ordered cached directory entries.

## State and Persistence Behavior
All state is volatile metadata cache. The MDS remains authoritative for directory contents, leases, and dirfrag mapping; this object holds the client-side materialized entries.

## Dependencies and Integration Points
It forward-declares `Dentry` and `Inode` and uses STL containers. `Client`, `Dentry`, and `Inode` coordinate its lifetime.

## Risks and Edge Cases
`parent_inode` is a raw pointer and must outlive the `Dir`. `num_null_dentries` must stay balanced with dentry link state. Readdir cache invalidation must track directory completeness and ordered flags in `Inode`.

## Test Signals
Directory open/close lifecycle, dentry map insert/erase accounting, null dentry counts, readdir cache invalidation, and cache trimming of empty dirs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Dir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/FSCrypt.cc -->
# sources/distributed-fs/ceph/src/client/FSCrypt.cc

## Purpose
`FSCrypt.cc` implements Linux-only fscrypt support for libcephfs: kernel-compatible filename armoring, HKDF key derivation, key store management, OpenSSL cipher setup, filename/symlink encryption, file-data block encryption/decryption, and preparation for encrypted reads.

## Important APIs, Types, and Functions
Name armoring is handled by `fscrypt_fname_armor()` and `fscrypt_fname_unarmor()` over a kernel-compatible base64 alphabet. HKDF is implemented by `fscrypt_calc_hkdf()` using HMAC-SHA512 extract/expand. `FSCryptKey::init()` derives the key identifier and stores the raw key. `FSCryptKeyStore::{create,find,invalidate}` manage master keys, users, epochs, present flags, and decrypted inode tracking. `FSCryptDenc` sets up OpenSSL EVP ciphers, derives per-file keys, and encrypts/decrypts buffers. `FSCryptFNameDenc` encrypts/decrypts filenames and symlinks, including alternate-name handling for long encrypted names. `FSCryptFDataDenc` encrypts/decrypts block-aligned file data. `FSCrypt::init_ctx()`, `get_fname_denc()`, `get_fdata_denc()`, and `prepare_data_read()` are the main facade methods.

## Control Flow
Keys are added to `FSCryptKeyStore`, which derives an identifier and either creates or refreshes a handler. An inode decodes `fscrypt_auth` into an `FSCryptContext`; callers request a name or data denc, which resolves the master key, snapshots its epoch in an optional validator, configures the OpenSSL cipher, and derives a per-file key. Filename encryption pads plaintext, encrypts, hashes overflow bytes into a short no-hash name when needed, armors the result, and may retain alternate ciphertext. Data encryption expands writes to full fscrypt blocks and encrypts each block with an IV based on block number. Data decryption walks target blocks, treats recorded or zero-detected holes as zeroes, decrypts non-hole chunks, and splices requested ranges into the output.

## State and Persistence Behavior
The key store is process-local and guarded by shared mutexes. It tracks key handler epoch changes so validators can detect stale derived ciphers. `fscrypt_auth` and `fscrypt_file` are persisted as inode metadata by higher layers/MDS; this file encodes/decodes contexts and effective encrypted size but does not persist by itself. Key invalidation may leave handlers present=false with files busy until decrypted inode tracking empties.

## Dependencies and Integration Points
It depends on Ceph crypto wrappers, OpenSSL EVP/provider APIs, fscrypt uapi definitions, `bufferlist`, Ceph logging, and `CephContext` randomness. `Inode` initializes contexts and inherited auth, while `Client` path and IO operations call name/data denc helpers.

## Risks and Edge Cases
Compatibility with Linux fscrypt format is critical: base64 alphabet, HKDF info string, padding, CTS mode, IV generation, and key identifier derivation must match kernel expectations. Stack variable-length arrays are used for padded names and symlinks. Long encrypted names require correct alternate-name storage or decryption cannot recover original names. Hole detection uses both supplied hole segments and zero checks. `FSCryptKeyHandler::reset()` assumes an existing key before zeroing; invalidation paths must avoid null dereferences. OpenSSL cipher fetch return values and provider availability are operational risks.

## Test Signals
Round-trip filename, long filename alternate-name, symlink, and file-data encryption/decryption against kernel fscrypt vectors. Test key add/remove with multiple users, busy-file invalidation flags, stale key validator behavior, sparse encrypted reads, partial-block writes, unsupported policy/cipher modes, missing key behavior, and provider failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/FSCrypt.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/FSCrypt.h -->
# sources/distributed-fs/ceph/src/client/FSCrypt.h

## Purpose
`FSCrypt.h` declares Linux-only fscrypt constants, helper functions, policy/context encoding, key store objects, encryption/decryption classes, and the `FSCrypt` facade used by `Client` and `Inode`.

## Important APIs, Types, and Functions
Constants define nonce size, HKDF contexts, 4 KiB block geometry, alignment, and maximum IO size. Inline helpers compute block starts, block numbers, offsets, alignment, and hex output. `ceph_fscrypt_key_identifier`, `FSCryptKey`, `FSCryptPolicy`, and `FSCryptContext` model key IDs and encoded policy/context metadata. `FSCryptDenc` is the abstract cipher base; `FSCryptFNameDenc` and `FSCryptFDataDenc` specialize name/symlink and data encryption. `FSCryptKeyHandler`, `FSCryptKeyStore`, and `FSCryptKeyValidator` manage master keys and epoch validity. `FSCrypt` initializes contexts and returns denc instances.

## Control Flow
Callers decode inode auth into an `FSCryptContext`, resolve a master key through `FSCryptKeyStore`, create the proper denc type, derive filename or data keys, then transform names or buffers. Policy encode/decode wraps a versioned envelope around fscrypt v2 fields plus context nonce.

## State and Persistence Behavior
Policy/context bytes are serializable into inode metadata. Key material and decrypted inode lists are memory-only and guarded by locks. `fscrypt_file` effective-size handling is on `Inode`, not in this header, but the data denc enforces block-aligned encrypted storage semantics.

## Dependencies and Integration Points
It depends on `fscrypt_uapi.h`, OpenSSL headers, Ceph mutexes and bufferlist, and Linux build guards. `Client.h` exposes fscrypt public APIs only on Linux and embeds an `FSCrypt` instance.

## Risks and Edge Cases
The declarations expose raw OpenSSL pointers and require destructor cleanup. Policy support is intentionally narrow: v2, AES-256-XTS contents, AES-256-CTS filenames. Callers must account for block alignment and missing keys. `FSCryptDecryptedInodes::open_inodes` is declared but not actively managed in visible code.

## Test Signals
Compile on Linux and non-Linux, policy encode/decode compatibility, key spec validation, denc setup for supported/unsupported ciphers, alignment helper boundary cases, and encrypted read/write max IO sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/FSCrypt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Fh.cc -->
# sources/distributed-fs/ceph/src/client/Fh.cc

## Purpose
`Fh.cc` implements construction/destruction of the client file-handle object.

## Important APIs, Types, and Functions
`Fh::Fh(InodeRef, int flags, int cmode, uint64_t gen, const UserPerm&)` stores immutable open identity, initializes readahead, and registers the handle with `inode->add_fh(this)`. `Fh::~Fh()` unregisters from the inode via `rm_fh()`.

## Control Flow
Client open paths allocate `Fh` after resolving and opening an inode. Close/release paths eventually destroy it after refs drop, which removes it from the inode’s `fhs` set so future async errors are not propagated to a dead handle.

## State and Persistence Behavior
No persistent state is written. The constructor/destructor update transient inode bookkeeping.

## Dependencies and Integration Points
It depends on `Inode.h` and `Fh.h`. `Client` owns fd map entries and file-handle refcounts; `Inode::set_async_err()` iterates registered Fhs.

## Risks and Edge Cases
The constructor assumes a valid inode ref. Destruction must happen after fd and ll references are gone and while inode state is still valid. Missing unregister would leave dangling Fh pointers in `Inode::fhs`.

## Test Signals
Open/close refcount tests, async writeback error propagation to active handles only, and leak/assert checks around release paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Fh.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Fh.h -->
# sources/distributed-fs/ceph/src/client/Fh.h

## Purpose
`Fh.h` declares the per-open file handle state used by high-level fd operations and low-level libcephfs APIs.

## Important APIs, Types, and Functions
`Fh` stores `InodeRef inode`, open `flags`, generation, opening `UserPerm`, refcount `_ref`, current `pos`, open `mode`, position lock/waiters, `Readahead`, POSIX/flock lock state, and `async_err`. `has_any_filelocks()`, `take_async_err()`, `get()`, and `put()` are the main helpers.

## Control Flow
Client open creates an `Fh`, fd maps point to it, read/write/lseek lock and update `pos`, readahead state feeds read scheduling, lock calls update file lock state, and close/release drops refs and cleans lock/delegation state.

## State and Persistence Behavior
The handle is volatile process state. File locks and open modes are coordinated with MDS state by `Client`/`Inode`, but the local structures are not persisted. `async_err` latches writeback errors until the next consumer calls `take_async_err()`.

## Dependencies and Integration Points
It depends on `Readahead`, `InodeRef`, `UserPerm`, and MDS lock definitions. `Client` manages fd maps and lock operations. `Delegation` holds an `Fh*`.

## Risks and Edge Cases
Position locking uses a boolean plus waiter list rather than a mutex object, so all callers must follow client locking protocol. Async errors must not be lost across fsync/close. File lock state must be released before handle destruction. Delegations require the `Fh` lifetime to exceed delegation lifetime.

## Test Signals
Concurrent read/write/lseek position behavior, readahead lifecycle, fsync/close async error delivery, file lock release on close, and fd generation reuse tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Fh.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Inode.cc -->
# sources/distributed-fs/ceph/src/client/Inode.cc

## Purpose
`Inode.cc` implements client inode cache behavior: debug output, path construction, open/cap ref accounting, cap validity and wanted masks, directory cache opening, permission bit checks, delegation coordination, dirty cap marking, fscrypt context inheritance, and effective encrypted-size helpers.

## Important APIs, Types, and Functions
The destructor asserts no leftover object-cache objects or delegations and unlinks cap/snap lists. `print()` and `dump()` expose inode/cache/cap/snap/open state. Path helpers are `make_long_path()`, `make_short_path()`, `make_path_string()`, and `make_nosnap_relative_path()`. Cap helpers include `get_cap_ref()`, `put_cap_ref()`, `caps_issued()`, `caps_issued_mask()`, `caps_used()`, `caps_file_wanted()`, `caps_wanted()`, `caps_dirty()`, and `get_best_perms()`. Delegation helpers include `recall_deleg()`, `break_deleg()`, `set_deleg()`, and `unset_deleg()`. Dirty state is handled by `mark_caps_dirty()` and `mark_caps_clean()`. Linux fscrypt helpers initialize/inherit contexts and manage effective size.

## Control Flow
Open paths call `get_open_ref()`, update metrics, and break conflicting delegations. Close paths call `put_open_ref()`. Capability checks first prefer valid snap/auth caps, then any valid cap, optionally implemented caps, touching cap LRU and updating hit/miss metrics. Dirty caps pin the inode and enqueue it in the auth session dirty list for later flush. Delegation setup verifies timeout enabled, no recalled delegations, open conflicts, and already-issued needed caps before creating or reinitializing a delegation.

## State and Persistence Behavior
This file manipulates volatile client cache state and dirty capability state that will later be flushed to MDS. Inode fields reflect authoritative metadata snapshots from MDS plus local dirty/flushing overlays. `cap_refs`, `open_by_mode`, `dirty_caps`, `flushing_caps`, `cap_snaps`, object cache set, and delegation list govern local lifetime and consistency. `fscrypt_file` may store the effective plaintext size when `Client::get_fscrypt_as()` is enabled.

## Dependencies and Integration Points
It depends on `Client`, `Dentry`, `Dir`, `Fh`, `MetaSession`, `ClientSnapRealm`, `Delegation`, MDS file lock/cap types, object cacher, and fscrypt on Linux. `Client` drives cap messages, request handling, flushing, and waiting; `MetaSession` owns dirty/flushing xlists.

## Risks and Edge Cases
Cap accounting is correctness-critical: issued versus implemented caps, auth-cap filtering during revocation, snap caps, and write-delegated buffer caps all affect cache validity. Dirty caps without auth cap are ignored with assertions on prior state, which matters during reconnect/rejection. `delegations_broken()` compares delegation type with `CEPH_FILE_MODE_RD`, which deserves scrutiny because delegation constants differ from file mode constants. Path building relies on first parent dentry and can fall back to ino paths for disconnected inodes. Fscrypt effective size uses raw little-endian storage in a byte vector.

## Test Signals
Cap hit/miss and validity tests across TTL/gen changes, open mode wanted caps including fscrypt write-read cap, dirty cap queueing/cleaning/flushing, delegation conflict and wait behavior, inode destruction leak assertions, path construction for linked/snapped/snapdir/disconnected inodes, async error propagation, and fscrypt effective size round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Inode.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Inode.h -->
# sources/distributed-fs/ceph/src/client/Inode.h

## Purpose
`Inode.h` declares the central client metadata-cache inode, its capability records, cap-snapshot records, flags, directory/object-cache state, fscrypt fields, delegation list, and helper APIs.

## Important APIs, Types, and Functions
`Cap` represents an MDS-issued cap for one inode/session. `CapSnap` snapshots dirty inode state for snapshot flushing. `Inode` stores identity (`ino`, `snapid`, fake ino), stat metadata, layout, size/truncate/time fields, recursive stats, xattrs, inline data, fscrypt metadata/context, directory cache (`Dir*`, frag trees/maps), caps/auth cap, dirty/flushing lists, snap realm, cap refs, object cache set, parent dentries, symlink, waiters, delegations, unsafe ops, active Fhs, and dir pin. Helpers cover path construction, refs, open refs, cap accounting, valid size, directory opening, async errors, dumping, charmap metadata, delegation, dirty caps, fscrypt inheritance, and effective size.

## Control Flow
MDS reply trace insertion populates/updates `Inode`. Dentries and file handles hold refs. Cap grants/revokes update `caps`, `auth_cap`, and wanted/dirty state. File IO checks caps and object cache state through this inode. Snapshot handling links it to a `SnapRealm` and may create `CapSnap` entries. Directory operations allocate `Dir` lazily and use frag maps for MDS targeting.

## State and Persistence Behavior
The inode mirrors persisted MDS metadata and OSD file layout, but the object itself is a transient cache record. Dirty caps, flushing tids, inline data, xattrs, fscrypt fields, and cap snaps represent local modifications pending MDS acknowledgement. `ObjectCacher::ObjectSet` ties file data cache/writeback to this inode.

## Dependencies and Integration Points
It depends on Ceph/MDS types, `ObjectCacher`, `MetaSession`, `UserPerm`, `Delegation`, `FSCrypt`, `InodeRef`, and request messages. `Client` is a friend-like owner through direct access and orchestrates most state transitions.

## Risks and Edge Cases
This is a dense ownership hub: raw pointers, intrusive refs, xlist items, object cache membership, and session cap lists must all be unwound in the right order. Directory hardlink assumptions are asserted. Cap ref and open mode maps default-insert entries in several helpers. Fscrypt is included unconditionally by this header but protected in parts by Linux guards, so platform compile coverage matters.

## Test Signals
Trace insertion/update, cap grant/revoke/import/export, dirty cap and cap snap flushing, inode ref/drop trimming, directory cache open/close, object cache cleanup, delegation lifecycle, file lock state, quota/charmap metadata, fscrypt metadata, and fake inode mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/Inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/InodeRef.h -->
# sources/distributed-fs/ceph/src/client/InodeRef.h

## Purpose
`InodeRef.h` defines the intrusive smart-pointer alias used to hold client inode refs.

## Important APIs, Types, and Functions
It forward-declares `Inode`, declares `intrusive_ptr_add_ref(Inode*)` and `intrusive_ptr_release(Inode*)`, and aliases `InodeRef` to `boost::intrusive_ptr<Inode>`.

## Control Flow
Any `InodeRef` increments/decrements the inode’s embedded refcount through functions implemented elsewhere. It is used in dentries, file handles, requests, snap dirs, roots, cwd, and many client helper results.

## State and Persistence Behavior
No state is persisted. The alias controls lifetime of in-memory inode cache records.

## Dependencies and Integration Points
It depends only on Boost intrusive pointer. `Client`, `Dentry`, `Fh`, `MetaRequest`, `Inode`, and `SnapRealm` all integrate this ownership model.

## Risks and Edge Cases
Raw `Inode*` and `InodeRef` are mixed heavily. Any raw pointer escaping without a corresponding ref can race trimming, while leaked refs keep cache and caps pinned.

## Test Signals
Inode trim with outstanding refs, low-level ll_get/ll_put behavior, file handle and dentry lifetime tests, and reconnect/unmount cache teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/InodeRef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/MetaRequest.cc -->
# sources/distributed-fs/ceph/src/client/MetaRequest.cc

## Purpose
`MetaRequest.cc` implements diagnostics and dentry setters for client metadata requests sent to MDS.

## Important APIs, Types, and Functions
`MetaRequest::dump()` emits request id, op, paths, inode/dentry targets, timestamps, MDS routing, retry/forward counters, unsafe status, caller/owner ids, release counts, flags, and abort code. `set_dentry()`, `dentry()`, `set_old_dentry()`, and `old_dentry()` manage intrusive dentry refs for primary and secondary paths.

## Control Flow
Client operation builders populate a `MetaRequest`, then `make_request()`/`send_request()` route it to an MDS. Admin/debug dumping can inspect live requests. Dentry setters assert they are only called once, making request construction order explicit.

## State and Persistence Behavior
Requests are transient in-memory records. Unsafe requests correspond to operations not yet safe on the MDS journal, but this file only reports that state.

## Dependencies and Integration Points
It depends on client cache types, MDS request/reply messages, and `Formatter`. `Client` owns request maps/lists and lifecycle, while `MetaSession` links active/unsafe requests.

## Risks and Edge Cases
Dumping assumes referenced inode/dentry objects remain alive through intrusive refs. Setter assertions catch accidental replacement but can abort on unexpected rebuild paths. Age uses current coarse clock minus op stamp.

## Test Signals
Request dump/admin output, single-assignment assertions, dentry lifetime across async request completion, abort reporting, and unsafe request visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/MetaRequest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/MetaRequest.h -->
# sources/distributed-fs/ceph/src/client/MetaRequest.h

## Purpose
`MetaRequest.h` declares the client’s MDS request record, including operation header, paths, pinned cache objects, cap release hints, routing/retry state, reply state, waiters, and helper predicates.

## Important APIs, Types, and Functions
Fields include private inode/dentry refs for path/path2/other targets, `ceph_mds_request_head head`, `filepath path/path2`, `alternate_name`, fscrypt metadata, payload `data`, cap drop/unless masks, release vector, regetattr mask, MDS routing fields, refcount, reply, readdir `dirp`, unsafe flags/list items, wait contexts, target inode, and caller perms. Methods include `abort()`, `aborted()`, `get_abort_code()`, setters/takers for inode refs, dentry setters, `get()`/`_put()`, caller/owner setters, path/data helpers, `is_write()`, `can_forward()`, `auth_is_best()`, and `dump()`.

## Control Flow
Client operation code constructs a request with an MDS op, attaches paths/cache refs/perms/data, assigns a tid, routes it through a session, and waits for reply/safe completion. Forward/retry fields track MDS redirection. `auth_is_best()` helps choose auth versus replica MDS based on operation and caps.

## State and Persistence Behavior
The request object is volatile but models durable metadata operation progress until MDS reply and safe journal acknowledgement. `got_unsafe`, unsafe xlist items, and waitfor_safe contexts preserve ordering and completion semantics for writes.

## Dependencies and Integration Points
It depends on MDS op/message types, `filepath`, `DentryRef`, `InodeRef`, `UserPerm`, and xlist. `Client` and `MetaSession` manage ownership, sending, aborting, replay, and completion.

## Risks and Edge Cases
Reference counting is manual and `_put()` is intentionally pseudo-private for `Client::put_request()`. Cap release masks must match cache state or stale caps can linger. Forwarding is disallowed for writes and opens. `auth_is_best()` contains subtle MDS lock/cap heuristics, especially for getattr/xattr/rstat behavior.

## Test Signals
Write/open forwarding refusal, auth-MDS selection for getattr/xattr/rstat, abort propagation, request replay after reconnect, safe waiters, cap release encoding, fscrypt alternate-name create/open requests, and refcount cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/MetaRequest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/MetaSession.cc -->
# sources/distributed-fs/ceph/src/client/MetaSession.cc

## Purpose
`MetaSession.cc` implements metadata-session diagnostics and cap-release batching for one MDS session.

## Important APIs, Types, and Functions
`MetaSession::get_state_name()` maps session enum values to readable strings. `MetaSession::dump()` emits MDS rank, addresses, sequence, cap generation/TTL, renew state, cap count/details, and state. `enqueue_cap_release()` lazily creates an `MClientCapRelease`, raises its OSD epoch barrier, and appends a cap item.

## Control Flow
Client cap release paths call `enqueue_cap_release()` while removing or dropping caps. Later client session flushing sends the accumulated message. Admin/debug paths call `dump()`.

## State and Persistence Behavior
The session state is in-memory but represents live protocol state with an MDS: caps, pending releases, dirty/flushing inodes, active/unsafe requests, and renew sequence. Cap releases are buffered until sent to the MDS.

## Dependencies and Integration Points
It depends on `MClientCapRelease`, `Inode`, `Formatter`, and MDS types. `Client` owns session maps, opening/closing/reconnect, cap renewal, release flushing, and request queues.

## Risks and Edge Cases
Destructor asserts all xlists are empty, so session teardown ordering must remove caps, dirty/flushing inodes, requests, and unsafe requests first. OSD barrier tracking must preserve the max epoch across queued releases.

## Test Signals
Session state dump, cap release batching/barrier max, teardown assertions after unmount/reconnect, and cap dump formatting with active caps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/MetaSession.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/MetaSession.h -->
# sources/distributed-fs/ceph/src/client/MetaSession.h

## Purpose
`MetaSession.h` declares the client-side protocol session with an MDS rank.

## Important APIs, Types, and Functions
`MetaSession` stores `mds_num`, connection, sequence, cap generation/TTL/renew data, addresses, MDS feature flags, state enum, reclaim state enum, MDS daemon state, readonly flag, waiting contexts, xlists for caps/dirty/flushing/requests/unsafe requests, flushing cap tids, and pending `MClientCapRelease`. Methods include `get_dirty_list()`, `get_state_name()`, `dump()`, and `enqueue_cap_release()`. `MetaSessionRef` is a shared pointer alias.

## Control Flow
Client opens sessions as MDS maps are resolved, links caps and requests to the session, renews caps, flushes dirty caps/releases, handles reconnect/reclaim, and closes sessions during unmount or failover.

## State and Persistence Behavior
Session state is volatile protocol state. It tracks what must be renewed, replayed, flushed, or released to maintain consistency with the MDS, but the durable metadata state is on the MDS journal.

## Dependencies and Integration Points
It depends on MDS map/types, cap release messages, xlist, `ConnectionRef`, `Context`, and feature bitsets. `Cap`, `Inode`, `CapSnap`, and `MetaRequest` are linked through xlists.

## Risks and Edge Cases
State enum includes `STATE_REJECTED`, but `get_state_name()` currently falls through to unknown for it. Shared-pointer ownership covers session lifetime, but xlist entries are raw item links requiring explicit cleanup. Reclaim state must match client reconnect behavior.

## Test Signals
Open/close/stale/rejected state handling, reconnect reclaim success/failure, readonly session behavior, xlist cleanup on teardown, dirty/flushing cap transitions, and release message generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/MetaSession.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/ObjecterWriteback.h -->
# sources/distributed-fs/ceph/src/client/ObjecterWriteback.h

## Purpose
`ObjecterWriteback.h` adapts `Objecter` operations to the `WritebackHandler` interface used by `ObjectCacher`.

## Important APIs, Types, and Functions
`ObjecterWriteback` implements `read()`, `may_copy_on_write()`, single-buffer `write()`, scattered `write()`, and `can_scattered_write()`. Reads call `Objecter::read_trunc()`. Writes call `Objecter::write_trunc()` or build an `ObjectOperation` with multiple writes and call `Objecter::mutate()`. Completion contexts are wrapped in `C_Lock` and `C_OnFinisher`.

## Control Flow
The object cache invokes this handler on cache miss, flush, or scattered writeback. The handler submits objecter operations and arranges for callbacks to run through the supplied finisher while holding the supplied lock.

## State and Persistence Behavior
The class itself holds only pointers to `Objecter`, `Finisher`, and lock. Persistent effects are OSD object reads/writes submitted through the objecter with snap context, truncate information, and mtime.

## Dependencies and Integration Points
It depends on `osdc/Objecter.h` and `osdc/WritebackHandler.h`. `Client` constructs it for its `ObjectCacher`/writeback path.

## Risks and Edge Cases
`may_copy_on_write()` always returns false, so cache behavior must not rely on handler-side COW. Callback lock ordering must match client/object cache expectations. Scattered writes assume OSD/objecter support and return true from `can_scattered_write()`.

## Test Signals
Object cache read/writeback paths, callback lock/finisher ordering, scattered write correctness, truncate sequence/size propagation, snap context propagation, and OSD error delivery to client writeback completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/ObjecterWriteback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/RWRef.h -->
# sources/distributed-fs/ceph/src/client/RWRef.h

## Purpose
`RWRef.h` defines a lightweight state-gated reader/writer reference mechanism used by the client lifecycle. Readers increment a refcount only when a required state predicate is satisfied; writers transition state and can wait for active readers to drain.

## Important APIs, Types, and Functions
`RWRefState<T>` stores current state, lock, condition variable, reader count, and virtual predicates `check_reader_state()`, `check_writer_state()`, and `is_valid_state()`. `RWRef<T>` is an RAII object with `is_state_satisfied()`, `update_state()`, `is_first_writer()`, and `wait_readers_done()`.

## Control Flow
Reader operations construct `RWRef(state, required, true)`. If allowed, `reader_cnt` increments and destructor decrements/notifies. Writer operations construct `RWRef(state, next_state, false)`, transition state if permitted, then call `wait_readers_done()` before completing lifecycle-sensitive work. Client mount/init state structs specialize the predicates in `Client.h`.

## State and Persistence Behavior
All state is in-memory synchronization state. It avoids holding a reader lock during IO while still blocking lifecycle writers until in-flight readers leave.

## Dependencies and Integration Points
It depends on Ceph mutex/condition variable wrappers and assertions. `Client` uses it for initialize and mount state transitions.

## Risks and Edge Cases
Writer construction sets `satisfied=true` even if it is not the first writer; callers must inspect `is_first_writer()` when that distinction matters. There is no reader wait path; failed readers must return or retry at a higher layer. Predicate correctness is entirely delegated to subclasses. Destructors lock state, so misuse during object teardown can deadlock if state outlives assumptions fail.

## Test Signals
Concurrent readers during unmount, failed readers in wrong state, first-writer versus subsequent-writer behavior, writer wait for reader drain, state update validity assertions, and no deadlock with unrelated locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/client/RWRef.h -->
