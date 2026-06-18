# subset-b-009167 research

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/flist.c -->
# sources/sync-backup/rsync/flist.c

## Purpose

`flist.c` builds, serializes, receives, sorts, searches, and frees rsync file lists. It is the bridge between source filesystem discovery and the transfer/generator pipeline. On the sender it walks argv or `--files-from` input, applies path cleanup and filters, creates compact `struct file_struct` entries, transmits them using rsync protocol flags, and emits additional incremental recursion file lists. On the receiver/generator side it decodes those wire entries, validates untrusted names, maps ids, reconstructs file metadata, sorts/deduplicates the list, and provides lookup helpers used by deletion, fuzzy matching, and hard-link handling.

## Important APIs, Types, And Functions

Key exported state includes `cur_flist`, `first_flist`, `dir_flist`, `send_dir_ndx`, `send_dir_depth`, `flist_cnt`, `file_total`, `file_old_total`, `flist_eof`, `io_error`, `filesystem_dev`, `flist_csum_len`, and `xfer_flags_as_varint`. These globals are consumed by the generator, receiver, hard-link code, id mapping, progress reporting, and incremental recursion scheduler.

Important entry points are `init_flist()`, `send_file_list()`, `recv_file_list()`, `send_extra_file_list()`, `recv_additional_file_list()`, `make_file()`, `unmake_file()`, `get_dirlist()`, `flist_find()`, `flist_find_name()`, `flist_find_ignore_dirness()`, `flist_free()`, `clear_file()`, `f_name_cmp()`, `f_name_has_prefix()`, `f_name_buf()`, `f_name()`, `link_stat()`, `change_pathname()`, and `get_device_size()`.

The central internal functions are `send_file_entry()` and `recv_file_entry()`, which implement the on-wire metadata format; `send_file_name()` and `send_directory()`, which discover files and append them to lists; `send_implied_dirs()` and `send1extra()`, which support `--relative` and incremental recursion; `flist_sort_and_clean()`, which sorts, strips roots, removes duplicates, and prunes empty dirs; and `flist_new()`, `flist_expand()`, and `flist_done_allocating()`, which manage list and pool allocation.

## Control Flow

`init_flist()` computes the file-list checksum length from the negotiated file checksum algorithm and enables file-list progress output when appropriate. The sender enters `send_file_list()`, initializes list objects and optional hard-link state, starts output buffering, then repeatedly reads source names from argv or `--files-from`. Each name is sanitized, split into directory and basename when needed, normalized for `--relative`, checked for unsafe `..`, daemon exclusions, server filters, directory transfer policy, and missing-arg behavior. Existing source args become `file_struct` entries via `send_file_name()`, and directories trigger `send_directory()` or incremental-recursion diversion.

`make_file()` is the local filesystem-to-`file_struct` constructor. It runs `readlink_stat()` or uses a supplied stat result, applies filters and `-x` mount rules, handles `--copy-devices`, records uid/gid, mtimes, optional atime/crtime, symlink text, device ids, hard-link dev/inode cache values, long file lengths, and optional checksums. The entry is allocated either from the current file-list pool or as a temporary standalone object.

`send_file_entry()` serializes a `file_struct`. It maintains static last-value caches for name, mode, uid, gid, mtime, atime, device major, and hard-link group data, then sets `XMIT_*` flags to avoid repeating unchanged fields. It writes compressed name-prefix data, length, times, mode, ids and optional id names, rdev, symlink target, old-protocol hard-link dev/inode values, and optional file checksums. `recv_file_entry()` reverses that format, including protocol-version branches, name iconv, path safety checks, sender-filter trust validation, hard-link reference expansion, device/special handling, ACL/xattr reception, and pool allocation.

After discovery, `send_file_list()` sends the end marker and sorts the list. In non-incremental mode it sends id lists and sets `flist_eof`. In incremental recursion it builds `dir_flist` tree links with `add_dirs_to_tree()` and can call `send_extra_file_list()` to send child directory batches. `send_extra_file_list()` walks the directory tree, sends `NDX_FLIST_OFFSET - dir_ndx` headers, emits a child file list with `send1extra()`, updates file totals and stats, then advances to child or sibling dirs until it writes `NDX_FLIST_EOF`.

The receiver calls `recv_file_list()` for the initial list and later incremental lists. It validates directory indices against `dir_flist`, reads xflags until an end marker, decodes each entry, enforces incremental path locality, updates file type counters, builds sorted pointers, receives id lists for old/non-incremental protocols, sorts and cleans, and merges received io-error flags. `recv_additional_file_list()` handles the special one-item initial list case by reading either EOF or an additional directory list.

Search and sort behavior is specialized for rsync semantics. `f_name_cmp()` compares virtual full paths without materializing strings and treats directories with path-like trailing slash ordering for protocol 29 and later. `flist_sort_and_clean()` uses stable merge sort by default, removes duplicate names on the receiver by clearing inactive entries, marks duplicate directories on the sender, strips leading roots for relative paths after sorting, and implements empty-directory pruning by temporarily overloading depth values.

## State And Persistence

The file-list lifecycle is in-memory and protocol-stream-backed. Non-temp file lists share an allocation pool and form a circular-prev/linear-next list. `file_total`, `file_old_total`, and `flist_cnt` track active work and incremental cleanup. Temp lists are used for directory scans such as deletion and fuzzy matching. `io_error` persists file-list construction errors across send/receive and is deliberately sent to the peer to protect delete modes. Static caches in `send_file_entry()` and `recv_file_entry()` are protocol state; they rely on sequential entry processing. `pathname`, `orig_dir`, and `pathname_len` cache sender cwd transitions.

## Dependencies And Integration Points

This file depends heavily on `rsync.h` macros and extra-field layout, `ifuncs.h` helpers, `inums.h` number formatting, `io.h` wire I/O, the memory-pool allocator, filter APIs, id-list APIs, ACL/xattr APIs, iconv conversion, hard-link helpers from `hlink.c`, filesystem wrappers such as `do_stat_at()` and `x_lstat()`, and generator-side consumers such as `delete_in_dir()` and `recv_generator()`. The generator relies on sorted `cur_flist`, `dir_flist`, `F_DEPTH`, `FLAG_CONTENT_DIR`, `FLAG_TOP_DIR`, hard-link group fields, and `flist_find*()` lookups.

## Risks

The highest-risk areas are protocol compatibility branches, name/path validation, static compression state, and extra-field sizing. A mismatch in `XMIT_*` flags or protocol version handling corrupts the wire stream. Unsafe path handling can become a traversal vulnerability, so checks around `clean_fname()`, absolute names, daemon filters, implied filters, and `sanitize_path()` are security-critical. `MAXPATHLEN` calculations protect stack buffers but need regression coverage. Duplicate handling and empty-dir pruning temporarily reuse fields, making ordering and active-entry assumptions fragile. Incremental recursion uses multiple shared globals and parent/child indices; off-by-one errors can strand lists or free pools too early. Long sizes, nanosecond mtimes, device ids, and hard-link group fields all depend on conditional extra allocation.

## Test Signals

Useful tests include recursive and non-recursive file-list builds; `--relative`, `/./`, trailing slash, `.` and `..` rejection cases; daemon and server filter rejection; `--files-from` with null and newline separators; iconv filename and symlink conversion; protocol compatibility for 28, 29, 30, and 31 features; `--delete-missing-args`; `--one-file-system`; duplicate file and directory names; `--prune-empty-dirs`; large files over 4 GiB; nanosecond mtimes; ACL/xattr preservation; device/special preservation; symlink munging and unsafe symlink copy behavior; incremental recursion with additional file lists; and hard-link transfers across initial and later file lists.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/flist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/generator.c -->
# sources/sync-backup/rsync/generator.c

## Purpose

`generator.c` contains logic exclusive to rsync's generator process. It walks the received file lists, decides what must be created, deleted, copied locally, hard-linked, or transferred, emits itemized change records, sends checksum blocks to the sender for delta transfers, coordinates hard-link completion, schedules delete phases, and performs final directory timestamp and permission repair.

## Important APIs, Types, And Functions

The main exported functions are `generate_files()`, `check_for_finished_files()`, `atomic_create()`, `quick_check_ok()`, `unchanged_attrs()`, and `itemize()`. `maybe_ATTRS_REPORT` and `maybe_ATTRS_ACCURATE_TIME` are exported reporting flags used by hard-link and attribute paths.

Important internal routines include delete-delay helpers `start_delete_delay_temp()`, `flush_delete_delay()`, `remember_delete()`, `read_delay_line()`, `do_delayed_deletions()`, per-directory deletion `delete_in_dir()` and `do_delete_pass()`, metadata comparators `mtime_differs()`, `any_time_differs()`, `perms_differ()`, `ownership_differs()`, `acls_differ()`, and `xattrs_differ()`, block-signature generation `sum_sizes_sqroot()` and `generate_and_send_sums()`, alternate-basis selection `find_fuzzy()`, `try_dests_reg()`, `try_dests_non()`, local copy helper `copy_altdest_file()`, the main per-entry state machine `recv_generator()`, hard-link skip handling `handle_skipped_hlink()`, and directory finalization `touch_up_dirs()`.

## Control Flow

`generate_files()` sets itemizing/log behavior from protocol role and daemon/server status, computes flags for directory retouching, delete behavior, and delta mode, optionally runs a delete-before pass, then loops over `cur_flist` entries in sorted order. In incremental recursion, it first processes a parent directory pseudo-entry and can wait for more receiver file lists when hard-link lookahead is needed. Each active entry is converted to a path and passed to `recv_generator()`. After each entry it drains hard-link and redo completions via `check_for_finished_files()`, sends keepalives or socket flushes, advances through incremental file lists, and finally coordinates phases with `NDX_DONE` markers and `MSG_DONE` counts.

`recv_generator()` is the core decision engine. It starts with static cursors for parent directory tracking, dry-run missing subtrees, skipped subtrees, and fuzzy basis lists. It handles list-only output, daemon receive filters, dry-run parent absence, validation that parent dirs appear in non-incremental file lists, and `--delete-missing-args`. It implements `--ignore-non-existing`, `--ignore-existing`, destination type checks, permission-mode adjustment when not preserving perms, directory creation and later retouching, delete-during scans, symlink/device/special creation, regular-file size bounds, update-only logic, alternate-destination handling, partial-dir basis selection, fuzzy basis selection, backup creation, delta checksum emission, and success notifications for `--remove-source-files`.

For regular files, the generator first checks destination type and alternate basis directories. `quick_check_ok()` compares size and mtime, or checksum when `always_checksum` is enabled. `try_dests_reg()` searches `basis_dir[]` for increasingly strong matches: any regular file, quick-check match, and unchanged attributes. Depending on `--compare-dest`, `--copy-dest`, or `--link-dest`, it may report up-to-date, hard-link, local-copy, or return a basis file index. If delta transfer is needed, `generate_and_send_sums()` maps the basis file and writes weak and strong rolling checksum signatures.

Non-regular paths are handled inline. Directories are created or retouched and may trigger `delete_in_dir()`. Symlinks are checked for safety and created through `atomic_create()`. Devices and special files are created with `mknod` through `atomic_create()` when allowed. Unsupported non-regular files are skipped with informational output.

Deletion behavior is split by option. `delete_in_dir()` builds a local directory list with `get_dirlist()`, then deletes items absent from `cur_flist`, respecting mount points, `--one-file-system`, uid-write restrictions, daemon/local filters, and delayed deletion. `do_delete_pass()` runs that per directory for delete-before or delete-after. `--delete-delay` uses an in-memory buffer plus an unlinked temp file overflow; records are null-delimited mode/name entries optionally prefixed with `!` for uid-write restrictions.

`check_for_finished_files()` drains sender/receiver feedback. It handles hard-link completion indices, redo indices, old incremental file-list cleanup, directory touch-up for completed parent dirs, and `NDX_DONE` emission. `touch_up_dirs()` restores writable permissions and mtimes after contents are transferred.

## State And Persistence

Most state is in memory, but delete-delay may spill to an unlinked temporary file descriptor. Static variables inside `recv_generator()` persist across file entries and cache parent directory state, skipped subtree state, and fuzzy basis lists. Global `phase` tracks generator protocol phases. `deldelay_buf`, `deldelay_fd`, and counters hold delayed deletion data. `need_retouch_dir_times` and `need_retouch_dir_perms` persist whether a final directory pass is needed. File-list entries are mutated with flags such as `FLAG_MISSING_DIR`, `FLAG_DIR_CREATED`, `FLAG_FILE_SENT`, `FLAG_HLINK_DONE`, and hard-link predecessor fields.

## Dependencies And Integration Points

The generator consumes `cur_flist`, `first_flist`, `dir_flist`, `flist_eof`, and lookup helpers from `flist.c`; hard-link APIs from `hlink.c`; checksum and map-file APIs; transfer finalization and cleanup APIs; delete, backup, partial-dir, ACL, xattr, and filter modules; sender/receiver message APIs such as `write_ndx()`, `wait_for_receiver()`, `get_redo_num()`, and `get_hlink_num()`; and filesystem wrappers from rsync's portability layer. It emits checksum headers and itemize records to `sock_f_out`/`f_out`, which drive sender-side file data generation.

## Risks

`recv_generator()` is a dense state machine with many option interactions. Regressions can silently skip transfers, delete wrong files, or produce incorrect itemized output. Delete modes rely on `io_error` protection and must not run after unsafe file-list omissions. Alternate-destination paths can conflate real destination stat data with basis stat data if `stat_x` ownership is mishandled. Hard-link handling mutates linked-list fields and file-list progress counters, so skipped links and redo paths are fragile. In-place backups and copy-dest paths must preserve cleanup semantics to avoid leaving temp files or losing attributes. Delete-delay parsing is custom and must reject corrupt records. Directory retouching can fight permission constraints, fake-super behavior, and dry-run/list-only modes.

## Test Signals

Tests should cover quick-check by size, mtime, checksum, and nanoseconds; directory creation and final retouch; delete-before, delete-during, delete-delay, and delete-after; `--max-delete`; `--ignore-existing`, `--ignore-non-existing`, `--update`, min/max size; `--partial-dir`, fuzzy basis, compare/copy/link dest; symlink safety, device and special creation, write-devices; hard-link groups with skipped entries, delayed leaders, and incremental recursion; in-place backups; redo pass behavior; remove-source-files success messages; list-only output; ACL/xattr differences; one-file-system deletion; and protocol phase ordering with early delay/delete done messages.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/generator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/getfsdev.c -->
# sources/sync-backup/rsync/getfsdev.c

## Purpose

`getfsdev.c` is a tiny diagnostic/helper program that prints the filesystem device major/minor pair for each pathname argument. It is built against rsync portability definitions so it can use the same `STRUCT_STAT` and optional `stat64()` choice as the main program.

## Important APIs, Types, And Functions

The only function is `main(int argc, char *argv[])`. It declares `STRUCT_STAT st`, chooses `stat64()` when `USE_STAT64_FUNCS` is configured and `stat()` otherwise, then prints `major(st.st_dev)` and `minor(st.st_dev)` as `major/minor`.

## Control Flow

The program iterates over command-line paths with `while (--argc > 0)`, stats each path, exits with status 1 on the first stat failure, prints one line per successful path, and exits 0 after all paths are processed.

## State, Dependencies, And Integration

There is no persistent state. It depends on `rsync.h` for `STRUCT_STAT`, feature macros, standard headers, and device-number macros. It is likely used by build tests or developer diagnostics around device-number portability and `--one-file-system` behavior.

## Risks

The program casts major/minor values to `long`, which is appropriate for diagnostics but not a stable machine-readable ABI on exotic platforms. It stops at the first failed path and prints a generic error without `strerror(errno)`.

## Test Signals

Run it against regular files, directories, mount points, missing paths, and platforms that enable `USE_STAT64_FUNCS`. Expected output is one `major/minor` line per existing input and nonzero exit on failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/getfsdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/getgroups.c -->
# sources/sync-backup/rsync/getgroups.c

## Purpose

`getgroups.c` is a portable helper that prints the current user's supplementary group ids, similar to `id -G`, while ensuring the user's primary gid appears in the output even on systems where `getgroups()` omits it.

## Important APIs, Types, And Functions

The only function is `main()`. It uses `MY_GID()` from rsync portability code, optionally calls `getgroups(0, NULL)` when `HAVE_GETGROUPS` is available, allocates a `gid_t` array of `n + 1`, fills it with `getgroups(n, list)`, prints each gid as an unsigned long with trailing spaces, tracks whether the primary gid was present, then prints the primary gid if missing.

## Control Flow

The program obtains the supplementary group count, allocates storage, fetches the group list, emits all returned gids, conditionally emits the primary gid, prints a newline, and exits 0. If `getgroups(0, NULL)` fails it reports through `perror()` and returns 1. If allocation fails it writes `out of memory!` and exits 1.

## State, Dependencies, And Integration

There is no persistent state. It depends on `rsync.h` for `gid_t`, `MY_GID()`, `UNUSED`, feature detection, and standard functions. It is a build/test utility for group-id portability and may be used by tests that need predictable group membership output.

## Risks

If the second `getgroups()` call fails, the code does not recheck `n` before iterating. Group membership can change between the count and fill calls. Output formatting has spaces between supplementary ids and may omit a separating space before the primary gid when no supplementary groups were printed, which is fine for whitespace-token parsing.

## Test Signals

Test with users whose primary gid is included and omitted from `getgroups()`, with zero supplementary groups, and on platforms without `HAVE_GETGROUPS`. Failure-path tests should simulate `getgroups()` and `malloc()` errors if possible.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/getgroups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/hashtable.c -->
# sources/sync-backup/rsync/hashtable.c

## Purpose

`hashtable.c` provides rsync's compact open-addressed hash table for integer keys plus Bob Jenkins lookup3 hash functions for byte strings. The table is used by hard-link matching, one-file-system deletion bookkeeping, and other places that need fast integer-key lookup without per-node allocation.

## Important APIs, Types, And Functions

Exported functions are `hashtable_create(int size, int key64)`, `hashtable_destroy(struct hashtable *tbl)`, `hashtable_find(struct hashtable *tbl, int64 key, void *data_when_new)`, `hashlittle(const void *key, size_t length)`, and, when 64-bit integers are available, `hashlittle2(const void *key, size_t length)`.

The table stores either `struct ht_int32_node` or `struct ht_int64_node` elements selected by `key64`. Macros from `rsync.h` such as `HT_NODE()` and `HT_KEY()` abstract node access. `HASH_LOAD_LIMIT(size)` grows at 75 percent occupancy. Key value zero is reserved as the empty-slot sentinel, so callers must bias real zero keys before insertion.

## Control Flow

`hashtable_create()` rounds the requested size up to at least 16 and to a power of two, allocates a zeroed node array sized for 32-bit or 64-bit keys, initializes counters, and optionally emits hash debug output. `hashtable_destroy()` frees the node array and table.

`hashtable_find()` rejects zero keys, grows the table when inserting past the load limit, reinserts all non-empty old nodes, then hashes the requested key. For 32-bit keys it uses a Jenkins one-at-a-time style byte hash over the little-endian encoded key. For 64-bit keys it uses a compact Jenkins hashword finalization. Lookup uses linear probing with a power-of-two mask. If the key exists, the node is returned. If an empty slot is found and `data_when_new` is null, it returns null. Otherwise it writes the key, sets `node->data` to `data_when_new`, increments entries, and returns the new node.

`hashlittle()` and `hashlittle2()` are adapted lookup3 routines. They choose fast aligned 32-bit, aligned 16-bit, or byte-at-a-time paths based on pointer alignment and endian configuration, mix 12-byte blocks, handle tail bytes through switch fallthrough, finalize, and force nonzero results using `NON_ZERO_32` or `NON_ZERO_64`.

## State And Persistence

State is entirely heap allocated per table. Node data is caller-owned and is not freed by `hashtable_destroy()`. During growth, nodes are reinserted and data pointer values are preserved, including null data through a temporary sentinel path. Debug logging includes table address, size, and key width.

## Dependencies And Integration Points

The file depends on `rsync.h` allocation wrappers, integer typedefs, endian and size macros, hash-table structs/macros, debug/logging helpers, and cleanup on internal errors. `hlink.c` uses nested 64-bit tables for dev/inode groups and a 32-bit table for prior incremental hard-link groups. `generator.c` uses a 64-bit table to track device ids already accepted during one-file-system deletion.

## Risks

Zero is not a valid key. Callers that forget to offset zero-valued device ids or group ids will hit a fatal internal error. Open addressing performance depends on keeping load under the growth threshold and on good hash distribution. The table never deletes individual keys. Data pointer ownership is external, so destroying a table with allocated node data leaks unless the caller frees nested data first, as `idev_destroy()` does. `hashlittle()` is not cryptographic and should not be used for adversarial integrity checks.

## Test Signals

Tests should insert and find 32-bit and 64-bit keys, verify growth preserves keys and null data, reject zero keys, exercise collision probing, destroy nested caller-owned tables, and compare `hashlittle()`/`hashlittle2()` behavior across aligned and unaligned buffers, short tails from 0 to 12 bytes, and big/little endian builds.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/hashtable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/help-from-md.awk -->
# sources/sync-backup/rsync/help-from-md.awk

## Purpose

`help-from-md.awk` generates a C help header from a fenced Markdown section. The caller passes `-v hfile=help-NAME.h NAME.NUM.md`; the script finds a Markdown comment that references the output header and converts the following code fence into `rprintf(F, "...\\n");` lines.

## Important APIs, Types, And Functions

The script uses AWK `BEGIN`, pattern actions, and `END`. Key variables are `hfile`, `ARGV[1]`, `heading`, `findcomment`, `backtick_cnt`, `prints`, and `foundcomment`. It uses `sub()` to escape a literal dot in `hfile`, `gsub()` to escape double quotes in help text, and writes generated output with redirection to `hfile`.

## Control Flow

At startup the script constructs a generated-file heading and a regex matching `[comment]` followed by the requested header name. Every line beginning with triple backticks increments `backtick_cnt` and is not copied. Once the comment is found, lines inside the first fenced block are escaped and appended to `prints`. Encountering a second fence exits the scan. In `END`, if the section was found and closed, the script writes the heading plus accumulated `rprintf()` statements. Otherwise it prints a failure message and exits 1.

## State, Dependencies, And Integration

The script persists only the generated header file. It is part of the build-time documentation/help pipeline and expects Markdown source conventions to remain stable: a comment marker naming the header followed by a fenced block containing literal help text.

## Risks

The regex only escapes the first dot in `hfile`, so unusual header names with multiple regex metacharacters could match more broadly than intended. Only double quotes are escaped; backslashes in help text are not doubled, so C escape sequences in Markdown can be interpreted by the generated C compiler. It assumes the wanted help text is in the first code fence after the marker and treats more than one opening fence as completion.

## Test Signals

Tests should generate a known help header from Markdown, verify quotes are escaped, verify missing comment and unterminated fence fail, check multiple help sections, and compile a generated header containing backslashes, percent signs, and empty lines.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/help-from-md.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/hlink.c -->
# sources/sync-backup/rsync/hlink.c

## Purpose

`hlink.c` implements hard-link preservation. On the sender it maps device/inode pairs into hard-link group numbers or first-link indices. On the receiver/generator it orders group members, links later members to completed leaders, handles skipped links, and remembers prior incremental-recursion hard-link paths across file lists.

## Important APIs, Types, And Functions

Under `SUPPORT_HARD_LINKS`, exported functions are `init_hard_links()`, `idev_find()`, `idev_destroy()`, `match_hard_links()`, `hard_link_check()`, `hard_link_one()`, `finish_hard_link()`, and `skip_hard_link()`.

Static state includes `data_when_new`, `dev_tbl`, `prior_hlinks`, and `hlink_flist`. `dev_tbl` is a nested 64-bit hash: device key to inode hash table. `prior_hlinks` is a 32-bit hash used by the receiver in incremental recursion to remember prior hard-link group paths or previous indices.

## Control Flow

`init_hard_links()` creates sender/old-protocol device tables or receiver incremental prior-link tables depending on role and protocol. `idev_find()` offsets device ids by one so real device zero can be represented, creates an inode table per device, and returns the inode node, using `-1` as the new-node data sentinel. `idev_destroy()` frees all nested inode tables before freeing `dev_tbl`.

`match_hard_links()` runs after a file list is sorted. It gathers sorted indices of hard-linked files and calls `match_gnums()`. `match_gnums()` sorts those indices by group number, marks first and last members, fills `F_HL_PREV()` as a reverse linked list using wire indices, and in incremental recursion updates or consults `prior_hlinks` so groups spanning file lists remain connected.

`hard_link_check()` is called by the generator for hard-linked entries that are not first. It uses `check_prior()` to find a prior unskipped group member or cached prior path. If the prior member is still being transferred, it rewires predecessor fields, marks the current file as waiting, increments `cur_flist->in_progress`, and returns skip. If a prior completed leader exists, it stats the leader, optionally considers alternate basis directories, then calls `maybe_hard_link()` to create or verify the hard link.

`finish_hard_link()` is called when a leader transfer or local match is complete. It marks the leader done, stores `alt_dest` in `F_HL_PREV()` for first/done entries, walks the waiting reverse chain, calls `maybe_hard_link()` for each follower, decrements `in_progress`, sends remove-source success messages when needed, and in incremental recursion replaces the prior hash data with a cached pathname. `skip_hard_link()` marks skipped entries and promotes a previous waiting member to last when necessary.

## State And Persistence

Hard-link state is stored in file-list extra fields and in process-local hash tables. For protocol 30 and later, the sender transmits a first hard-link index instead of raw dev/inode for every member. For older protocols the receiver groups dev/inode itself. Incremental recursion persists group continuity in `prior_hlinks` while the process runs; it is not written to disk.

## Dependencies And Integration Points

This file depends on `hashtable.c`, `flist.c` lookup/index functions, `generator.c` APIs (`itemize()`, `quick_check_ok()`, `unchanged_attrs()`, `atomic_create()`), filesystem wrappers (`link_stat()`, `do_link_at()`), alternate basis directories, ACL/xattr accessors, and message/logging helpers. It is tightly coupled to `file_struct` hard-link macros from rsync headers.

## Risks

The code relies on overloading `F_HL_PREV()` for previous indices, first/done alternate-destination ids, and waiting-chain links. Incorrect flag combinations can create cycles, strand `in_progress`, or link to the wrong file. Incremental recursion has extra risk because prior groups may be skipped, freed, or represented only by cached path strings. Dry-run and alt-dest behavior can report a link target that is not actually present. Platform limits around hard-linking symlinks, devices, and special files are conditional and must match compile-time capabilities.

## Test Signals

Tests should cover hard-linked regular files in sorted and unsorted index modes, protocol pre-30 and post-30, incremental recursion groups spanning multiple file lists, skipped first/last/middle members, leaders still transferring, dry-run with link-dest, remove-source-files success, hard-linking symlinks/specials where supported and unsupported, alt-dest matches, and error paths for missing prior leaders.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/hlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/ifuncs.h -->
# sources/sync-backup/rsync/ifuncs.h

## Purpose

`ifuncs.h` defines small inline helpers used throughout rsync. The functions cover dynamic buffers, wire-mode portability, directory-entry name quirks, `stat_x` initialization/freeing, and allocation-backed string duplication.

## Important APIs, Types, And Functions

`alloc_xbuf(xbuf *xb, size_t sz)` allocates an `xbuf` buffer with zero length and position. `realloc_xbuf(xbuf *xb, size_t sz)` resizes an existing buffer through rsync's checked `realloc_array()`. `free_xbuf(xbuf *xb)` frees the buffer and clears the structure.

`to_wire_mode(mode_t mode)` maps platform symlink mode bits to rsync's wire value `0120000` when the local `_S_IFLNK` differs. `from_wire_mode(int mode)` maps that wire value back to local mode bits. `d_name(struct dirent *di)` hides `HAVE_BROKEN_READDIR` by returning `di->d_name - 2` on affected systems. `init_stat_x(stat_x *sx_p)` initializes create-time, ACL, and xattr fields. `free_stat_x(stat_x *sx_p)` frees ACL/xattr side data only when the corresponding preserve options are enabled. `my_strdup()` allocates and copies a string using `my_alloc()` and source location metadata.

## Control Flow

All functions are direct inline helpers. The mode conversion helpers conditionally rewrite only symlink type bits. `free_stat_x()` uses scoped `extern` declarations for `preserve_acls` and `preserve_xattrs` so callers can clean up optional data without duplicating feature checks.

## State, Dependencies, And Integration

The helpers have no persistent state. They depend on `rsync.h` types and allocation wrappers, ACL/xattr cleanup functions when compiled, and feature macros. `flist.c`, `generator.c`, `hlink.c`, and other modules use `init_stat_x()`/`free_stat_x()` around metadata comparisons and transfer setup; file-list serialization uses mode conversion helpers.

## Risks

Because these functions are inline and widely included, changes can affect many modules. `realloc_xbuf()` does not preserve the old pointer on failure because `realloc_array()` is expected to be fatal or checked by rsync allocation policy. `free_stat_x()` only frees optional data when preserve flags are currently enabled, so callers must keep flag state consistent with how the `stat_x` was populated. `d_name()` encodes a platform workaround that would be dangerous if enabled incorrectly.

## Test Signals

Compile with and without symlink support, ACLs, xattrs, and broken-readdir simulation. Test wire-mode round trips on platforms with nonstandard symlink bits, xbuf allocation/reallocation/free, and `stat_x` cleanup after ACL/xattr population.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/ifuncs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/install-sh -->
# sources/sync-backup/rsync/install-sh

## Purpose

`install-sh` is a portable shell implementation of the classic BSD/X11 install command. It installs files or creates directories during the build, with options for copy mode, permissions, owner/group changes, stripping, and filename transformation.

## Important APIs, Types, And Functions

The script is pure POSIX-style shell. It honors environment overrides `DOITPROG`, `MVPROG`, `CPPROG`, `CHMODPROG`, `CHOWNPROG`, `CHGRPPROG`, `STRIPPROG`, `RMPROG`, and `MKDIRPROG`. Supported options are `-c` to copy instead of move, `-d` to create a directory, `-m MODE`, `-o OWNER`, `-g GROUP`, `-s` to strip, `-t=SED_EXPR` to transform the basename, and `-b=SUFFIX` for transform basename handling.

## Control Flow

The argument parser records one source and one destination unless `-d` is used, in which case the source becomes the directory destination. It validates required operands and source existence, appends the source basename when destination is an existing directory, computes `dstdir` through sed, creates missing parent directories component by component, then either creates/configures the target directory or installs a file.

For file installation, it computes the final destination filename, applies optional basename transformation, creates a temporary file named `_inst.$$_` in the destination directory, moves or copies the source to the temp file, installs a trap to remove the temp file on exit, applies owner, group, strip, and mode commands, removes any old destination, and renames the temp file into place.

## State And Persistence

Persistent effects are filesystem changes only: parent directory creation, final file/directory creation, ownership/group/mode changes, optional stripping, and temporary file cleanup. `DOITPROG=echo` can turn actions into dry-run command printing.

## Dependencies And Integration Points

The script is used by make/install workflows and avoids relying on a platform `install` binary. It depends on shell, `sed`, `basename`, and the configured file utilities. The name `install-sh` avoids make implicit-rule conflicts with a target named `install`.

## Risks

The script is old and only lightly quoted. Paths with spaces, glob characters, leading dashes, or unusual IFS characters are risky in several tests and command invocations. Parent directory creation uses sed and `set -` path splitting rather than `mkdir -p`. Temporary file names use `$$`, which can collide in hostile/shared directories. Removing the old destination before the final move means a failure during `mv` can leave no installed file.

## Test Signals

Test regular file install, directory creation, install into existing directory, mode/owner/group/strip options, transform options, `DOITPROG=echo`, missing source/destination errors, nested parent creation, and paths containing spaces or shell metacharacters to document current portability limits.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/install-sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/inums.h -->
# sources/sync-backup/rsync/inums.h

## Purpose

`inums.h` provides inline numeric formatting wrappers used by debug, itemization, statistics, and logging paths. It centralizes the choice between raw, comma-formatted, and human-readable number rendering while delegating actual formatting to `do_big_num()` and `do_big_dnum()`.

## Important APIs, Types, And Functions

Integer helpers are `big_num(int64 num)`, `comma_num(int64 num)`, and `human_num(int64 num)`. Floating helpers are `big_dnum(double dnum, int decimal_digits)`, `comma_dnum(double dnum, int decimal_digits)`, and `human_dnum(double dnum, int decimal_digits)`.

`comma_num()` and `comma_dnum()` use `human_readable != 0` to request comma/grouped formatting from the underlying formatter. `human_num()` and `human_dnum()` pass the full `human_readable` level, allowing human-readable units when enabled.

## Control Flow

Each inline function immediately calls the appropriate formatter and returns its `char *` result. There is no local allocation or branching beyond reading the global `human_readable`.

## State, Dependencies, And Integration

The functions have no own state, but they depend on the global `human_readable` and on formatter functions that likely return static rotating buffers. Many modules include this header for concise logging, including file-list stats, checksum debug, hashtable debug, hard-link debug, and generator messages.

## Risks

Because results are `char *` values from shared formatter routines, callers should not assume long-lived ownership or unlimited simultaneous formatted values. Output changes when `human_readable` changes globally, so tests should set that option explicitly. Inline definitions in a header mean signature or semantic changes propagate widely at compile time.

## Test Signals

Test raw, comma, and human-readable output for small, large, negative, and floating values; multiple calls in one logging expression if formatter buffers rotate; and behavior with `human_readable` set to 0, 1, and higher levels.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/inums.h -->
