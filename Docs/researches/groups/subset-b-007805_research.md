# subset-b-007805 Research

This grouped report covers the 34 mapped source files for `subset-b-007805`. Each file section is bounded by the required reconciliation markers and uses the original source path as its section title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write-closed2.c -->
# sources/distributed-fs/openafs/src/tests/write-closed2.c

Purpose: exercises AFS cache-manager writeback behavior when a file is mmaped, its containing directory ACL is changed to remove access, the descriptor is closed, and the mapped page is modified before `munmap`. It is a regression-style client test for permissions, mmap dirtying, and close/write ordering.

Important APIs and functions: `set_acl` builds a `ViceIoctl` payload for `VIOCSETAL` and calls `pioctl` with follow-symlinks disabled. `doit` creates and enters `bad`, opens/truncates a target file, maps one byte with `MAP_SHARED`, drops directory ACLs to `system:anyuser 0`, closes the fd, writes `0x17` through the mapping, then unmaps. `main` only parses an optional filename.

Control flow/state: the persistent state is the newly created directory and file in the current working directory. The key state transition is fd-open to mmap to ACL-restricted directory to fd-close to mmap write. Dependencies are AFS-specific `pioctl`, `afs/venus.h`, and POSIX mmap/open/truncate calls. Risks include destructive relative paths (`bad`), assuming the current directory is an AFS volume where `VIOCSETAL` works, and only checking syscall failures, not post-write file contents. Test signal is process exit: success means all operations including delayed writeback through `munmap` completed without local errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write-closed2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write-large.c -->
# sources/distributed-fs/openafs/src/tests/write-large.c

Purpose: validates writing an AFS file up to the 2 GiB minus 1 byte boundary. It is aimed at large-file handling and cache/file-server write path limits.

Important APIs and functions: `check_size` optionally `stat`s the fixed file `foobar` and compares `st_size`. `main` opens `foobar` with `O_LARGEFILE` when available, writes 2,097,151 chunks of 1024 bytes, then expects the next 1024-byte write to return exactly 1023 bytes, producing size `2147483647`.

Control flow/state: a single file named `foobar` is created/truncated in the working directory and left behind. The loop makes the file nearly 2 GiB, then intentionally tests the boundary short-write. Dependencies are POSIX `open`, `write`, `close`, `stat`, large-file macros, and BSD `err` APIs.

Risks: this test consumes about 2 GiB of quota and time, uses an uninitialized stack buffer for content, and assumes the expected AFS/file-size limit is exactly `INT32_MAX`; on modern large-file-capable storage a full final 1024-byte write would make the test fail. Test signal is strict exit status plus final size verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write-large.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write-rand.c -->
# sources/distributed-fs/openafs/src/tests/write-rand.c

Purpose: creates or overwrites a file with pseudo-random bytes of a requested size. It is a simple workload generator for write tests rather than a verifier.

Important APIs and functions: `write_random_file` allocates up to a 2048-byte buffer, fills it with `rand()` bytes, and repeatedly writes chunks until the requested `size_t` length reaches zero. `main` parses `file size`, seeds with `time(NULL)`, opens the file `O_RDWR | O_CREAT` mode `0755`, seeks to offset zero, writes, and closes.

Control flow/state: state is only the target file contents. The file is not truncated, so if the new requested size is smaller than the old file size, stale trailing data may remain. Dependencies are POSIX file APIs and libc random/time functions.

Risks: `atoi` silently accepts bad or negative sizes before conversion to `size_t`; `write_random_file` returns `char *` but returns `0`; partial writes are treated as errors instead of retrying. Test signal is weak: success means writes returned the requested chunk lengths, not that the resulting file size or data was verified.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write-rand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write-ro -->
# sources/distributed-fs/openafs/src/tests/write-ro

Purpose: shell regression check that writes to a replicated read-only volume fail. It attempts to create `../../replicated/foo`.

Important APIs and control flow: the script runs `touch ../../replicated/foo || exit 0` and then `exit 1`. Success is inverted: if `touch` fails, the script exits zero; if `touch` succeeds, it exits one.

State and persistence: on a broken environment where the write succeeds, it leaves `foo` in the replicated tree before failing. There is no cleanup because the success case is considered a failure. Dependencies are `/bin/sh`, `touch`, and the test harness layout where `../../replicated` points at a read-only AFS replicated volume.

Risks/test signals: the test only distinguishes touch success from failure and does not inspect errno, ACLs, or volume type. If the path is missing for reasons unrelated to read-only enforcement, the script still passes. Its signal is therefore suitable only in a carefully prepared AFS test cell.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write-ro -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write-ro-file.c -->
# sources/distributed-fs/openafs/src/tests/write-ro-file.c

Purpose: verifies that a basic create/write/close/unlink sequence can complete in the current directory. Despite the name, it is a writable-file smoke test likely paired with read-only volume checks elsewhere.

Important APIs and functions: `main` opens `foo` with `O_RDWR | O_CREAT` and mode `0`, writes three bytes `"foo"`, closes the descriptor, then unlinks the file. On write or close failure it attempts to unlink before reporting via `err`.

Control flow/state: the only persistent artifact is `foo`, removed on normal and most error paths. Dependencies are POSIX `open`, `write`, `close`, `unlink`, and `err`.

Risks: using create mode `0` means permissions are no-access after creation, though the already-open descriptor remains writable. The code treats short positive writes as success because it only checks `< 0`, so a partial write would pass. Test signal is exit code and absence of syscall errors, not content verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write-ro-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write-ucc.c -->
# sources/distributed-fs/openafs/src/tests/write-ucc.c

Purpose: stresses updates to file contents plus metadata changes before close. The name suggests write/update/chmod/chown or cache consistency coverage.

Important APIs and functions: `doit` opens a target file for write/create/truncate, writes `"hej\n"`, sets access and modification times with `utimes`, changes mode to `0644`, attempts `chown(filename, 0, 0)` without enforcing success, checks size with `fstat` while the fd is open, closes, then checks size again with `stat`. `main` accepts an optional filename defaulting to `blaha`.

State and integration: the file remains after the test with size four and mode `0644` if `chmod` succeeds. It depends on POSIX metadata syscalls and is relevant to AFS client store-status/writeback sequencing.

Risks/test signals: ignoring `chown` errors is intentional for non-root test runs but means ownership semantics are not verified. It catches short writes and size mismatches before and after close, which are good signals for delayed AFS writeback/cache consistency issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write-ucc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write1 -->
# sources/distributed-fs/openafs/src/tests/write1

Purpose: minimal shell smoke test for create, write, read-back, and remove in the current test directory.

Important behavior: it writes `hej` to `foo` with shell redirection, compares command-substituted `cat foo` output against `hej`, and removes `foo`. Each step exits one on failure.

State/dependencies: state is a temporary relative file `foo`, normally removed. It depends on `/bin/sh`, `echo`, `cat`, `test`, and `rm`, plus normal AFS client read-after-write behavior.

Risks/test signals: command substitution strips trailing newlines, so the comparison checks logical text rather than byte-for-byte file content. The test is intentionally small and only signals gross write/read/remove failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write1 -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write2 -->
# sources/distributed-fs/openafs/src/tests/write2

Purpose: shell smoke test for overwriting an existing file and seeing the new contents through a subsequent read.

Important behavior: it writes `hopp` to `foo`, verifies the read-back, overwrites `foo` with `hej`, verifies again, then removes the file.

State/dependencies: state is only the relative file `foo`. Dependencies are standard shell utilities and the current directory's filesystem semantics. Integration point is the AFS client cache path for truncate-on-redirection followed by read-after-write.

Risks/test signals: like `write1`, it normalizes away the newline via command substitution and does not test binary content, append behavior, or concurrent readers. It is a concise signal for overwrite/truncate propagation in the test volume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write2 -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write3.c -->
# sources/distributed-fs/openafs/src/tests/write3.c

Purpose: tests ordinary small-file write, truncate, read, close, and unlink behavior, including in-fd size observation before close.

Important APIs and functions: `check_size` verifies `stat` size unless the `paranoia` flag is set. `check_size_read` saves current offset, seeks to start, allocates a buffer of expected size, reads exactly that many bytes, then seeks to end and expects the offset to equal the expected size. `main` writes `"kaka"` to `foobar`, verifies after close, reopens with `O_TRUNC`, writes again, verifies via read and seek, closes, then unlinks.

State: creates `foobar` in the current directory and removes it at the end. Dependencies are POSIX file APIs and `err`.

Risks/test signals: it incorrectly declares `read`/`lseek` results as `size_t`, so negative errors are poorly represented, and the second `open` uses decimal `644` instead of octal `0644`. Still, it provides useful read-after-write and file-length signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/write3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/Makefile.in -->
# sources/distributed-fs/openafs/src/tools/Makefile.in

Purpose: top-level make dispatcher for the OpenAFS `src/tools` subtree.

Important targets and control flow: defines `SUBDIRS=dumpscan rxperf`. For `all`, `dest`, `install`, `clean`, and `distclean`, it loops over each subdirectory, runs `$(MAKE) $@`, and exits immediately if a child make fails.

State and dependencies: it does not build artifacts directly; persistence is delegated to child makefiles. It depends on make variables expanded by configure, a shell, and child directories with compatible targets.

Integration points: this file connects the main OpenAFS build to `dumpscan` and `rxperf`. A failure in `dumpscan/Makefile.in` or `rxperf` propagates through the `|| exit 1` guard.

Risks/test signals: the `cd $$A && $(MAKE) ... && cd ..` pattern assumes all subdirectory names are simple and that returning to `..` is sufficient. Build signal is coarse: success means all child targets returned zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/audit/readsysvmq -->
# sources/distributed-fs/openafs/src/tools/audit/readsysvmq

Purpose: example Perl consumer for OpenAFS fileserver audit logs emitted through the System V message queue audit interface.

Important APIs and control flow: the script requires one argument, the audit log path. It uses `IPC::SysV` `ftok($path, 1)` to derive the queue key, opens the message queue with `msgget($mqkey, S_IRUSR)`, then loops forever calling `msgrcv`. Each received message is unpacked as native long message type plus the remaining text via `unpack("l! a*", $msg)` and printed.

State/dependencies: no persistent state is written. It depends on Perl, `IPC::SysV`, SysV IPC support, and a fileserver started with `-audit-interface sysvmq` plus matching `-auditlog` path.

Risks/test signals: it blocks indefinitely, has no signal handling or queue cleanup, assumes a 2048-byte message payload, and prints raw audit text. Its operational signal is visible audit lines or immediate failure if the path/key/queue is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/audit/readsysvmq -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/Makefile.in -->
# sources/distributed-fs/openafs/src/tools/dumpscan/Makefile.in

Purpose: builds the dumpscan tools and support libraries for parsing, inspecting, extracting, and repairing AFS volume dumps.

Important targets: `libdumpscan.a` is built from parser, dump writer, directory, pathname, backup header, and stage header objects. `libxfiles.a` is built from stream abstraction objects in the adjacent files. User tools include `afsdump_scan`, `afsdump_dirlist`, `afsdump_extract`, and `dumptool`; `afsdump_xsed` has a target but is not in the default `all` target. Error-table sources/headers are generated from `.et` files via `COMPILE_ET`.

Dependencies/integration: includes OpenAFS build config and LWP make fragments, links against auth, audit, volser, vldb, ubik, rxkad, rx, hcrypto, lwp, util, opr, com_err, roken, and platform libraries. `MODULE_CFLAGS=-DNATIVE_UINT64=afs_uint64` chooses the native `dt_uint64` implementation.

Risks/test signals: object dependency rules ensure generated error headers exist, while `repair.o` disables strict aliasing. The makefile's main test signal is successful compile/link; no runtime dump fixtures are exercised here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/afsdump_dirlist.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/afsdump_dirlist.c

Purpose: command-line utility that lists entries from an AFS directory data file, not a full volume dump.

Important APIs/functions: `parse_options` handles `-h`, `-q`, and `-v`, defaulting input to `-` for stdin. `my_error_cb` counts parse errors and emits com_err messages unless quiet. `main` initializes relevant OpenAFS error tables, opens the input as an `XFILE`, sets `dp.print_flags = DSPRINT_DIR`, marks `DSFLAG_SEEK` when possible, and calls `ParseDirectory(&input_file, &dp, 0, 1)` where `toeof=1` means parse directory pages until EOF.

State/dependencies: no persistent output; it reads only. It depends on `libdumpscan`, `libxfiles`, OpenAFS error tables, and directory format definitions from `directory.c`/`dumpfmt.h`.

Risks/test signals: the process exits zero even if `ParseDirectory` returns an error after printing `*** FAILED`, so callers must inspect output/stderr rather than only exit status. Directory corruption is reported through callbacks, but quiet mode suppresses details.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/afsdump_dirlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/afsdump_extract.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/afsdump_extract.c

Purpose: extracts files, directories, and symlinks from an AFS volume dump into a destination directory, optionally selecting by vnode number or volume-relative path.

Important APIs/functions: `parse_options` handles `-A`, `-H`, `-i`, `-n`, `-p`, `-q`, and `-v`; it separates requested path names from vnode numbers. `Path_PreScan` builds a vnode/path hash before extraction unless vnode-number mode is used. `directory_cb`, `file_cb`, and `symlink_cb` are registered as `dump_parser` callbacks. `file_cb` seeks to `v->d_offset`, opens the target path, and copies `v->size` bytes with `copyfile`. `symlink_cb` reads link data and calls `symlink`.

State/persistence: it may create the destination directory, `chdir` into it, create nested directories and files, and create symlinks. `-n` suppresses writes. Dependencies are seekable `XFILE` input for path mode, `pathname.c`, `directory.c`, parser callbacks, and POSIX filesystem APIs.

Risks/test signals: selected path matching is prefix-based for directories; file modes and ACL saving are incomplete (`do_acls` is a placeholder, output files use `0644`). Exit status is always zero after parse, even on parse errors. There are also concrete option/allocation risks: when no destination argument is provided, `target` is first set to `"."` and then overwritten with `argv[optind + 1]`; the selection arrays use `malloc(name_count + sizeof(char *))` and `malloc(vnum_count + sizeof(afs_uint32))` instead of element count times element size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/afsdump_extract.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/afsdump_scan.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/afsdump_scan.c

Purpose: general-purpose scanner for full AFS volume dumps. It can print dump headers, volume headers, vnode records, ACLs, directories, paths, debug details, and optionally generate a repaired dump.

Important APIs/functions: `parse_printflags` maps `-P` letters to `DSPRINT_*`; `parse_repairflags` maps `-R` letters to `DSFIX_*`. `setup_repair` opens `repair_output` and wires repair callbacks from `repair.c`. `print_vnode_path` calls `Path_Build` during vnode callbacks. `main` opens input with `xfopen`, enforces seekability for repair and path printing, optionally pre-scans paths with `Path_PreScan`, then calls `ParseDumpFile`.

State/persistence: normal mode reads only and prints to stdout/stderr. Repair mode writes a new dump to `-g` and appends `DumpDumpEnd` after successful parsing. Dependencies include parser library, path hash logic, repair callbacks, xfiles streams, and OpenAFS error tables.

Risks/test signals: return status is always zero at the final `exit(0)`, so automation must parse diagnostics. Path printing requires a seekable dump because it pre-scans and then rewinds. Repair output quality depends on parser recovery flags and generated defaults from `repair.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/afsdump_scan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/afsdump_xsed.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/afsdump_xsed.c

Purpose: older or alternate dump scanner/rewriter based on the UB/MR-AFS code path. It resembles `afsdump_scan` but adds `-A nnn` to grant all directory ACL rights to a specified ID while generating a repaired dump.

Important APIs/functions: it contains local `parse_printflags`, `parse_repairflags`, `parse_options`, `print_vnode_path`, `munge_admin_acl`, and `setup_repair`. `munge_admin_acl` edits the on-dump ACL buffer in a directory vnode, inserting the ID into positive rights or removing it from negative rights, then delegates to `repair_vnode_cb`.

State/dependencies: in repair mode it writes `repair_output`; with `-A` it mutates directory ACLs in the generated dump. It depends on `dumpscan.h`, repair callbacks, OpenAFS ACL rights constants, and seekable `XFILE` input for path or repair modes.

Risks/test signals: this file appears less maintained than `afsdump_scan.c`: option string omits `q` although the switch handles it, `my_error_cb` lacks an explicit return, `setup_repair` and `xfopen` calls use older argument conventions, and the known-type test uses `||` where `&&` was likely intended. It should be treated cautiously unless its target is still built in a matching legacy environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/afsdump_xsed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/backuphdr.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/backuphdr.c

Purpose: generic backup-system header adapter for dumpscan, currently recognizing old Stage backup headers and exposing them as `backup_system_header`.

Important APIs/functions: `try_backuphdr` is registered as a special top-level parser for `STAGE_VERSMIN`. It calls `ParseStageHdr`, optionally prints via `PrintBackupHdr`, invokes `cb_bckhdr`, seeks back after callbacks when `DSFLAG_SEEK` is set, and frees allocated strings. `PrintBackupHdr` formats version, volume, location, dump range, dump time, flags, length, and tape file number.

State/dependencies: no persistent state; it allocates transient strings inside `backup_system_header` via `stagehdr.c`. It depends on `dumpscan.h`, `dumpscan_errs.h`, `stagehdr.h`, time formatting, and parser callback conventions.

Risks/test signals: only Stage headers are recognized; unknown backup headers return `DSERR_MAGIC`. Callback consumers must copy header data if needed because storage is freed before return. The printed length path differs for native and struct-based `dt_uint64`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/backuphdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/directory.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/directory.c

Purpose: parses, searches, and generates AFS directory data in on-disk/dump page format.

Important APIs/functions: `parse_directory` reads 2 KiB pages, checks the `AFS_DIR_MAGIC` tag, walks allocated directory entries, prints when `DSPRINT_DIR` is set, and invokes `cb_dirent`. `ParseDirectory` is the public wrapper. `DirectoryLookup` installs a temporary `cb_dirent` to search by name or vnode. Generation functions `Dir_Init`, `Dir_AddEntry`, `Dir_Finalize`, `Dir_EmitData`, and `Dir_Free` build directory pages with hash chains and allocation bitmaps.

State/persistence: parser state is transient except callback side effects. Generator state lives in `struct dir_state` until emitted to an `XFILE`, optionally with a `VTAG_DATA` tag. Dependencies include `afs/dir.h`, `dumpfmt.h`, byte-order conversion, `XFILE`, and parser error callbacks.

Risks/test signals: the parser trusts many on-disk sizes and name layouts after basic checks; corrupted allocation bitmaps can skip entries or abort pages. Generation has a 128-page old-style allocation map assumption. Test signals are directory listings, lookup success, and downstream path building/extraction behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/directory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/dump.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/dump.c

Purpose: serializes dumpscan in-memory records back into AFS dump format.

Important APIs/functions: `DumpDumpHeader`, `DumpVolumeHeader`, and `DumpVNode` emit top-level and attribute tags according to field masks. `DumpVNodeData` writes a `VTAG_DATA` size and caller-provided buffer. `CopyVNodeData` writes a data tag and streams bytes from one `XFILE` to another in 64 KiB chunks. `DumpDumpEnd` writes the dump trailer magic.

State/dependencies: no global state; persistence is whatever is written to the output `XFILE`. It depends on tag constants from `dumpfmt.h`, field masks/types from `dumpscan.h`, network byte-order helper writers from `primitive.c`, and input seeking by callers when copying vnode data.

Risks/test signals: serialization only writes fields whose masks are set, so caller repair/defaulting is responsible for completeness. The `VHTAG_OFFLINE` and `VHTAG_MOTD` paths use `WriteTagInt32` with the first string byte, which looks inconsistent with string parsing and is a risk for repaired dump fidelity. Test signal is successful reparse/restore of generated dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/dump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/dumpfmt.h -->
# sources/distributed-fs/openafs/src/tools/dumpscan/dumpfmt.h

Purpose: central description of AFS volume dump wire-format constants and embedded AFS directory page layouts.

Important definitions: dump version and begin/end magic values; top-level tags for dump header, volume header, vnode, and dump end; attribute tags for dump headers, volume headers, and vnodes; directory constants `AFS_DIR_MAGIC`, entries per page, max pages, and hash bucket count. It defines packed-format structs `afs_dir_pagehdr`, `afs_dir_header`, `afs_dir_direntry`, and union `afs_dir_page`.

State/dependencies: this header defines format, not behavior. It depends on `intNN.h` for sized AFS integer aliases.

Integration points: all parser/writer files use these tag constants to keep read/write symmetry. `directory.c` and `repair.c` use the directory page structures when interpreting or generating directory data.

Risks/test signals: these structs assume the OpenAFS dump/on-disk directory layout and alignment remain compatible with the C representation. Any tag mismatch causes parser desynchronization, so round-trip tests through `ParseDumpFile` and `Dump*` are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/dumpfmt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/dumpscan.h -->
# sources/distributed-fs/openafs/src/tools/dumpscan/dumpscan.h

Purpose: public API for the dumpscan library, including data models, parser callbacks, flags, path hash types, and exported functions.

Important types: `backup_system_header`, `afs_dump_header`, `afs_vol_header`, `afs_vnode`, and `afs_dir_entry` carry parsed dump data with field masks. `tagged_field` and `tag_parse_info` drive generic tag parsing and recovery flags. `dump_parser` is the primary integration contract, containing callbacks for backup headers, dump/volume headers, vnode categories, data, errors, directory entries, plus `DSFLAG_SEEK`, `DSPRINT_*`, and `DSFIX_*` flags. `path_hashinfo` and `vhash_ent` support path construction/following.

Integration points: command-line tools configure `dump_parser` and call `ParseDumpFile`; repair and extraction callbacks use offsets and field masks; writers use the same model for output.

Risks/test signals: callbacks receive stack-owned records and must copy data they retain. Many operations require seekable `XFILE`s but this is represented by a flag rather than enforced by the type system. Test signals include compile-time API consistency and successful parse/path/extract/repair workflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/dumpscan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/dumptool.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/dumptool.c

Purpose: standalone interactive tool for inspecting and restoring MR-AFS/OpenAFS dump files. It predates or sits beside the callback-based dumpscan library and contains its own dump parser, directory walker, and optional MR-AFS residency helpers.

Important APIs/functions: `main` opens a dump, reads the dump header and volume header, scans vnodes twice, validates the dump trailer, then either lists all FIDs (`-i`), performs MR-AFS residency operations, or starts `InteractiveRestore`. `ReadDumpHeader`, `ReadVolumeHeader`, and `ScanVnodes` parse tagged records into `VolumeDiskData` and `VnodeDiskObject`. `InsertVnode`/`GetVnode` maintain large-directory and small-file vnode indexes. Interactive commands route to `DirectoryList`, `ChangeDirectory`, `CopyFile`, `CopyVnode`, and optional `DumpAllFiles`.

State/persistence: builds in-memory indexes and caches directory vnode data; copy commands write files from dump data to the host filesystem. It uses global arrays, counters, terminal width, and MR-AFS option state. Dependencies include OpenAFS volume/vnode/dir headers, large-file stdio, optional residency server APIs, and POSIX terminal/file calls.

Risks/test signals: the code has legacy assumptions, globals, limited bounds checks, and conditional MR-AFS code. It handles corrupt or incomplete dumps with `-f` only for trailer absence. Strong signals are interactive restore success and correct FID/path listing from real dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/dumptool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/int64.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/int64.c

Purpose: formatting, shifting, and optional self-tests for `dt_uint64`, supporting both native 64-bit and emulated `{hi,lo}` implementations from `intNN.h`.

Important APIs/functions: `hexify_int64` returns a fixed-width 16-hex-digit string. `decimate_int64` formats decimal; the non-native path uses a precomputed table of decimal powers of two and digit accumulation. `shift_int64` shifts left or right across the high/low boundary. Under `TEST_INT64`, `verify_int64_size`, constructor/comparison tests, and a test `main` are compiled.

State/dependencies: uses static buffers when callers pass `NULL`, so results are overwritten by later calls. Non-native decimal formatting mutates `bitvals` from ASCII digits to numeric digits in `prep_table`. Dependencies are `intNN.h` macros and stdio/string.

Risks/test signals: static return buffers are not thread-safe and nested calls need caller-provided buffers. Shift expressions around 32-bit boundaries are delicate. The optional test block provides constructor and comparison coverage but says arithmetic tests are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/int64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/intNN.h -->
# sources/distributed-fs/openafs/src/tools/dumpscan/intNN.h

Purpose: abstracts fixed-width integer support for dumpscan, especially unsigned 64-bit dump offsets.

Important definitions: when `NATIVE_UINT64` is defined, `dt_uint64` aliases that native type and macros implement construction, extraction, comparison, arithmetic, and network byte-order conversion directly. Otherwise `dt_uint64` is a struct of `afs_uint32 hi, lo` with equivalent macro operations. It declares `hexify_int64`, `decimate_int64`, and `shift_int64`.

State/dependencies: header-only macro logic depends on `afs/stds.h` and byte-order macros such as `htonl`/`ntohl` available in including sources. The build makefile defines `NATIVE_UINT64=afs_uint64`, so modern OpenAFS builds take the native branch.

Risks/test signals: macro arguments may be evaluated more than once in some operations and have type assumptions. The non-native `get64` loses high bits by returning only `.lo`, so callers must not use it for full-width values. Test signals come from `int64.c` with `TEST_INT64` and from large/seekable dump parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/intNN.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/internal.h -->
# sources/distributed-fs/openafs/src/tools/dumpscan/internal.h

Purpose: private cross-module declarations for dumpscan implementation files.

Important APIs: declares internal parser entry points `parse_volhdr` and `parse_vnode`, directory helper `parse_directory`, backup-header adapter `try_backuphdr`, and utilities `handle_return`, `prep_pi`, and `match_next_vnode`.

State/dependencies: no state. It includes `xfiles.h` and `dumpscan.h`, tying all private declarations to the public parser data model.

Integration points: `parsedump.c` uses `parse_volhdr`, `parse_vnode`, and `try_backuphdr` in its top-level tag table. `parsevnode.c` uses `parse_directory` and `match_next_vnode` for directory callbacks and repair resync. Command-line tools do not include this header directly; it is for library internals.

Risks/test signals: this header exposes non-public symbols without include guards of its own, relying on included headers and compile discipline. Prototype drift would break parser builds. Compile/link of `libdumpscan.a` is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/parsedump.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/parsedump.c

Purpose: top-level parser for AFS volume dump streams and public wrappers for parsing a full dump, just a dump header, just a volume header, or one vnode.

Important APIs/functions: `top_fields` maps top-level tags to `parse_dumphdr`, `parse_volhdr`, `parse_vnode`, `parse_dumpend`, and `try_backuphdr`. `parse_dumphdr` validates begin magic/version, parses attributes with `dumphdr_fields`, invokes `cb_dumphdr`, and frees kept strings. `parse_dumptimes` reads the two-entry from/to array. `parse_dumpend` validates trailer magic and returns `DSERR_DONE`. Public `ParseDumpFile`, `ParseDumpHeader`, `ParseVolumeHeader`, and `ParseVNode` set up `tag_parse_info` via `prep_pi` and normalize returns through `handle_return`.

State/dependencies: parser state is callback-driven and transient; `dump_parser` may record `vol_uniquifier` later via volume parsing. Dependencies are `dumpfmt.h`, `internal.h`, `stagehdr.h`, and primitive/tag parsing.

Risks/test signals: unknown tags stop current object parsing by returning zero for higher-level handling, so stream position discipline is critical. Magic/version checks are strong early corruption signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/parsedump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/parsetag.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/parsetag.c

Purpose: generic tagged-data parser used by dump, volume, and vnode parsing.

Important API: `ParseTaggedData(XFILE *, tagged_field *, unsigned char *tag, tag_parse_info *, void *g_refcon, void *l_refcon)` loops reading one-byte tags, finds them in a field table, reads values according to `DKIND_*`, and invokes optional per-field parser callbacks. `DKIND_SPECIAL` callbacks own stream consumption and return with the next tag in `*tag`.

State/control flow: `tag_parse_info` carries error callback references and recovery state. `TPFLAG_SKIP` skips null tags forward; `TPFLAG_RSKIP` can seek backward after skipped bytes to account for inserted data. String values are freed unless the callback returns `DSERR_KEEP`.

Dependencies/integration: relies on primitive readers and `XFILE` seeking for recovery. All higher-level parsers are table-driven on top of this function.

Risks/test signals: special callbacks must obey the stream contract or the parser desynchronizes. The null-tag recovery is heuristic and should be validated on corrupt dump fixtures. Memory ownership for strings is subtle but explicit through `DSERR_KEEP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/parsetag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/parsevnode.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/parsevnode.c

Purpose: parses individual vnode records, including metadata, ACLs, file/directory/symlink data, and optional corruption resynchronization.

Important APIs/functions: `parse_vnode` reads vnode number/uniquifier, records offsets, parses tagged attributes with `vnode_fields`, optionally resyncs with `resync_vnode`, then dispatches to vnode-type callbacks. `store_vnode` fills `afs_vnode` fields and masks. `parse_acl` copies the raw ACL block and can print positive/negative rights via `rights2str`. `parse_vdata` reads data size/offset, handles symlink target buffering, parses directory contents when needed, or skips data.

State/dependencies: uses static `LastGoodVNode` for resync and static symlink buffer reuse. It depends on `dumpfmt.h`, `internal.h`, `afs/acl.h`, `afs/prs_fs.h`, directory parsing, and `match_next_vnode`.

Risks/test signals: static state is not reentrant. Resync heuristics can drop vnodes or seek around corrupt regions, so repaired parses need validation. Callback behavior depends on `DSFLAG_SEEK`; without seeking, callbacks that inspect data can consume the stream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/parsevnode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/parsevol.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/parsevol.c

Purpose: parses AFS volume header records from tagged dump data into `afs_vol_header`.

Important APIs/functions: `parse_volhdr` initializes the header, records offset, calls `ParseTaggedData` with `volhdr_fields`, invokes `cb_volhdr`, stores `voluniq` into `dump_parser.vol_uniquifier`, and frees kept strings. `store_volhdr` handles scalar, flag, time, and string fields while setting field masks. `parse_weekuse` reads and validates a seven-element usage array.

State/dependencies: persistent parser side effect is `p->vol_uniquifier`. The header and strings are transient; callbacks must copy what they keep. Dependencies are `dumpfmt.h`, `dumpscan_errs.h`, primitive readers, and time formatting.

Risks/test signals: weekuse count mismatch is fatal format error. String ownership depends on `DSERR_KEEP`, and volume header completeness is not enforced here; repair callbacks fill missing fields later. Printing uses raw integer/time formatting and is mostly diagnostic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/parsevol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/pathname.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/pathname.c

Purpose: builds a vnode hash table from a dump and uses it to resolve volume-relative paths or construct paths for vnodes.

Important APIs/functions: `Path_PreScan` runs a secondary `dump_parser` over the dump, collecting volume file count, vnode offsets, parent links, directory data offsets/sizes, and directory-entry parent relationships. `Path_Follow` tokenizes a path, repeatedly seeks to parent directory data, and calls `DirectoryLookup` by name. `Path_Build` walks parent links from a vnode to root, either using fast numeric components or reverse directory lookups for real names. `Path_FreeHashTable` releases entries.

State/dependencies: persistent state is `path_hashinfo.hash_table`, sized from volume file count. It depends on seekable `XFILE`s, `DirectoryLookup`, parser callbacks, and accurate directory vnode data.

Risks/test signals: `Path_Follow` mutates its input string with `strtok` and appears to call `strtok(path, "/")` twice, skipping the first component. Missing parents or incomplete directory data are fatal. Strong signals are successful `afsdump_scan -Pp` and path-based extraction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/pathname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/primitive.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/primitive.c

Purpose: low-level big-endian primitive readers/writers for the `XFILE` abstraction.

Important APIs/functions: `ReadByte`, `ReadInt16`, `ReadInt32`, and `ReadString` read raw dump values and convert network order to host order. `ReadString` reads byte-by-byte in 256-byte chunks, growing a NUL-terminated buffer. `WriteByte`, `WriteInt16`, `WriteInt32`, `WriteString`, `WriteTagByte`, `WriteTagInt16`, `WriteTagInt32`, and `WriteTagInt32Pair` serialize values and tag-value combinations.

State/dependencies: no persistent state. It depends on `xfread`/`xfwrite`, libc allocation, string functions, and network byte-order conversion.

Risks/test signals: `ReadString` allocation and `realloc` handling is careful, but very long unterminated strings can allocate until EOF/error. WriteTag helpers manually construct network byte order instead of using `hton*`, so tests should round-trip tags and integer values. These functions are foundational; failures surface throughout all dump parsing/writing tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/primitive.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/repair.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/repair.c

Purpose: callback set for generating a repaired AFS dump from a parsed possibly incomplete/corrupt input dump.

Important APIs/functions: global `repair_output` is the output `XFILE`. `repair_dumphdr_cb` requires volume ID and synthesizes volume name/from/to times as needed before `DumpDumpHeader`. `repair_volhdr_cb` fills missing or bogus volume fields such as version, name, service flags, uniquifier, type, parent, quota, disk usage, file count, and dates before `DumpVolumeHeader`. `repair_vnode_cb` infers missing vnode type/metadata, creates default ACLs for directories, writes vnode attributes, copies existing data, or synthesizes an empty/default directory page.

State/persistence: writes a new dump to `repair_output`; uses `repair_verbose` for diagnostics. Dependencies include `dump.c`, `dumpfmt.h`, `afs/acl.h`, `afs/dir.h`, and vnode offsets from parsing.

Risks/test signals: generated defaults are lossy and may create semantically incorrect but structurally parseable dumps. The default ACL branch appears to set total differently depending on owner in a way worth review. Test signals are reparsed output dumps and successful restore/salvage behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/repair.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/stagehdr.c -->
# sources/distributed-fs/openafs/src/tools/dumpscan/stagehdr.c

Purpose: parses and writes legacy Stage backup headers that may precede an AFS dump.

Important APIs/functions: `hdr_checksum` computes a 32-bit checksum over the fixed header buffer. `ParseStageHdr` preserves the starting offset, reads a 1024-byte header, validates minimum version, `STAGE_MAGIC`, and checksum, fills `backup_system_header`, duplicates host/partition/volume strings, and optionally reads the next tag byte. On no-header/EOF it seeks back and returns `DSERR_MAGIC`. `DumpStageHdr` fills a fixed `stage_header`, computes checksum complement, and writes it.

State/dependencies: transient allocation of strings in `backup_system_header`; caller frees. Depends on `XFILE`, network byte-order conversion, `stagehdr.h`, and `intNN.h`.

Risks/test signals: fixed `strcpy` into 64-byte fields assumes caller-provided strings fit. Native 64-bit dump length is truncated to 32 bits when written because the Stage header has a 32-bit length field. Test signal is header parse/print and checksum validation on known Stage dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/stagehdr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/stagehdr.h -->
# sources/distributed-fs/openafs/src/tools/dumpscan/stagehdr.h

Purpose: declares the legacy Stage backup header wire format used by `stagehdr.c` and `backuphdr.c`.

Important definitions: constants `STAGE_MAGIC`, `STAGE_CHECKSUM`, `STAGE_VERSMIN`, `STAGE_NAMLEN`, and `STAGE_HDRLEN`. `struct stage_header` lays out version, dates, tape file number, dump time, host/disk/name strings, volume ID, dump length, level, magic, checksum, and flags.

State/dependencies: no behavior or persistent state. It includes `intNN.h` for AFS integer types.

Integration points: `parsedump.c` recognizes `STAGE_VERSMIN` as a possible top-level backup header tag. `ParseStageHdr` validates and maps this struct into the generic `backup_system_header` exposed by `dumpscan.h`.

Risks/test signals: the struct models a fixed 1024-byte header but does not itself enforce packing; compatibility depends on field ordering and platform ABI matching the intended layout. Validation is through checksum and magic during parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tools/dumpscan/stagehdr.h -->
