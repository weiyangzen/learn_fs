# subset-b-009109 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/damage.py -->
# sources/sync-backup/bup/lib/bup/cmd/damage.py

## Purpose
`damage.py` is a deliberately destructive testing command that corrupts byte ranges in one or more files. It is intended for recovery/fsck testing, not normal repository operation.

## APIs and Control Flow
The only helper is `randblock(n)`, which returns `n` pseudo-random bytes. `main(argv)` parses `--num`, `--size`, `--percent`, `--equal`, and `--seed`, then opens each target in `r+b`, computes a maximum corruption size, and writes random blocks either at random offsets or evenly spaced offsets. Input paths are normalized through `argv_bytes`; progress is logged with `path_msg`.

## State, Dependencies, Integration, Risks, Tests
The command mutates files in place and has no rollback. `--seed` makes corruption repeatable for tests. Empty files are risky because offset math assumes a positive size; large `--percent`/`--size` settings can overwrite most or all content. It integrates with `bup fsck` and parity-data tests by creating damaged pack or index files. Test signals are deterministic seed behavior, correct size/offset bounds, and refusal to run without filenames.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/damage.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/demux.py -->
# sources/sync-backup/bup/lib/bup/cmd/demux.py

## Purpose
`demux.py` is an internal stream demultiplexer used by remote execution, especially `bup on`, to recover a child command's stdout/stderr framing from a multiplexed channel.

## APIs and Control Flow
`main(argv)` rejects all positional arguments, flushes local stdout/stderr, wraps stdout with `byte_stream`, then opens a `DemuxConn` on stdin's file descriptor and `/dev/null` as the outgoing control sink. It reads lines from `DemuxConn.readline` until EOF and writes them to stdout.

## State, Dependencies, Integration, Risks, Tests
It depends on `bup.helpers.DemuxConn`, `byte_stream`, and option parsing. It persists no state; its only observable behavior is stream forwarding. It is tightly coupled to `cmd/mux.py` and `cmd/on.py` framing conventions. Risks are protocol drift, binary data assumptions around `readline`, and unexpected arguments from callers. Test signals include rejection of arguments, exact forwarding of muxed stdout, stderr flush behavior, and clean flush on exceptions/EOF.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/demux.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/drecurse.py -->
# sources/sync-backup/bup/lib/bup/cmd/drecurse.py

## Purpose
`cmd/drecurse.py` exposes the filesystem traversal engine as a CLI. It prints, profiles, or silently consumes the recursive directory listing used by indexing and backup flows.

## APIs and Control Flow
`main(argv)` requires exactly one path, parses literal and regex excludes, normalizes literal excludes relative to a relative traversal root, and calls `bup.drecurse.recursive_dirlist`. With `--profile` it consumes under `cProfile`; with `--quiet` it drains without output; otherwise it writes each path as bytes to stdout.

## State, Dependencies, Integration, Risks, Tests
The command does not persist state. It depends on `bup.drecurse`, exclude parsers, `argv_bytes`, and `byte_stream`. It is a direct diagnostic surface for the traversal behavior that `bup index` relies on. Risks center on path normalization differences between absolute and relative roots, regex/literal exclude parity with `index`, and traversal errors being reported through shared helper error state. Test signals include one-file-system behavior, exclude matching, profile/quiet modes, byte path output, and exact one-argument validation.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/drecurse.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/features.py -->
# sources/sync-backup/bup/lib/bup/cmd/features.py

## Purpose
`features.py` reports build/runtime capabilities for the installed bup executable: version, source commit/date, Python version, readline support, POSIX ACL support, and xattr support.

## APIs and Control Flow
`show_support(out, bool_opt, what)` formats a yes/no capability line. `main(argv)` rejects arguments, creates a byte stdout stream, prints `version.version`, `version.commit`, `version.date`, `platform.python_version`, and probes `_helpers.readline`, `_helpers.read_acl`, and `metadata.xattr`.

## State, Dependencies, Integration, Risks, Tests
The command is read-only and persists nothing. It depends on optional compiled helper symbols, metadata feature flags, and the generated `bup.version` module. It integrates with support/debug workflows and remote `bup on` commands where `features` is allowed without local repository server setup. Risks are misleading reports if optional helper imports are stubbed or if platform encoding cannot ASCII-encode the Python version. Test signals are no-argument enforcement and capability output under helper builds with/without readline, ACL, and xattr symbols.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/features.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/fsck.py -->
# sources/sync-backup/bup/lib/bup/cmd/fsck.py

## Purpose
`fsck.py` verifies pack integrity and optionally generates or uses par2 recovery data. It distinguishes normal verification, parity generation, repair, quick checksum verification, and a `--par2-ok` capability probe.

## APIs and Control Flow
Key helpers include `par2_setup`, `is_par2_parallel`, `par2`, `par2_generate`, `par2_recovery_file_status`, `git_verify`, `attempt_repair`, `do_pack`, and `merge_exits`. `main(argv)` configures global `opt`, discovers pack stems from arguments or the repository, reports stray pack-related files, determines mode, and processes packs serially or with forked workers limited by `--jobs`. Verification uses `git verify-pack` unless `--quick` checks trailing SHA1 checksums. Repair runs `par2 repair`, then regenerates missing/bad `.idx` with `git index-pack`.

## State, Dependencies, Integration, Risks, Tests
The command reads and may create/delete `.par2`, `.vol*.par2`, `.idx`, and temporary files near packs. It depends on external `par2` and `git`, pack naming conventions, `Sha1`, and bup exit constants where `EXIT_FALSE` can mean repair was needed or recovery info already existed. Risks include destructive repair mode, parity files left by interrupted tools, forked child error propagation, handling of missing pack/index files, and old par2 implementations lacking `-t1`. Test signals include parity status classification, quick checksum failures, generation tempdir cleanup, repair paths that rebuild indexes, parallel job exit merging, and `--par2-ok` incompatibility checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/fsck.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/ftp.py -->
# sources/sync-backup/bup/lib/bup/cmd/ftp.py

## Purpose
`ftp.py` is an interactive or scripted VFS browser for a bup repository. It supports `ls`, `cd`, `pwd`, `cat`, `get`, `mget`, help, and quit-style commands.

## APIs and Control Flow
`do_ls` delegates listing option parsing to `bup.ls`. `write_to_file` streams file contents with `chunkyreader`. Completion helpers use readline hooks and `vfs.contents`. `present_interface(stdin, out, extra, repo)` maintains a resolved VFS `pwd`, tokenizes shell-like input with `shquote.quotesplit`, resolves paths relative to `pwd`, and executes commands. `main(argv)` checks the repository and opens a `LocalRepo`.

## State, Dependencies, Integration, Risks, Tests
Runtime state is limited to current VFS directory and global completion cache/repo. `get` and `mget` write local files in the process working directory, using remote names or supplied local names. Dependencies include `_helpers.readline`, `vfs`, `ls`, `shquote`, `git`, and byte streams. Risks include encoding assumptions in terminal round-trips, local filename overwrite behavior, symlink dereference semantics in `mget`, and completion exceptions. Test signals include scripted command mode, relative path resolution, error messages for missing/non-directory paths, wildcard matching, and readline optionality.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/ftp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/fuse.py -->
# sources/sync-backup/bup/lib/bup/cmd/fuse.py

## Purpose
`fuse.py` mounts a bup repository VFS as a read-only FUSE filesystem using the `python-fuse` bindings, exposing repository paths to ordinary file tools.

## APIs and Control Flow
Import-time checks reject missing, fusepy-like, or too-old FUSE modules. `BupFs` implements `getattr`, `readdir`, `readlink`, `open`, and `read`. These methods convert FUSE string paths to argv bytes, resolve VFS items, augment metadata as requested, and stream file reads from `vfs.fopen`. `main(argv)` parses mount options, opens `LocalRepo`, configures foreground/debug/allow-other flags, and starts FUSE.

## State, Dependencies, Integration, Risks, Tests
The mount is read-only and persistent only while the process runs. It depends on `python-fuse`, `vfs`, `xstat`, metadata availability, and byte/path conversion. Risks include the file comment's known path handling limitations because FUSE paths are strings, incomplete offset support in `readdir`, fake metadata defaults unless `--meta` is supplied, and exposing repository content to other users with `--allow-other`. Test signals are import/version rejection, read-only enforcement, symlink reads, metadata times floored to seconds, and directory entry encoding.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/fuse.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/gc.py -->
# sources/sync-backup/bup/lib/bup/cmd/gc.py

## Purpose
`cmd/gc.py` is the CLI wrapper for bup garbage collection. It guards an experimental destructive operation behind `--unsafe` and forwards validated options to `bup.gc.bup_gc`.

## APIs and Control Flow
`main(argv)` parses verbosity, garbage threshold, compression, `--ignore-missing`, and `--unsafe`. It rejects positional arguments, requires `--unsafe`, validates `threshold` as an integer percentage from 0 to 100, checks that a repository exists, then invokes `bup_gc(threshold=..., compression=..., verbosity=..., ignore_missing=...)`.

## State, Dependencies, Integration, Risks, Tests
The wrapper itself persists nothing, but it triggers pack rewrites, bloom/midx clearing, reflog expiration, and object deletion in `bup.gc`. It depends on `git.check_repo_or_die`, option parsing, and the library GC implementation. Risks are mostly delegated: interrupted GC can leave derived indexes cleared and requires rerunning before adding data. Test signals include `--unsafe` refusal, threshold validation, no positional args, forwarding of compression/verbosity/ignore-missing, and repository requirement.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/gc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/get.py -->
# sources/sync-backup/bup/lib/bup/cmd/get.py

## Purpose
`get.py` transfers objects, commits, branches, saves, tags, or unnamed objects from a source bup/git repository to a destination repository. It supports fast-forward, append, pick, force-pick, new-tag, replace, unnamed fetch, optional rewrite/repair, and remote destination/source forms.

## APIs and Control Flow
Argument handling is custom through `argspec`, `usage`, `misuse`, `Spec`, and `parse_args`, because transfer methods carry ordered mode context. Resolvers (`resolve_src`, `resolve_ff`, `resolve_append`, `resolve_pick`, `resolve_new_tag`, `resolve_replace`, `resolve_unnamed`) validate all requested operations before writes. Handlers (`handle_ff`, `handle_append`, `handle_pick`, `handle_new_tag`, `handle_replace`, `handle_unnamed`) perform object walks with `get_random_item`, commit copying with `transfer_commit`, or save rewriting via `Rewriter`. `get_everything` compares hashsplit configs, creates a `Rewriter` when required, transfers all objects, accumulates ref updates, and updates refs only after successful writes.

## State, Dependencies, Integration, Risks, Tests
Persistent effects are new objects and final ref updates in the destination; rewrite/repair may record repair trailers in commit messages and returns `EXIT_RECOVERED` when repairs succeed. Dependencies include `repo_for_url`, `repo_for_location`, `vfs`, `git.walk_object`, `commit_message`, `RepairInfo`, `Rewriter`, and remote client error classes. Risks include config mismatch without explicit copy/rewrite choice, `--ignore-missing` being dangerous and limited to unnamed fetches, duplicate tag targeting, remote index suggestion races handled by rechecking existence, and ref update failures after object transfer. Test signals include parser ordering, resolver misuse cases, all transfer methods, delayed ref update atomicity, repair-id validation, excludes only for rewrite/repair, and missing object handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/get.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/help.py -->
# sources/sync-backup/bup/lib/bup/cmd/help.py

## Purpose
`help.py` dispatches to the top-level bup help or the system `man` command for a specific bup manual page.

## APIs and Control Flow
`main(argv)` parses exactly zero or one command argument. With no argument it `execvp`s `bup -h`. With one argument it builds `bup` or `bup-<command>`, checks for development manual pages under `../../Documentation`, temporarily sets `MANPATH` when present, and `execvp`s `man`. More than one argument is a fatal parse error.

## State, Dependencies, Integration, Risks, Tests
It replaces the process with `bup` or `man`, so there is no normal return on success. It mutates `os.environb['MANPATH']` only for the child exec path. Dependencies are `bup.path.exe`, `bup.path.exedir`, `glob`, and `argv_bytes`. Risks include missing `man`, stale development documentation paths, and command names that do not map to manuals. Test signals include no-arg exec target, one-arg docname construction, `MANPATH` injection when local manpage exists, and `EXIT_FAILURE` on `OSError`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/help.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/import_duplicity.py -->
# sources/sync-backup/bup/lib/bup/cmd/import_duplicity.py

## Purpose
`import_duplicity.py` imports duplicity backup history into a bup save branch by restoring each duplicity collection timestamp into a temporary directory, indexing it, and saving it with matching commit dates.

## APIs and Control Flow
`logcmd` and `exc` log commands and skip execution under `--dry-run`. `main(argv)` validates source URL and destination save name, checks the bup repository, creates a temporary work directory, runs `duplicity collection-status`, parses `full` and `inc` timestamp lines from the log, then for each timestamp runs duplicity restore, `bup index -uxf`, and `bup save --strip --date ... -f ... -n ...`. Cleanup removes the tempdir in `finally`.

## State, Dependencies, Integration, Risks, Tests
It writes temporary duplicity cache, restore, index, and log files, then appends commits to the destination branch. Dependencies are external `duplicity`, `rm`, the current bup executable, `git.check_repo_or_die`, and timestamp parsing via `timegm/strptime`. Risks include experimental status, shell command failures aborting via `check_call`, fragile parsing of duplicity output, and `finally` cleanup being skipped in dry-run semantics only through `exc`. Test signals include dry-run logging, timestamp extraction, command sequence order, cleanup behavior, and date preservation in saved commits.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/import_duplicity.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/index.py -->
# sources/sync-backup/bup/lib/bup/cmd/index.py

## Purpose
`index.py` maintains the filesystem index consumed by `bup save`. It updates, prints, checks, clears, and reports modified entries while storing compact metadata and hardlink information.

## APIs and Control Flow
`IterHelper` tracks the current old-index entry. `check_index` validates reader iteration invariants. `clear_index` removes stat/meta/hlink index files. `update_index` traverses paths with `recursive_dirlist`, compares new stat data against old entries, marks deleted paths, updates metadata through `MetaStoreWriter`, maintains `HLinkDB`, optionally fakes hash validity, and merges old/new index writers. `main(argv)` applies mode defaults, sleeps to avoid timestamp races, parses excludes, reduces paths, and handles update/print/status/modified/check flows.

## State, Dependencies, Integration, Risks, Tests
Persistent state is the bup index triple: stat index, metadata store, and hardlink database. Dependencies include `metadata.from_path`, `index.Reader/Writer`, `hlinkdb`, `recursive_dirlist`, exclude parsing, and default index path helpers. It directly feeds `save.py`, which trusts valid SHA and metadata offsets. Risks include timestamp race comments, device-change invalidation, deleted entries retained until merge policy changes, hardlink DB consistency, and fake-valid/invalid misuse. Test signals include stale detection, mode/status output, excludes/xdev behavior, metadata time clearing, merge with existing index, check-mode invariants, and `--clear` restrictions.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/index.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/init.py -->
# sources/sync-backup/bup/lib/bup/cmd/init.py

## Purpose
`init.py` creates a local or remote bup repository. It is the command-line entry for repository initialization through the unified repository location abstraction.

## APIs and Control Flow
`main(argv)` parses optional `-r/--remote` and at most one directory. A positional directory becomes a `file` URL with an absolute path and cannot be combined with `--remote`. Otherwise `main_repo_location` resolves the target. `repo_for_location(loc, create=True)` performs the actual initialization inside a context manager.

## State, Dependencies, Integration, Risks, Tests
The persistent effect is a new bup/git repository at the selected location. Dependencies include `URL`, `main_repo_location`, `repo_for_location`, `argv_bytes`, and `git.GitError`. Risks are ambiguous local-vs-remote target selection, poor diagnostics if remote creation fails, and filesystem permission errors. Test signals include positional/remote conflict, multiple-argument rejection, absolute local path conversion, remote path parsing, successful context open, and `EXIT_FAILURE` on `GitError`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/init.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/join.py -->
# sources/sync-backup/bup/lib/bup/cmd/join.py

## Purpose
`join.py` reconstructs file content from bup refs or object hashes by streaming joined blob/tree content to stdout or a named output file.

## APIs and Control Flow
`main(argv)` resolves an optional remote repository, reads refs from positional arguments or stdin lines, opens `repo_for_location`, and opens `-o` output if provided. For each ref it calls `src.join(ref)` and writes each returned blob to the output stream. `KeyError` is logged and returns failure.

## State, Dependencies, Integration, Risks, Tests
The command is read-only against the repository but can overwrite the output file path. Dependencies include `repo.join`, `linereader`, `byte_stream`, and `main_repo_location`. It integrates with split/save data retrieval and remote repository access. Risks include partial output before a later ref fails, missing object/ref errors surfacing as `KeyError`, and no explicit append/overwrite controls for `-o`. Test signals include stdin ref mode, remote repository opening, binary output correctness, output file handling, and failure after flushing partial data.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/join.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/list_idx.py -->
# sources/sync-backup/bup/lib/bup/cmd/list_idx.py

## Purpose
`list_idx.py` inspects bup/git `.idx` or `.midx` files and prints object hashes, optionally limited by a hex prefix.

## APIs and Control Flow
`main(argv)` validates at least one filename, converts `--find` to bytes, checks length <= 40 and valid hex after padding odd nibble counts, then opens each object index with `git.open_object_idx`. If the prefix is a full 40 hex chars it uses `exists`; otherwise it exhaustively scans hashes and writes matching `filename hash` lines.

## State, Dependencies, Integration, Risks, Tests
It is read-only. Dependencies are `git.open_object_idx`, `hexlify/unhexlify`, `add_error`, `handle_ctrl_c`, and progress output. It is a diagnostic companion to pack/midx maintenance. Risks include slow exhaustive scans for short prefixes, continuing after index-open errors through saved error state, and path byte/string handling. Test signals include invalid hex rejection, odd-length prefix padding, full-hash fast path, exhaustive prefix output, multiple index handling, and Ctrl-C handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/list_idx.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/ls.py -->
# sources/sync-backup/bup/lib/bup/cmd/ls.py

## Purpose
`cmd/ls.py` is a thin CLI adapter around `bup.ls`, listing repository VFS paths.

## APIs and Control Flow
`main(argv)` flushes stdout, wraps it as a byte stream, delegates all option parsing and listing behavior to `ls.via_cmdline(argv[1:], out=out)`, and exits with the returned code. The local file intentionally points readers to `lib/bup/ls.py` for the actual option specification.

## State, Dependencies, Integration, Risks, Tests
The command is read-only and persists nothing. Its dependencies are just `bup.ls` and `byte_stream`, but it is integrated wherever users expect `bup ls` and where `ftp.do_ls` reuses lower-level `bup.ls` functions. Risks are wrapper-level minimal: stdout byte behavior and correct exit-code propagation. Test signals should focus on delegation, flushing, returned status via `sys.exit`, and ensuring the wrapper does not alter argv semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/ls.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/margin.py -->
# sources/sync-backup/bup/lib/bup/cmd/margin.py

## Purpose
`margin.py` analyzes object ID distribution in the repository, reporting either the longest matching SHA1 prefix or prediction error for object offset distribution.

## APIs and Control Flow
`main(argv)` rejects positional arguments, checks the repo, opens `git.PackIdxList` with optional `ignore_midx`, and writes to stdout. In `--predict` mode `do_predict` compares each object's sorted position to its expected position from the first 64 hash bits. Default mode scans adjacent IDs, computes the maximum bit-prefix match using `_helpers.bitmatch`, and logs collision-capacity estimates.

## State, Dependencies, Integration, Risks, Tests
It is read-only. Dependencies include pack index iteration, `_helpers.bitmatch`, and math/struct calculations. It is diagnostic rather than core backup flow. Risks include division by zero for an empty object list, stale earth-population constant in explanatory output, and precision assumptions for very large indexes. Test signals include no-arg enforcement, midx vs idx-only selection, duplicate object skipping, predict output formatting, and behavior on small/empty repositories.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/margin.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/memtest.py -->
# sources/sync-backup/bup/lib/bup/cmd/memtest.py

## Purpose
`memtest.py` measures memory and lookup costs for pack index, midx, and bloom lookup paths by repeatedly testing object existence.

## APIs and Control Flow
`linux_memstat` optionally reads `/proc/self/status`. `report(count, out)` emits RSS, major faults, user/sys milliseconds, and elapsed milliseconds while updating global timing baselines. `main(argv)` rejects arguments, opens a `PackIdxList`, writes a header, warms random SHA generation, then for each cycle tests either real objects from an infinite iterator or random non-existing SHA values. It prints aggregate bloom/midx/idx search counters and total time.

## State, Dependencies, Integration, Risks, Tests
State is process-local globals for timing and search counters in imported modules. It persists nothing. Dependencies are Linux `/proc`, `resource.getrusage`, `_helpers.random_sha`, and pack index structures. Risks include platform-specific RSS units, infinite iterator assumptions when `--existing` has no objects, and assertions relying on negligible random SHA collisions. Test signals include output schema, `--existing` behavior, `--ignore-midx`, cycle/number handling, and graceful missing `/proc` warning once.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/memtest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/meta.py -->
# sources/sync-backup/bup/lib/bup/cmd/meta.py

## Purpose
`meta.py` is a metadata archive utility. It can create, list, extract, start/finish extraction, or edit bup metadata streams independently of full repository save/restore operations.

## APIs and Control Flow
`open_input` and `open_output` map empty or `-` names to byte stdin/stdout. `main(argv)` prepends default `--paths --symlinks --recurse`, enforces exactly one action, sets `metadata.verbose`, and delegates to `metadata.save_tree`, `display_archive`, `start_extract`, `finish_extract`, `extract`, or archive iteration plus field mutation for `--edit`. `--edit` applies the last relevant user/group set/unset flag semantics while uid/gid are parsed as integers.

## State, Dependencies, Integration, Risks, Tests
Create/list/edit read and write archive streams; extract modes create filesystem paths and apply metadata. Dependencies are `bup.metadata`, byte streams, and `argv_bytes`. Integration points are `.bupm` metadata compatibility and restore-like ownership handling. Risks include private `_ArchiveIterator` use, destructive filesystem extraction, conflicting action/argument combinations, and stream output corruption if stdout is not flushed/wrapped. Test signals include one-action enforcement, stdin/stdout file handling, recurse/xdev/symlink flags, numeric-id extraction, edit ordering, and invalid uid/gid errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/meta.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/midx.py -->
# sources/sync-backup/bup/lib/bup/cmd/midx.py

## Purpose
`midx.py` builds, checks, and prunes multi-index files that aggregate many pack indexes into faster lookup structures.

## APIs and Control Flow
`_maybe_open_midx` handles missing referenced idx files and optionally removes broken midx files. `check_midx` verifies sub-index membership, midx membership, and ordering. `_do_midx` opens idx/midx inputs, calculates a fanout table size from object count/pages, writes an atomic `.midx` header/table/object/name map, and uses `_helpers.merge_into` over an mmap. `do_midx_dir` removes redundant midxes, groups inputs according to high/low water marks and fd limits, and repeatedly calls `do_midx_group`. `main(argv)` validates modes, resolves pack dir, fd limits, check/build/auto/force behavior, and optional printed names.

## State, Dependencies, Integration, Risks, Tests
Persistent state is `.midx` files in `objects/pack`; auto/force can remove redundant or broken midxes. Dependencies include `git.open_idx`, `midx.open_midx`, `resource.RLIMIT_NOFILE`, atomic file replacement, fsync, mmap, and object index layout. It integrates with lookup-heavy commands and GC, which clears midxes before rewriting packs. Risks include fd limit miscalculation, broken midx cleanup, output filename collisions, stale references, and correctness of sorted object merges. Test signals include check failures, missing idx handling, auto thresholds, force single-output behavior, max-files grouping, atomic output, and redundant midx deletion.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/midx.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/mux.py -->
# sources/sync-backup/bup/lib/bup/cmd/mux.py

## Purpose
`mux.py` runs a subcommand and multiplexes its stdout and stderr into bup's framed stream protocol. It is paired with `demux.py` for remote command execution.

## APIs and Control Flow
`main(argv)` duplicates original stdin, replaces fd 0 with `/dev/null` while parsing options, requires a command, creates stdout/stderr pipes, spawns the subcommand with original stdin and pipe outputs, writes the `BUPMUX` header to stdout, and calls `helpers.mux` to frame both output streams. It waits for the child and exits with the child's status.

## State, Dependencies, Integration, Risks, Tests
State is process/file-descriptor state only. It depends on `Popen`, `stopped`, `byte_stream`, `helpers.mux`, and exact fd inheritance behavior. It integrates with `on__server.py`, which prepends `mux --` to remote argv, and `demux.py`, which consumes the framed stream. Risks include descriptor leaks from `close_fds=False`, protocol header mismatch, subcommand stdin ownership, and timeout behavior in `stopped`. Test signals include stdout/stderr interleaving preservation, child exit propagation, missing command fatal, and stdin redirection semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/mux.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/on.py -->
# sources/sync-backup/bup/lib/bup/cmd/on.py

## Purpose
`on.py` runs selected bup commands on a remote host over SSH while providing a local protocol server for commands that need repository access. It enables reverse backup/restore-style workflows with constrained server permissions.

## APIs and Control Flow
`run_server` wraps an SSH child with `Conn` and `protocol.Server`. `restricted_repo_config` only allows `init-dir`/`set-dir` requests that match the local repo. `save_or_split_server_config` parses the local command options and vets ref updates so save/split can only update the expected branch with a new commit descending from the previous one. `main(argv)` parses host/port and subcommand, chooses a server config for supported commands, starts remote `on--server`, sends NUL-separated argv with a length prefix, runs local server if needed, and demuxes remote stderr output.

## State, Dependencies, Integration, Risks, Tests
It may update the local repository through a restricted protocol server; the remote host runs the actual bup command. Dependencies include SSH transport, `protocol.Server`, `LocalRepo`, command parsers from save/split, `parse_commit`, and mux/demux. Risks include command authorization gaps, ref-vetting assumptions, unsupported command handling, host parsing with colons, and deadlocks around SSH pipes. Test signals include supported-command matrix, init rejection, restricted repo path enforcement, save/split ref update vetting, remote argv framing, demux output, and return-code propagation.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/on.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/on__server.py -->
# sources/sync-backup/bup/lib/bup/cmd/on__server.py

## Purpose
`on__server.py` is the remote helper launched by `bup on`. It receives a length-prefixed argv vector safely over stdin and execs the requested command under `bup mux`.

## APIs and Control Flow
`main(argv)` rejects arguments, reads a 4-byte big-endian size and bounded payload from byte stdin, splits NUL-separated argv, replaces argv[0] with `path.exe()`, and prepends `mux --`. It moves stdin/stdout to fds 3 and 4 for server communication, redirects stdout to stderr for subcommand-visible output, replaces stdin with `/dev/null`, sets `BUP_SERVER_REVERSE`, then `execvp`s bup.

## State, Dependencies, Integration, Risks, Tests
Persistent state is only the environment variable inherited by the execed command. File descriptor reshaping is the main side effect. It depends on exact fd expectations in remote client/server code and mux. Risks include malformed size/payload assertions, fd collision assumptions, stdout/stderr confusion for subcommands, and exec failure returning 99. Test signals include argv framing, size bound, fd 3/4 availability, `BUP_SERVER_REVERSE`, stdin denial, and mux argv construction.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/on__server.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/prune_older.py -->
# sources/sync-backup/bup/lib/bup/cmd/prune_older.py

## Purpose
`prune_older.py` removes old saves according to retention windows and optionally runs garbage collection afterward. It is experimental and requires `--unsafe`.

## APIs and Control Flow
`branches` yields selected head names and hashes. `classify_saves` assumes decreasing UTC order and retains all saves in the newest window, then the newest save per day/month/year for configured windows, then drops older saves. `main(argv)` parses retention periods relative to `--wrt` or current time, logs effective windows, enumerates branch revisions with author times, derives save names using `save_names_for_commit_utcs`, prints intended actions under `--pretend`, or calls `bup_rm` and then `bup_gc`.

## State, Dependencies, Integration, Risks, Tests
Persistent effects are ref/history rewrites via `bup_rm` and pack cleanup via `bup_gc`. Dependencies include `git.rev_list`, `period_as_secs`, `partition`, `LocalRepo`, `bup_rm`, and `bup_gc`. Risks include dangerous experimental deletion, memory use from building full rev lists, reliance on save-name derivation rather than hashes, timezone/localtime grouping, and retention window edge cases. Test signals include `--unsafe` gate, period parsing, `--pretend` output, classification ordering, branch filters, error gating via `die_if_errors`, and optional GC invocation.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/prune_older.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/random.py -->
# sources/sync-backup/bup/lib/bup/cmd/random.py

## Purpose
`random.py` emits deterministic pseudo-random bytes, primarily for tests, benchmarks, and data generation pipelines.

## APIs and Control Flow
`main(argv)` requires exactly one byte-count argument, parses it with `parse_num`, installs Ctrl-C handling, and only writes binary data to stdout when `--force` is set or stdout is not a terminal. Actual generation is delegated to `_helpers.write_random(fd, total, seed, verbose_flag)`.

## State, Dependencies, Integration, Risks, Tests
The command persists nothing but can flood stdout with binary data. Dependencies are compiled helper generation, terminal detection through `istty1`, and parse helpers. Risks include accidental terminal corruption, huge byte counts, and seed semantics depending on `_helpers.write_random`. Test signals include parse suffixes, tty refusal without `-f`, deterministic output for a seed, verbose byte counter behavior, and Ctrl-C handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/random.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/restore.py -->
# sources/sync-backup/bup/lib/bup/cmd/restore.py

## Purpose
`restore.py` extracts files and directories from a bup repository VFS into the filesystem, preserving metadata, optional sparse files, hardlinks, and configurable owner/group mappings.

## APIs and Control Flow
Important helpers are `valid_restore_path`, `parse_owner_mappings`, `apply_metadata`, `hardlink_compatible`, `hardlink_if_possible`, `write_file_content`, `write_file_content_sparsely`, and recursive `restore`. `main(argv)` parses remote/outdir/exclude/mapping options, opens a repository, resolves each requested path with metadata, follows `latest` links specially, and either restores children into the current directory or restores the leaf name. Directory restore creates paths, descends with `vfs.contents`, then applies metadata after children; file restore creates content, handles sparse writes and hardlink reuse, then applies metadata.

## State, Dependencies, Integration, Risks, Tests
Persistent state is the restored filesystem tree and metadata. Dependencies include `vfs`, `metadata` behavior through item metadata, `_helpers.write_sparsely`, owner mappings, `repo_for_location`, and exclude regex semantics shared with indexing. Risks include destructive overwrite/metadata application, path validation requiring branch and revision, hardlink compatibility false positives/negatives, sparse truncation correctness, symlink and special-file creation, and global `total_restored`. Test signals include latest handling, directory `.` semantics, owner map parsing, exclude behavior, sparse output, hardlink restoration order, metadata application timing, and outdir creation.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/restore.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/rm.py -->
# sources/sync-backup/bup/lib/bup/cmd/rm.py

## Purpose
`rm.py` removes branches or saves from a bup repository through the shared `bup.rm.bup_rm` implementation. It is an experimental destructive command guarded by `--unsafe`.

## APIs and Control Flow
`main(argv)` parses compression, verbosity, `--unsafe`, and one or more target paths. It refuses to run without `--unsafe`, requires at least one path, checks that the repository exists, opens `LocalRepo`, converts targets to bytes, and calls `bup_rm(repo, targets, compression=..., verbosity=...)`.

## State, Dependencies, Integration, Risks, Tests
Persistent effects are delegated to `bup_rm`, likely including ref updates and new pack/object state for rewritten reachable history. Dependencies are `Options`, `check_repo_or_die`, `LocalRepo`, and `argv_bytes`. Risks are destructive target interpretation, no pretend mode here, and compression defaults influencing rewritten objects. Test signals include unsafe gate, target requirement, compression/verbosity forwarding, byte path conversion, and repository-open lifetime around `bup_rm`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/rm.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/save.py -->
# sources/sync-backup/bup/lib/bup/cmd/save.py

## Purpose
`save.py` creates bup tree and commit objects from the filesystem index, preserving metadata and hardlink relationships, and optionally updating a named backup branch.

## APIs and Control Flow
`opts_from_cmdline` validates output mode, sources, date, size/bandwidth limits, strip/strip-path/graft behavior, save name, and destination repo. `save_tree` is the core: it reads index entries, optionally precomputes progress totals, maps filesystem paths to archive paths, uses `Stack` to build nested git trees, writes `.bupm` metadata entries, reuses valid indexed object IDs, hashes changed regular files with `split_to_blob_or_tree`, writes symlinks or empty blobs for special files, validates/repackages index entries, and handles root metadata collisions. `commit_tree` writes a commit with bup trailers. `main` opens destination repo, index/metastore/hlink DB, calls `save_tree`, prints requested tree/commit IDs, and updates the named branch.

## State, Dependencies, Integration, Risks, Tests
Persistent effects include new blobs/trees/commits, optional branch update, and updated index entries. Dependencies are `hashsplit`, `index`, `metadata`, `hlinkdb`, `tree.Stack`, `repo_for_location`, `open_noatime`, and commit-message helpers. Risks include filesystem races between index and save, mode changes after indexing, root/strip/graft collisions, incorrect metadata sort-key assumptions documented in comments, sparse/hardlink metadata consistency, and remote bandwidth/client failures. Test signals include mode validation, strip/graft conflicts, index-missing error, metadata `.bupm` ordering, changed-file hashing, skipped large files, branch parent update, and progress math.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/save.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/server.py -->
# sources/sync-backup/bup/lib/bup/cmd/server.py

## Purpose
`server.py` starts a bup protocol server on stdin/stdout, serving repository operations to clients over an existing transport such as SSH.

## APIs and Control Flow
`main(argv)` rejects arguments, logs a debug message, defines a `ServerRepo` subclass that checks the requested repo and initializes `LocalRepo` with a server reference, then wraps byte stdin/stdout in `Conn` and runs `protocol.Server.handle()`.

## State, Dependencies, Integration, Risks, Tests
Persistent effects depend on allowed protocol commands: reads, object writes, and ref updates can occur through the server. Dependencies include `protocol.Server`, `LocalRepo`, `git.check_repo_or_die`, and `helpers.Conn`. It integrates with remote repository clients and generic bup transport. Risks include broad protocol exposure compared with `on.py` restricted configs, transport EOF/error behavior, and repository path validation. Test signals include no-argument enforcement, byte-stream wrapping, server command handling through `Conn`, and `ServerRepo` repo validation.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/server.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/split.py -->
# sources/sync-backup/bup/lib/bup/cmd/split.py

## Purpose
`split.py` chunks input data with bup's rolling hashsplit algorithm and writes blobs, trees, commits, named saves, copied input, or no-op benchmark output.

## APIs and Control Flow
`opts_from_cmdline` validates mutually exclusive modes, git-id input, pack sizing, fanout, bandwidth, date, remote repo, `BUP_SERVER_REVERSE` stdin restrictions, and save names. `split` applies progress callbacks, then chooses `split_to_blobs`, `split_to_blob_or_tree`, `split_to_shalist`, or raw hashsplit iteration depending on mode. It prints blob/tree/commit IDs as requested and creates commit messages with trailers. `main` configures hashsplit fanout and client bandwidth, opens stdin/files or git object iterators, conditionally opens/creates a repository, loads split config, writes objects or calculates null hashes, and updates a named ref after writing.

## State, Dependencies, Integration, Risks, Tests
Persistent effects are blobs/trees/commits and optional branch ref updates; `--copy` and `--noop` avoid repository writes. Dependencies include `hashsplit`, repo location helpers, `git.CatPipe`, packwriter options, commit helpers, and config parsing. Risks include option interaction bugs, `--max-pack-objects` assigning to `max_pack_size` in code, stdin restrictions under reverse server mode, ref update after writes, and benchmark division by zero for instant runs. Test signals include all mode combinations, git-id streaming, keep-boundaries, no-repo copy/noop behavior, named save dummy tree entry, remote writes, and compression/pack limits.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/split.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/tag.py -->
# sources/sync-backup/bup/lib/bup/cmd/tag.py

## Purpose
`tag.py` lists, creates, overwrites, or deletes lightweight bup/git tags under `refs/tags`.

## APIs and Control Flow
`main(argv)` checks the repo and flattens `git.tags()` values. With `--delete` it verifies existence unless `--force`, then calls `git.delete_ref`. With no args it prints all tags. With two args it validates non-empty/non-dot tag name, resolves the commit via `git.rev_parse`, confirms the object exists in `PackIdxList`, and updates `refs/tags/<tag>` with force semantics.

## State, Dependencies, Integration, Risks, Tests
Persistent state is tag refs. Dependencies include `git.tags`, `rev_parse`, `PackIdxList`, `update_ref`, and `delete_ref`. Risks include comment-marked need to review safe writes, force overwrite behavior, tag listing order from git tag map, and creation of tags pointing to existing objects that may not be commits despite variable naming. Test signals include listing, missing delete with/without force, dot-prefix rejection, duplicate tag rejection, nonexistent commit handling, object existence checks, and force update.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/tag.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/tick.py -->
# sources/sync-backup/bup/lib/bup/cmd/tick.py

## Purpose
`tick.py` sleeps until the next whole-second boundary. It is a small timing helper used to avoid timestamp-resolution races in tests or scripts.

## APIs and Control Flow
`main(argv)` rejects arguments, reads `time.time()`, computes the fractional remainder to the next integer second as `1 - (t - int(t))`, and sleeps that amount.

## State, Dependencies, Integration, Risks, Tests
It persists nothing and depends only on `time` and option parsing. It is conceptually related to the explicit one-second wait in `index.py` for timestamp race avoidance. Risks are minimal: if called exactly on a boundary it sleeps a full second, and system clock adjustments are not considered. Test signals include no-argument enforcement and elapsed sleep falling within expected bounds relative to the next second.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/tick.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/validate_object_links.py -->
# sources/sync-backup/bup/lib/bup/cmd/validate_object_links.py

## Purpose
`validate_object_links.py` scans pack contents and reports missing object links from commits and trees to their referenced parents, trees, and child entries.

## APIs and Control Flow
`obj_type_and_data_ofs` parses Git pack object header kind and compressed-data offset. `Pack` opens a pack associated with an idx, iterates non-blob objects by offset order, decompresses whole commit/tree/tag objects directly or resolves deltas through `catpipe`, and yields `(oid, type, data)`. `main(argv)` rejects args, checks the repo, counts objects, iterates every idx and pack, derives referenced SHA lists from `tree_iter` or parsed commits, and checks existence in `PackIdxList`.

## State, Dependencies, Integration, Risks, Tests
It is read-only and returns `EXIT_FALSE` when missing links are found. Dependencies include pack file format, `git.tree_iter`, `git.parse_commit`, `PackIdxList`, `pairwise`, and zlib. Risks include assuming pack version 2 and 5-byte headers are enough for 4GiB objects, skipping tag objects, private idx methods, and object count zero division in progress. Test signals include missing child detection, delta object handling, tag warning, no-argument fatal, pack header parsing, and progress across multiple idx files.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/validate_object_links.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/validate_ref_links.py -->
# sources/sync-backup/bup/lib/bup/cmd/validate_ref_links.py

## Purpose
`validate_ref_links.py` is a compatibility wrapper that runs `validate_refs` in link-validation mode.

## APIs and Control Flow
`main(argv)` parses only verbosity and optional refs, constructs a new argv beginning with the original program name, repeats `-v`, appends `--links`, appends byte refs, and returns `validate_refs.main(args)`.

## State, Dependencies, Integration, Risks, Tests
It is read-only apart from validation output. Dependencies are `bup.cmd.validate_refs`, option parsing, and `argv_bytes`. It exists to expose a narrower command name/API for missing-link checks. Risks are wrapper drift if `validate_refs` changes option names or if verbosity semantics differ. Test signals include argument forwarding, multiple `-v` preservation, byte ref conversion, and return-code propagation from `validate_refs`.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/validate_ref_links.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/validate_refs.py -->
# sources/sync-backup/bup/lib/bup/cmd/validate_refs.py

## Purpose
`validate_refs.py` validates selected or all repository refs for missing linked objects and malformed or abridged `.bupm` metadata.

## APIs and Control Flow
`expected_bup_entry_count_for_tree` counts expected metadata entries from tree data, treating `.bupd` chunked directories specially. `resolve_refs` maps VFS refs to object IDs and reports missing refs. `main(argv)` requires at least one validation mode unless both option values are `None`, opens `LocalRepo`, resolves refs, defines `for_item` for `find_live_objects`, reports missing objects, parses `.bupm` streams with `Metadata.read`, compares counts to expected tree entries, and returns `EXIT_FAILURE`, `EXIT_FALSE`, or `EXIT_TRUE` according to severity.

## State, Dependencies, Integration, Risks, Tests
It is read-only. Dependencies include `bup.gc.count_objects/find_live_objects`, `vfs`, `git.walk_object` behavior, metadata parsing, `tree_data_reader`, and pack idx broad existence checks when `--links` is enabled. It integrates with validation wrappers and GC's mark traversal. Risks include incomplete missing-object lists without `--links`, unsupported VFS item kinds, exception escalation for unparsable `.bupm`, and nuanced exit codes. Test signals include all/no refs, missing ref handling, missing object notices, extra vs abridged bupm counts, `.bupd` handling, and default option behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/validate_refs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/version.py -->
# sources/sync-backup/bup/lib/bup/cmd/version.py

## Purpose
`version.py` prints the bup version, build/source date, or commit ID.

## APIs and Control Flow
The module defines `version_rx`, a regex for acceptable version strings, though this file does not use it directly. `main(argv)` rejects positional arguments, allows at most one of `--date` and `--commit`, wraps stdout as bytes, and writes `version.date` truncated at the first space, `version.commit`, or `version.version`.

## State, Dependencies, Integration, Risks, Tests
It is read-only and depends on generated `bup.version` values plus byte-stream output. It is used by support diagnostics and remote command allowlists. Risks are minimal: unused `version_rx` can drift, `date.split` assumes byte date format, and option booleans are summed numerically. Test signals include no-arg version output, date and commit modes, mutual exclusion, unexpected arg fatal, and byte newline formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/version.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/web.py -->
# sources/sync-backup/bup/lib/bup/cmd/web.py

## Purpose
`web.py` serves a read-only HTTP view of a bup repository using Tornado. It lists directories with optional metadata/hash/hidden/human-size query parameters and streams file content.

## APIs and Control Flow
Parameter helpers (`ParamInfo`, `request_params`, `encode_query`, `from_req_bool`) validate and normalize query state. `_compute_breadcrumbs`, `_contains_hidden_files`, and `_dir_contents` prepare listing template data from VFS resolution. `BupRequestHandler` overrides path argument decoding, handles GET/HEAD, resolves paths with metadata, redirects directories to trailing slash, renders `list-directory.html`, sets file headers (`Last-Modified`, `Content-Type`, `Etag`, `Content-Length`), and streams file chunks with deferred header setting. `main(argv)` parses inet or `unix://` bind address, opens `LocalRepo`, configures Tornado static/template paths, binds sockets, optionally opens a browser, and starts the IOLoop. SIGTERM stops the loop.

## State, Dependencies, Integration, Risks, Tests
Persistent state is none, but it exposes repository data over HTTP for the process lifetime. Dependencies include Tornado, `vfs`, `metadata`, `xstat`, resource templates/static assets, MIME types, and local repo access. Risks include debug mode enabled, broad exception-to-500 handling, strict query rejection producing unhandled `ValueError`, hidden-file double traversal, byte/path quoting issues, UNIX socket/browser incompatibility, and response headers delayed until first chunk. Test signals include directory redirect/listing, query normalization, hidden/meta/hash rendering, HEAD vs GET headers, file streaming errors, address parsing, SIGTERM shutdown, and missing Tornado failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/web.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/xstat.py -->
# sources/sync-backup/bup/lib/bup/cmd/xstat.py

## Purpose
`xstat.py` prints detailed bup metadata for filesystem paths, with selectable metadata fields and timestamp resolution reduction.

## APIs and Control Flow
`parse_timestamp_arg` converts resolution tokens through `parse_timestamp`, requires the result to be 1 or a power of 10, and reports fatal parse errors. `main(argv)` parses include/exclude field flags in order, establishes the active metadata field set, sets `metadata.verbose`, then for each path calls `metadata.from_path(path, archive_path=path)`, rounds atime/mtime/ctime down when requested, and writes `metadata.detailed_bytes`.

## State, Dependencies, Integration, Risks, Tests
It is read-only except for stdout. Dependencies include `metadata.all_fields`, `metadata.from_path`, `metadata.detailed_bytes`, byte argv, and `parse_timestamp`. Risks include field order semantics, float division from `/` when rounding timestamps if values are ints, skipping ENOENT through `add_error`, and path metadata errors for special files. Test signals include resolution validation, include-before-exclude behavior, unknown fields, missing path handling, verbose/quiet effect, and formatting for multiple paths with blank separators.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/cmd/xstat.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/commit.py -->
# sources/sync-backup/bup/lib/bup/commit.py

## Purpose
`commit.py` parses and constructs Git commit metadata used by bup save/get/split and annotates bup-created commits with version and argv trailers.

## APIs and Control Flow
`parse_tz_offset` converts `+HHMM`/`-HHMM` to seconds. `parse_commit_gpgsig` removes Git continuation formatting. Regex constants define accepted safe author/committer fields, parents, mergetag, optional gpgsig, and message. `CommitInfo` stores parsed fields. `parse_commit` matches the regex and returns typed fields. `_local_git_date_str`, `_git_date_str`, and `create_commit_blob` format commit headers. `has_trailers` detects a trailer block. `commit_message` appends `Bup-Version`, shell-encoded `Bup-Argv`, and optional ASCII trailers, inserting a blank line when needed.

## State, Dependencies, Integration, Risks, Tests
The module is pure except for importing current bup `version`. It depends on regex correctness, `utc_offset_str`, and `enc_sh`. It integrates with `save`, `split`, `get`, and remote ref-vetting in `on.py`. Risks include incomplete Git commit grammar coverage, mergetag/gpgsig assumptions, strict safe string regex rejecting valid commits, and trailer detection differing from Git's full interpreter. Test signals include parsing commits with multiple parents, timezone signs, gpgsig continuation, message trailers, create/parse round trips, and argv shell encoding.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/commit.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/compat.py -->
# sources/sync-backup/bup/lib/bup/compat.py

## Purpose
`compat.py` centralizes Python-version compatibility and process argv byte handling for bup.

## APIs and Control Flow
It exports `environ`, `fsencode`, `pairwise` for Python < 3.10, `print_exception` with 3.10-style calling on older versions, `argv_bytes`, `get_argvb`, `get_argv`, `dataclass`, and `dataclass_frozen_for_testing`. `argv_bytes` uses `os.fsencode`; `get_argvb` and `get_argv` read original bytes from `bup_main.argv`. The dataclass wrapper drops `slots` on older Python, and the testing variant only freezes when `BUP_TEST_LEVEL` is set.

## State, Dependencies, Integration, Risks, Tests
State depends on Python version and environment. Dependencies include `bup_main`, `dataclasses`, and `traceback`. This module is imported broadly by command parsers and typed data structures to preserve byte argv semantics. Risks include losing slots behavior on older Python, `dataclass_frozen_for_testing` changing mutability only under tests, surrogateescape decode assumptions, and compatibility wrappers falling behind Python APIs. Test signals include pairwise fallback, print_exception compatibility, original argv byte preservation, dataclass slots/frozen behavior across env settings, and `get_argv` decoding.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/compat.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/config.py -->
# sources/sync-backup/bup/lib/bup/config.py

## Purpose
`config.py` provides configuration-related errors and remote option URL parsing for bup's repository abstractions.

## APIs and Control Flow
`ConfigError` is a marker exception used by configuration readers. `url_for_remote_opt(remote)` parses `--remote`-style bytes. It first attempts `parse_bytes_path_url(remote, require_auth=True)` and, if that returns an error/none, falls back to legacy `user@host:path` parsing. It supports ssh, bup, and bup-rev schemes with scheme-specific validation; `host == b'-'` creates an ssh URL without host for subprocess testing.

## State, Dependencies, Integration, Risks, Tests
The module is pure. Dependencies are `URL`, `parse_bytes_path_url`, and `path_msg` for diagnostics. It integrates with repo location helpers used by init/save/split/restore/get and remote client setup. Risks include subtle legacy parsing (`rpartition('@')`, first colon in hostpath), bup URL user/path restrictions, and returning either `URL` or diagnostic string. Test signals include legacy user containing `@`, missing colon/host, ssh test subprocess remote, bup/bup-rev validation, unexpected scheme errors, and bytes diagnostic formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/config.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/drecurse.py -->
# sources/sync-backup/bup/lib/bup/drecurse.py

## Purpose
`drecurse.py` is the low-level directory traversal engine for indexing and diagnostic traversal. It performs byte-path, no-follow, no-atime recursive listing with exclude and filesystem-boundary controls.

## APIs and Control Flow
`_dirlist(fd, path)` lists a directory by fd, `lstat`s entries relative to that fd, appends `/` to directory names, sorts reverse, and returns `(name, stat)` pairs. `_recursive_dirlist` filters literal and regex excludes, skips the bup repo directory, enforces `xdev` except for allowed paths, yields files immediately, descends into directories with `openat_noatime(... O_NOFOLLOW|O_DIRECTORY)`, yields children, then yields the directory path. `recursive_dirlist(paths, xdev, ...)` validates byte paths, stats each root, handles non-directories, opens directory roots, sets the starting device when xdev is enabled, and yields post-order directory entries.

## State, Dependencies, Integration, Risks, Tests
It persists nothing but reports errors through shared helper error state. Dependencies include `xstat.lstat`, compiled no-atime open helpers, `finalized`, `resolve_parent`, and regex exclude helpers. It integrates with `cmd/index.py` and `cmd/drecurse.py`. Risks include reverse sorting/post-order expectations required by index merge logic, symlink loop avoidance through no-follow flags, bytes/path formatting bugs in debug strings, permission errors, and filesystem boundary exceptions. Test signals include post-order traversal, file-vs-directory names, bup_dir exclusion, xdev skip-yield behavior, open/stat errors, exclude matching, and relative/absolute byte paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/drecurse.py -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/gc.py -->
# sources/sync-backup/bup/lib/bup/gc.py

## Purpose
`gc.py` implements bup's mark-and-sweep garbage collector. It identifies live objects reachable from refs, rewrites/deletes packs with garbage, and refreshes derived lookup structures.

## APIs and Control Flow
`count_objects` sums object counts across idx files. `report_missing` logs missing objects for ignore-missing mode. `find_live_objects` creates a temporary Bloom filter for live blobs plus a set of live non-blobs, walks refs with `walk_object`, optionally uses broad `PackIdxList` existence checks, and returns liveness structures. `sweep` opens a `LocalRepo` writer with duplicate allowance and an `on_pack_finish` callback, scans each idx, decides whether packs are fully dead, sufficiently live, or require rewrite, writes live objects to new packs, queues stale pack stems, and deletes stale pack-related files after safe points. `bup_gc` counts objects, marks live data, clears midxes/bloom/reflog, calls `sweep`, and warns if interrupted.

## State, Dependencies, Integration, Risks, Tests
Persistent effects include deleting pack files, writing new packs, clearing `bup.bloom`, removing `.midx`, and expiring Git reflogs. Dependencies include `bloom.BloomWriter`, `git.walk_object`, `git.catpipe`, `midx.clear_midxes`, `bloom.clear_bloom`, `LocalRepo`, and external `git reflog expire`. Risks are probabilistic blob retention, interruption after clearing derived data, missing object handling, stale pack deletion timing, reliance on pack stem regex, remote/client index cache interactions, and memory use for live trees. Test signals include zero-object no-op, missing object failure vs ignore logging, live object marking, threshold rewrite decisions, pack deletion after callback, abort on exceptions, reflog command failure, and derived index cleanup.
<!-- END_FILE_RESEARCH: sources/sync-backup/bup/lib/bup/gc.py -->
