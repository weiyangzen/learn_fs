# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_sendrecv.c

This is the main userland implementation behind `zfs send` and `zfs receive` in libzfs. It bridges CLI-level send/receive flags, dataset traversal, stream metadata construction, resume-token handling, redaction-bookmark handling, property preservation, encryption-root fixups, and kernel `libzfs_core` send/receive ioctls.

Primary responsibilities:
- Build compound send stream headers containing filesystem, snapshot, property, hold, clone-origin, and encryption-root metadata.
- Generate full, incremental, recursive, replication, raw, redacted, saved, and resumable send streams.
- Estimate send sizes and report progress through a background progress thread using `lzc_send_progress()`.
- Decode and validate send resume tokens.
- Receive single or compound streams, including recursive replication streams.
- Reconcile local dataset topology with incoming stream topology using GUID matching, renames, destroys, promotions, and second-pass retries.
- Apply received properties, command-line `-o` overrides, `-x` exclusions, snapshot properties, and snapshot holds.
- Handle encryption constraints for raw sends, key material, encryption roots, clone origins, and keylocation restoration.
- Translate stream/kernel errors into libzfs errors with actionable auxiliary messages.

Important data structures:
- `progress_arg_t` carries the dataset handle, send fd, output formatting flags, progress mode, and expected size into the send progress thread.
- `fsavl_node_t` indexes snapshots by GUID in an AVL tree so stream/local metadata can be matched independently of names.
- `send_data_t` is used while walking source datasets to build the large send-header nvlist. It tracks recursive traversal state, from/to snapshot txgs, parent snapshot GUIDs, property/hold collection, flags, and optional snapshot filters.
- `send_dump_data_t` controls actual stream dumping after metadata collection. It tracks from/to snapshots, previous snapshot object ids, replication/doall state, feature flags, hold tags, debug nvlists, progress settings, output fd, and accumulated size.
- `guid_to_name_data_t` supports GUID lookup over datasets and bookmarks, including redaction bookmark matching.
- Small wrapper structs such as `zfs_send`, `zfs_send_one`, and `zfs_send_resume_impl` adapt internal callbacks for `lzc_send_wrapper()`.

Send-side flow:
- `gather_nvlist()` opens the source dataset and drives `send_iterate_fs()`.
- `send_iterate_fs()` recursively builds per-filesystem metadata keyed by filesystem GUID. It records names, clone origins, parent-from-snapshot GUIDs, dataset properties, encryption-root markers, snapshots, snapshot properties, and optional holds.
- `send_iterate_snap()` records snapshot GUIDs and collects snapshot properties/holds while enforcing from/to snapshot windows.
- `send_iterate_prop()` filters out read-only, inherited, unsupported, unknown, snapshot space-limit, and inappropriate properties before adding sendable property values.
- `fsavl_create()`, `fsavl_find()`, and `fsavl_destroy()` provide fast GUID lookup over collected stream metadata.
- `send_prelim_records()` writes a compound `DRR_BEGIN` header carrying packed nvlist metadata when replication/properties/holds require it, then writes a checksum-protected `DRR_END` for that header.
- `dump_snapshot()` sends one snapshot, deciding whether it is included, whether it is incremental from the previous accepted snapshot, whether clone-origin snapshots must be preserved, and which `LZC_SEND_FLAG_*` flags apply.
- `dump_filesystem()` validates source snapshots and iterates either the full snapshot range or just from/to snapshots.
- `dump_filesystems()` orders recursive replication sends so parent datasets and clone origins are sent before dependent children.
- `zfs_send_cb_impl()` is the main recursive send coordinator. It validates inputs, emits preliminary metadata, optionally performs a dry-run pass for size/holds, installs temporary holds for destructive safety, sends the stream payloads, and writes the final compound end record.
- Public `zfs_send()` wraps `zfs_send_cb_impl()` with `lzc_send_wrapper()`.

Single-stream and redacted send:
- `zfs_send_one_cb_impl()` handles one dataset/snapshot stream, including optional properties/holds/backup headers.
- `snapshot_is_before()` validates that an incremental source is actually earlier in the target timeline, following clone origins recursively.
- Redacted send validation ensures the requested redaction bookmark exists on the target snapshot’s dataset and has redaction-snapshot metadata.
- `zfs_send_one()` is the public wrapper.

Resume/saved send:
- `zfs_send_resume_token_to_nvlist()` decodes tokens of the form version/checksum/uncompressed-length/hex-compressed-payload, verifies Fletcher checksum, inflates with zlib, and unpacks the nvlist.
- `lzc_flags_from_sendflags()` and `lzc_flags_from_resume_nvl()` merge user-requested and token-preserved send features.
- Redaction helpers `get_bookmarks()`, `find_redact_pair()`, `find_redact_book()`, and GUID-array comparison functions find a complete redaction bookmark matching the resumed stream.
- `zfs_send_resume_impl_cb_impl()` validates token fields, resolves original to/from GUIDs to names, estimates size if needed, starts progress reporting, and calls `lzc_send_resume_redacted()`.
- `zfs_send_resume()` decodes the token and dispatches the resumed send.
- `zfs_send_saved()` uses a dataset’s `receive_resume_token`, optionally combines it with a supplied resume token position, and sends saved partially received state.

Progress and reporting:
- `zfs_send_progress()` calls `lzc_send_progress()`.
- `send_progress_thread()` uses signals/timers to poll bytes and block counts while a send or size estimate is active.
- `send_progress_thread_exit()` cancels and joins the progress thread and restores the parent signal mask.
- `send_print_verbose()` formats human-readable or parsable size/progress output.
- Progress can also update process title when `progressastitle` is enabled.

Receive-side flow:
- `zfs_receive()` is the public entry point. It validates the fd, extracts optional clone origin from props, calls `zfs_receive_impl()`, then mounts/shares newly received filesystem trees through a changelist if appropriate.
- `zfs_receive_impl()` reads and validates the first `DRR_BEGIN`, detects byteswapped streams, rejects unsupported/deprecated stream features, propagates the holds feature, and dispatches to either `zfs_receive_one()` or `zfs_receive_package()`.
- `zfs_receive_package()` reads the compound header nvlist, verifies the header checksum, builds stream AVL metadata, runs pre-receive topology reconciliation for recursive incrementals, receives each contained substream, then reruns reconciliation and encryption hierarchy repair.
- `zfs_receive_one()` is the central single-stream receive routine. It computes the destination snapshot name according to exact, prefix `-d`, or tail `-e` receive semantics; resolves clone origins; validates stream feature compatibility; checks destination existence and overwrite rules; handles resume/newfs cases; prepares command-line property overrides/exclusions; calls `lzc_receive_with_cmdprops()` or `lzc_receive_with_heal()`; applies snapshot properties and holds; maps ioctl errors; and sets mount intent.
- `recv_skip()` consumes a stream after a recoverable duplicate/error case, parsing record payload sizes for object/write/spill/embedded records.
- `recv_read()` and `recv_read_nvlist()` are stream readers with optional checksum update and nvlist size protection.

Receive topology reconciliation:
- `recv_incremental_replication()` compares local dataset/snapshot GUID metadata with stream metadata. With `-F`, it deletes local snapshots/filesystems missing from the stream, renames snapshots/datasets whose GUIDs match but names differ, and promotes clones when stream/local origins differ.
- It uses multi-pass retry logic because renames, deferred destroys, and parent GUID changes can temporarily block later operations.
- `recv_rename()`, `recv_destroy()`, and `recv_promote()` wrap dataset mutations with changelist unmount/remount handling and encryption-root workarounds.
- `guid_to_name_redact_snaps()` and `guid_to_name()` resolve GUIDs to local names by searching progressively broader dataset hierarchy portions. This avoids choosing a less-local duplicate GUID when replicated trees are received piecemeal.
- `created_before()` compares snapshot creation txgs by GUID to decide promotion direction.

Encryption behavior:
- Send-side metadata marks encrypted datasets and encryption roots. Non-raw encrypted sends with properties are rejected unless `no_preserve_encryption` is explicitly set.
- Receive-side raw streams preserve encryption. Non-raw property streams infer `encryption=off` for new filesystems when appropriate.
- `zfs_setup_cmdline_props()` forbids overriding encryption properties for raw streams, restricts encryption settings for incremental streams, validates overrides via `zfs_valid_proplist()`, and uses `zfs_crypto_create()` to prepare wrapping key data.
- `recv_fix_encryption_hierarchy()` runs after recursive raw receive to force datasets into or out of encryption-root status to match the stream and restore keylocation values that were temporarily removed before the receive ioctl.
- Rename/promote helpers force grand origins to become encryption roots when EACCES indicates an encryption-root boundary conflict.

Property and hold handling:
- Dataset properties are sent in the compound header when `-p`, replication, backup mode, or recursive metadata collection requires them.
- Snapshot properties are stored under per-snapshot `snapprops`.
- Holds are collected under `snapholds` and reapplied after receive unless skipped.
- Command-line receive properties use boolean nvpairs for exclusions and strings for overrides. Exclusions may delete received non-inheritable properties or force explicit inheritance.
- Property errors returned from the receive ioctl are reported individually, with truncation summaries via `trunc_prop_errs()`.

Error handling notes:
- Send errors distinguish cross-target incrementals, missing incremental sources, unloaded encryption keys, stream feature mismatch, large microzap requirements, busy targets, and generic kernel errors.
- Receive errors distinguish bad magic, malformed nvlist, unsupported feature flags, deprecated dedup streams, wrong incremental parent, modified destination, destination exists, crypto/key failures, checksum/truncation, incompatible large-block/raw stream state, quota exhaustion, resume conflicts, and oversized kernel allocation.
- `recv_ecksum_set_aux()` enhances resumable checksum/truncation failures with the command needed to resume from the receive token.

External dependencies:
- Kernel/userland interfaces: `zfs_ioctl()`, `lzc_send_*`, `lzc_receive_*`, `lzc_hold()`, `lzc_destroy*()`, `lzc_rename()`, `lzc_change_key()`.
- Metadata libraries: nvlist/fnvlist, AVL trees, ZFS props/features, DMU replay records.
- Checksums/compression: Fletcher-4, zlib.
- Dataset/property helpers from other libzfs files: `zfs_open()`, `zfs_close()`, `zfs_iter_*`, `changelist_*`, `zfs_valid_proplist()`, `zfs_crypto_create()`, error helpers from `libzfs_util.c`.

Research relevance:
- This file is one of the densest userland sources for understanding OpenZFS copy-on-write replication semantics. It shows how snapshot GUIDs, clone origins, redaction bookmarks, raw encryption, resumable receive state, and recursive dataset trees are represented and reconciled across machines.
