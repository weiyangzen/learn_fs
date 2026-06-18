# Group Research: group_354_e2fsprogs_sources_local_fs_e2fsprogs_misc_tune2fs_c_sources_local_fs_6394341ae1dc

Scope: `Docs/research_subset_a.md`; source tree: `sources/local-fs/e2fsprogs`.

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/tune2fs.c -->
# File Research: sources/local-fs/e2fsprogs/misc/tune2fs.c

## Purpose
Implements `tune2fs`, plus optional `e2label` and `findfs` entry behavior, for inspecting and changing ext2/ext3/ext4 superblock parameters, feature flags, journals, quotas, UUIDs, labels, inode size, MMP state, checksums, and related filesystem metadata.

## Key Elements
Global option state records every command-line mutation request, including mount-count policy, error behavior, reserved block ownership/counts, label and last-mounted strings, UUID changes, feature edits, default mount options, journal settings, quota changes, extended options, inode-size expansion, 64-bit conversion requests, checksum rewrites, undo files, and orphan-file creation.

Feature handling is centered in `update_feature_set`. It validates requested `-O` feature edits against explicit set/clear masks, performs side effects for journal removal/addition, orphan files, sparse superblocks, MMP, dir_index, flex_bg, huge_file, metadata_csum, uninit_bg/GDT checksums, 64bit handoff to `resize2fs`, quota/project flags, encryption defaults, casefold encoding, and metadata_csum_seed. Dangerous operations require clean fsck state, unmounted or read-only constraints, or force flags.

Journal support includes external journal superblock lookup, user UUID table edits, internal journal inode removal, external journal removal, new internal/external journal creation, fast-commit sizing, and journal-user UUID updates when the filesystem UUID changes.

Checksum conversion support rewrites metadata after UUID or feature changes. The directory path adjusts htree limits and directory checksum tails. The inode path rewrites EA inodes first, then directories and other inodes, updating inline xattr hashes, xattr block hashes, extent checksums, directory checksums, inode checksums, group descriptor checksums, MMP checksums, and superblock checksum type/seed fields.

Inode-size expansion is a full metadata migration path: it reads bitmaps, identifies blocks that conflict with expanded inode tables, moves those blocks, fixes inode block references and group descriptor bitmap pointers, rewrites expanded inode tables, updates summary stats, and marks the filesystem invalid until the migration succeeds.

`main`/`tune2fs_main` orchestrates parsing, device resolution, optional ioctl label get/set on mounted Linux filesystems, libext2fs open with MMP handling, optional undo I/O setup, journal recovery, mount checks, requested superblock edits, feature/extended option application, quota updates, UUID replacement through mounted ioctl or direct superblock edit, inode resize, metadata checksum rewrite, superblock listing, and final close/writeout.

## Dependencies
Uses libext2fs extensively for filesystem open/close, bitmaps, inode scanning, block iteration, journal helpers, MMP, orphan files, checksums, group descriptors, directory blocks, xattrs, extents, and superblock fields. It also depends on e2p feature/mount-option parsing and listing, libuuid, blkid device lookup, quota support, com_err, plausible-device checks, devname resolution, undo I/O, and Linux ioctls for live label/UUID operations when available. Shared helper functions and globals are declared in `util.h`.

## Behavior/Risks
This file directly mutates on-disk metadata and has many operation-specific safety gates. Some changes intentionally leave the filesystem needing `e2fsck`, `e2fsck -D`, or `resize2fs`. Checksum and UUID changes can require whole-filesystem inode/directory/xattr rewrites, which are refused on mounted filesystems unless csum-seed semantics make them safe. Inode-size expansion relocates blocks and relies on undo I/O for recoverability; failures direct users to `e2undo`. Force flags can bypass selected safety checks, especially journal/MMP cases, so callers must preserve the command-line semantics carefully.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/tune2fs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/tune2fs.h -->
# File Research: sources/local-fs/e2fsprogs/misc/tune2fs.h

## Purpose
Small public header for embedding tune2fs behavior as a library entry point.

## Key Elements
Defines an include guard and C++ linkage wrapper. Declares `int tune2fs_main(int argc, char **argv);`, documented as taking the same arguments as the `tune2fs` executable and serving as the `libtune2fs` entry point.

## Dependencies
No external headers are included. Consumers are expected to provide normal C runtime argument arrays.

## Behavior/Risks
The header exposes the whole command-line tool as a callable API rather than a structured library interface, so callers inherit process-oriented behavior from `tune2fs.c`, including global option state, output to stdio/stderr, and exit-like error paths depending on build mode.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/tune2fs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/util.c -->
# File Research: sources/local-fs/e2fsprogs/misc/util.c

## Purpose
Provides helper routines shared by `tune2fs` and `mke2fs` for program-name extraction, user confirmation, mount safety checks, journal option parsing/sizing, fsck reminder output, and MMP diagnostic printing.

## Key Elements
`get_progname` strips directory prefixes from `argv[0]`. `proceed_question` prompts for confirmation, optionally auto-proceeding after a timeout via `alarm`, `setjmp`, and `longjmp`. `check_mount` rejects mounted or busy target devices unless sufficiently forced.

`parse_journal_opts` parses comma-separated `-J` options for external journal device, journal size, fast-commit size, journal location, and v1 journal superblock mode, storing results in the global variables declared by `util.h`. Invalid options print usage guidance and terminate.

`figure_journal_size` obtains default journal parameters from libext2fs and applies requested journal/fast-commit sizes, enforcing JBD2 minimum/maximum total blocks and ensuring the journal does not consume more than half the free filesystem blocks. `print_check_message` summarizes automatic fsck mount/time policy. `dump_mmp_msg` prints MMP failure details from an MMP block.

## Dependencies
Depends on libext2fs, JBD kernel structures, e2p, blkid/devname support, com_err, NLS wrappers, POSIX file/signal/time APIs, and `util.h`. Provides a fallback `strcasecmp` when the platform lacks one.

## Behavior/Risks
Several helpers terminate the process on invalid input or unsafe mount state, matching command-line utility expectations. `proceed_question` uses process-global signal/alarm state. Journal option parsing mutates shared global state used later by `tune2fs` and `mke2fs`, so ordering and single-process reuse matter.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/util.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/util.h -->
# File Research: sources/local-fs/e2fsprogs/misc/util.h

## Purpose
Declares shared tune2fs/mke2fs helper globals and function prototypes implemented in `util.c`.

## Key Elements
Exports journal configuration globals: `journal_size`, `journal_fc_size`, `journal_flags`, `journal_device`, and `journal_location_string`. Declares optional fallback `strcasecmp`, program-name extraction, confirmation prompt, journal option parsing, mount checking, journal sizing, check-policy printing, and MMP message dumping.

## Dependencies
The prototypes reference `struct ext2fs_journal_params`, `ext2_filsys`, and `struct mmp_struct`, so including files must already have suitable ext2fs declarations in scope or include this after ext2fs headers.

## Behavior/Risks
The header has no include guard. It exposes mutable global journal state, which keeps the command-line utility code simple but makes reentrant or repeated library-style use more fragile.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/util.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/uuidd.8.in -->
# File Research: sources/local-fs/e2fsprogs/misc/uuidd.8.in

## Purpose
Nroff manpage template for `uuidd`, the libuuid UUID generation daemon.

## Key Elements
Documents daemon mode with optional debug, pidfile, socket path, and idle timeout; client test mode for random or time UUID requests with optional bulk count; and kill mode. Explains that the daemon helps generate UUIDs, especially time-based UUIDs, securely and uniquely under high concurrency.

## Dependencies
Uses e2fsprogs substitution tokens for version/date. References libuuid, `uuidgen(1)`, the default pidfile `/var/lib/libuuid/uuidd.pid`, and the default request socket `/var/lib/libuuid/request`.

## Behavior/Risks
Documentation-only. It notes that the socket path is primarily for debugging because libuuid hard-codes the default path.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/uuidd.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/uuidd.c -->
# File Research: sources/local-fs/e2fsprogs/misc/uuidd.c

## Purpose
Implements `uuidd`, a Unix-domain socket daemon and command-line client for generating libuuid random, time-based, and bulk UUID responses.

## Key Elements
Command-line parsing supports daemon/debug mode, kill mode, random/time test requests, bulk count, custom pidfile/socket path, quiet mode, and idle timeout. Non-root invocations that use client/debug/custom-path operations drop effective IDs back to the real user/group.

Client requests use `call_daemon`, which connects to the configured Unix socket, sends a one-byte operation plus optional count, reads a 32-bit reply length, validates it against the caller buffer, and returns UUID bytes, counts, pid text, or max-operation text depending on operation.

`server_loop` owns daemon startup. It creates and locks the pidfile, probes for an existing daemon, binds/listens on the Unix socket, optionally daemonizes, installs cleanup signal handlers, writes its pid, accepts client connections, decodes operations, and dispatches to libuuid internal generators. Bulk time requests return one UUID plus a count of subsequent UUIDs; bulk random requests cap count to 1000 and fit the fixed reply buffer.

`create_daemon` forks, exits the parent, redirects stdio to `/dev/null`, changes to `/`, creates a new session, and sets real/effective uid to the effective uid. `read_all` and `write_all` provide retrying I/O loops for EINTR/EAGAIN-style partial transfers. Signal cleanup unlinks pidfile and socket.

## Dependencies
Uses libuuid public and internal APIs (`uuid__generate_time`, `uuid__generate_random`), `uuid/uuidd.h` operation constants and default paths, Unix sockets, file locks, pid files, signals, privilege APIs, NLS setup, and ext2fs headers for portability attributes.

## Behavior/Risks
The protocol is intentionally small but binary and host-endian for counts/reply lengths. Socket `bind` uses the caller-provided path copied into `sun_path` and unlinks any existing path first. The daemon uses a fixed 1024-byte reply buffer and caps bulk random replies accordingly. Cleanup relies on signal paths; abnormal termination can leave stale socket/pidfile entries, though startup probes and pidfile locking reduce duplicate-daemon risk.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/uuidd.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/uuidgen.1.in -->
# File Research: sources/local-fs/e2fsprogs/misc/uuidgen.1.in

## Purpose
Nroff manpage template for `uuidgen`, the command-line UUID generator.

## Key Elements
Documents `uuidgen [-r|-t]`, explaining default UUID generation through libuuid, random-based UUIDs when high-quality randomness is available, fallback to time-based UUIDs otherwise, and explicit forcing of random or time methods.

## Dependencies
Uses e2fsprogs substitution tokens for version/date. References `libuuid(3)`, OSF DCE 1.1 conformance, and e2fsprogs packaging.

## Behavior/Risks
Documentation-only. It communicates the security/uniqueness distinction between random UUIDs and time-based UUIDs, including the dependency on a high-quality random number generator such as `/dev/random`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/uuidgen.1.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/uuidgen.c -->
# File Research: sources/local-fs/e2fsprogs/misc/uuidgen.c

## Purpose
Implements the simple `uuidgen` command-line utility that prints one DCE-compatible UUID.

## Key Elements
Parses `-t` and `-r` with `getopt`, selecting time-based generation, random generation, or the libuuid default generator. Initializes NLS when enabled, calls the selected libuuid generator into a `uuid_t`, unparses it into the canonical string buffer, prints it with a trailing newline, and returns success.

## Dependencies
Uses libuuid public APIs `uuid_generate`, `uuid_generate_time`, `uuid_generate_random`, and `uuid_unparse`, plus standard stdio/getopt and e2fsprogs NLS support.

## Behavior/Risks
If both `-t` and `-r` are supplied, the last parsed option wins because `do_type` is overwritten. Invalid options print usage and exit. Output buffer is sized to 37 bytes, matching canonical UUID text plus NUL.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/uuidgen.c -->