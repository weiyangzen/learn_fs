# subset-b-009172 research

Grouped research report for rsync socket, syscall, SIMD checksum, support utility, and smoke-test files. Each section preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/simd-checksum-x86_64.cpp -->
# sources/sync-backup/rsync/simd-checksum-x86_64.cpp

Purpose: x86-64 C++ implementation of rsync's weak rolling checksum fast path. It replaces the scalar `get_checksum1()` loop with multiversioned SSE2, SSSE3, and AVX2 routines when `USE_ROLL_SIMD` is enabled, while keeping a scalar tail path for small or leftover byte ranges.

Important APIs/types/functions: the exported C symbol is `uint32 get_checksum1(char *buf1, int32 len)`. Internal workers are `get_checksum1_avx2_64()`, optional external `get_checksum1_avx2_asm()`, `get_checksum1_ssse3_32()`, `get_checksum1_sse2_32()`, `get_checksum1_default_1()`, and `get_checksum1_cpp()`. The file defines unaligned vector typedefs `__m128i_u` and `__m256i_u`, SSE2 compatibility macros that emulate SSSE3-style byte multiply/add operations, `roll_asm_have_avx2()` for runtime gating of the assembly AVX2 path, plus optional benchmark and self-test `main()` functions behind `BENCHMARK_SIMD_CHECKSUM1` and `TEST_SIMD_CHECKSUM1`.

Control flow: `get_checksum1_cpp()` initializes `s1`, `s2`, and index `i`, then attempts increasingly smaller vector blocks. AVX2 consumes 64-byte chunks if available, SSSE3 consumes 32-byte chunks if runtime multiversioning selects it, SSE2 consumes remaining 32-byte chunks, and `get_checksum1_default_1()` finishes 4-byte groups and final bytes. Each vector loop computes the same recurrence as the classic rsync rolling checksum: accumulate `s1` as byte sums plus `CHAR_OFFSET`, and `s2` as the weighted prefix-sum accumulator. The final return packs `(s1 & 0xffff) + (s2 << 16)`.

State and persistence behavior: the routines are pure over the input buffer and checksum accumulators. The only persistent process state is the cached `roll_asm_have_avx2()` result when assembly is enabled. There is no filesystem or network state.

Dependencies and integration points: this file depends on `rsync.h`, rsync integer aliases, `CHAR_OFFSET`, GCC/clang target attributes, and `<immintrin.h>`. It is compiled only for `__x86_64__` as C++ and only emits the optimized symbol when `USE_ROLL_SIMD` is configured. The exported `get_checksum1()` integrates with rsync's block matching and rolling checksum pipeline.

Risks: correctness depends on exact signed-byte handling, block-boundary math, and consistent `CHAR_OFFSET` constants between scalar and vector paths. Runtime CPU dispatch is subtle: the assembly AVX2 path must be gated or it can SIGILL on non-AVX2 CPUs, and compiler multiversioning behavior differs between GCC and clang. The AVX2 `CHAR_OFFSET` branch uses 32-byte constants in comments/code even though the loop consumes 64 bytes, so any nonzero `CHAR_OFFSET` build deserves focused validation. Alignment handling and final tail rollover are high-value regression targets.

Test signals: the `TEST_SIMD_CHECKSUM1` harness compares scalar, SSE2, SSSE3, AVX2, and auto dispatch across aligned and unaligned buffers and sizes from 1 through 65536. `BENCHMARK_SIMD_CHECKSUM1` provides throughput comparisons. Build coverage must include both intrinsic and optional `USE_ROLL_ASM` variants.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/simd-checksum-x86_64.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/socket.c -->
# sources/sync-backup/rsync/socket.c

Purpose: socket and connection management for rsync clients, daemon listeners, proxying, test-time TCP wrappers, and socket option parsing. It centralizes outbound connects, inbound daemon accept loops, and the `RSYNC_CONNECT_PROG` test hook.

Important APIs/types/functions: public entry points include `try_bind_local()`, `open_socket_out()`, `open_socket_out_wrapped()`, `is_a_socket()`, `start_accept_loop()`, and `set_socket_options()`. Internal helpers include `establish_proxy_connection()`, `open_socket_in()`, `sigchld_handler()`, `socketpair_tcp()`, and `sock_exec()`. The `socket_options[]` table maps option names such as `SO_KEEPALIVE`, `TCP_NODELAY`, buffer sizes, and IP TOS choices to `setsockopt()` calls.

Control flow: outbound connections parse `RSYNC_PROXY`, optionally split `USER:PASS@HOST:PORT`, call `getaddrinfo()`, iterate all resolved addresses, optionally bind a local address, apply socket options, enforce an alarm-based connect timeout, and then perform an HTTP CONNECT handshake when proxied. `open_socket_out_wrapped()` expands `%H` in `RSYNC_CONNECT_PROG` and either executes a local socket program or delegates to normal TCP connect. Inbound daemon setup resolves passive addresses, opens as many IPv4/IPv6 sockets as possible, applies reuse and configured options, listens on each fd, and then loops in `select()`, accepting one ready socket and forking a child to run the daemon callback.

State and persistence behavior: the file uses process-level environment (`RSYNC_PROXY`, `RSYNC_CONNECT_PROG`), global config (`bind_address`, `sockopts`, `default_af_hint`, `connect_timeout`, `pid_file_fd`), signal handlers for `SIGALRM` and `SIGCHLD`, and inherited descriptors. It does not persist data itself, but daemon children reopen logs and close inherited listener/pid fds.

Dependencies and integration points: depends on rsync logging/error APIs, `getaddrinfo()`, `getnameinfo()`, TCP/IP headers, `base64_encode()`, `lp_socket_options()`, `lp_listen_backlog()`, `shell_exec()`, and cleanup/error constants. The daemon accept loop integrates with clientserver handling via the callback `fn(fd, fd)`.

Risks: the proxy parser supports only simple colon-delimited credentials and CONNECT targets, so IPv6 proxy literals or colons in credentials are fragile. The connect timeout mutates the global `connect_timeout` to `-1` in the alarm handler. `socketpair_tcp()` is security-sensitive because it creates a loopback listener; it mitigates hijack races by comparing accepted peer and local socket endpoints. Socket option parsing uses `strtok()` on a duplicated string and reports unknown options but continues. Daemon forking requires careful fd closure to avoid pid-file and listener leaks.

Test signals: `RSYNC_CONNECT_PROG` and `sock_exec()` are explicitly for tests that need TCP-like behavior without external network access. Useful coverage includes proxy CONNECT success/failure, bind failures over multiple address families, IPv4/IPv6 listener conflict behavior, option parsing, daemon child reaping, and the anti-hijack peer/local-address check in `socketpair_tcp()`.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/stunnel-rsyncd.conf.in -->
# sources/sync-backup/rsync/stunnel-rsyncd.conf.in

Purpose: template stunnel configuration for serving rsync daemon traffic over SSL/TLS on port 874. It launches rsync as an stunnel-executed daemon process after TLS termination.

Important APIs/types/functions: this is configuration, not code. Important directives are `foreground`, `pid`, listener/remote `TCP_NODELAY` socket options, `setuid`/`setgid`, `[rsync]`, `accept = 874`, certificate/key paths, client verification settings, `exec = @bindir@/rsync`, and `execargs = rsync --server --daemon .`.

Control flow: stunnel accepts a TLS connection, optionally verifies the client certificate depending on the selected `verify`/`CAfile` lines, and execs rsync in daemon-server mode. The comments show an alternate daemon config path using `--config=/etc/rsync-ssl/rsyncd.conf`.

State and persistence behavior: stunnel maintains a pid file at `/var/run/stunnel-rsyncd.pid`; rsync daemon state and logs are delegated to the daemon config. Certificate and key files are read from `/etc/rsync-ssl/certs`.

Dependencies and integration points: depends on stunnel, rsync installed at the configured bindir, server TLS material, system CA bundle or an allowed-client certificate bundle, and an rsync daemon configuration reachable by the executed server.

Risks: the default active example uses `verify = 0`, allowing any client to attempt a TLS connection; authentication then relies on rsync daemon configuration. Running stunnel as root is required for rsync chroot support but increases configuration sensitivity. Certificate/key paths are examples and must be protected on disk.

Test signals: validation is mostly operational: stunnel should parse the generated config, bind port 874, present the configured certificate, execute rsync, and allow `rsync://`-style daemon module access through TLS. A hardened deployment should test the commented `verify = 3` client-certificate mode.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/stunnel-rsyncd.conf.in -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/Makefile -->
# sources/sync-backup/rsync/support/Makefile

Purpose: tiny support-directory makefile that builds the `savetransfer` helper.

Important APIs/types/functions: targets are `all`, `savetransfer`, and `clean`. `all` depends on `savetransfer`; `savetransfer` links from `savetransfer.o`; `clean` removes object files and the executable.

Control flow: normal make implicit rules compile `savetransfer.c` into `savetransfer.o` and link it. No custom compiler flags are specified here.

State and persistence behavior: produces local build artifacts `savetransfer.o` and `savetransfer`; `clean` removes them.

Dependencies and integration points: depends on make's built-in C rules and rsync's headers via `savetransfer.c`. It is a convenience build hook for support tooling, not the main rsync build system.

Risks: because it relies on implicit rules, unusual build environments may miss include paths or feature macros expected by `savetransfer.c`. It does not express header dependencies.

Test signals: `make -C support` should produce `savetransfer`, and `make -C support clean` should remove it.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/atomic-rsync -->
# sources/sync-backup/rsync/support/atomic-rsync

Purpose: Python wrapper that performs a pull-style rsync update into a new hard-linked tree and then swaps it into place, approximating an atomic directory update.

Important APIs/types/functions: `main()`, `atomic_symlink()`, `usage_and_exit()`, and `die()`. Constants include `ALT_DEST_ARG_RE`, which blocks user-supplied `--link-dest`, `--compare-dest`, and `--copy-dest` variants, and `RSYNC_PROG = /usr/bin/rsync`.

Control flow: parse command-line rsync arguments, require an existing local destination directory, reject alternate-dest options, parse allowed rsync exit codes from `ATOMIC_RSYNC_OK_CODES`, decide whether the destination is a `*-1`/`*-2` symlink rotation or a `~new~`/`~old~` directory swap, delete stale staging directories, run rsync with `--link-dest=<current dest>`, and then either rename a newly created symlink over the live link or rename current/new directories.

State and persistence behavior: creates and deletes sibling staging directories, updates symlinks with `os.rename()`, and preserves the prior destination until the next run. It dereferences the destination with `realpath()` and forbids `/` as the destination.

Dependencies and integration points: depends on Python 3, `/usr/bin/rsync`, filesystem hard links, and rsync's `--link-dest`. It is intended for local pull destinations rather than arbitrary push deployments.

Risks: the non-symlink `~old~`/`~new~` path is a rapid double rename, not a fully atomic switch. Existing `~old~` and `~new~` directories are removed. The symlink-rotation mode assumes link text suffix and real target suffix stay synchronized. Exit-code allowance defaults to treating vanished files as acceptable, which may hide real partial-copy problems if operators broaden the environment variable too far.

Test signals: tests should cover symlink rotation, plain directory rotation, rejection of alternate-dest options, `/` rejection, failed rsync return handling, and custom `ATOMIC_RSYNC_OK_CODES` parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/atomic-rsync -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/cvs2includes -->
# sources/sync-backup/rsync/support/cvs2includes

Purpose: generate `.cvsinclude` rsync filter files from CVS metadata so `--cvs-exclude` transfers still include checked-in files and directories.

Important APIs/types/functions: `main()` walks the tree, reads `CVS/Entries`, writes `.cvsinclude`, and removes stale include files. `INC_NAME` is `.cvsinclude`.

Control flow: optionally chdir to the supplied root, walk all subdirectories, remember existing `.cvsinclude` files, detect `CVS/Entries`, parse entries beginning with `/` or `D/`, write `+ /name` include lines next to the CVS directory when content changed, sort child directories for deterministic traversal, and delete include files not regenerated from current CVS metadata.

State and persistence behavior: mutates `.cvsinclude` files throughout the working tree. It avoids rewriting unchanged content but deletes stale generated files.

Dependencies and integration points: depends on Python 3 and CVS `Entries` file format. The generated files are consumed by rsync filters such as `-f ': .cvsinclude'` or `.rsync-filter` includes.

Risks: it assumes CVS entry syntax and does not preserve manual edits in `.cvsinclude` files that are considered stale. Running it in the wrong directory can create or delete include files broadly.

Test signals: create sample `CVS/Entries` files and stale `.cvsinclude` files, run the script, and confirm deterministic include lines, unchanged-file reporting, and stale-file removal.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/cvs2includes -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/deny-rsync -->
# sources/sync-backup/rsync/support/deny-rsync

Purpose: shell helper that emits a minimal rsync protocol error response to a non-daemon client and exits with a refusal-style code.

Important APIs/types/functions: `byte_escape()` formats numeric bytes; globals are `protocol_version=29` and `exit_code=4`. The payload mimics `rprintf(FERROR_XFER, "%s\n", msg)` in rsync's multiplexed protocol.

Control flow: take the first argument as the message, truncate it to fit a simple one-byte length, write protocol version and zero checksum seed as little-endian four-byte values, write a multiplexed error header and message, sleep one second so the client receives the error, and exit 4.

State and persistence behavior: no persistent state. It writes binary protocol bytes to stdout and diagnostic semantics are carried by the client-side rsync.

Dependencies and integration points: depends on bash, `printf`, `echo -ne`, and rsync protocol framing. It is useful as a forced command or policy denial shim.

Risks: protocol version and framing are intentionally naive and fixed; newer clients may behave differently. It supports only short messages and does not escape arbitrary binary data. `echo -E` behavior is shell-dependent but acceptable under bash.

Test signals: invoke via an rsync remote-shell/forced-command path and verify the client displays the supplied message rather than a generic broken-pipe failure and receives exit code 4 semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/deny-rsync -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/file-attr-restore -->
# sources/sync-backup/rsync/support/file-attr-restore

Purpose: Perl utility that parses `find ... -ls` output and restores selected permissions, owners, and groups onto matching local filesystem objects.

Important APIs/types/functions: option parsing via `Getopt::Long`; main input loop; `parse_map_file()` for `user FROM TO` and `group FROM TO` mappings; `usage()`. Options include `--all`, `--perms`, `--owner`, `--groups`, `--map`, `--dry-run`, and repeated `--verbose`.

Control flow: parse options, optionally load user/group mapping overrides, compile a detailed regex for `find -ls` lines, decode find-style escaped filenames, check that the current local object type matches the recorded type, compute mode bits including setuid/setgid/sticky bits from the permission string, resolve owner/group names or numeric IDs with caching, and conditionally call `chmod()` and `chown()`. It prints changed attributes or verbose OK/skip messages.

State and persistence behavior: can mutate file modes and ownership for regular files, directories, devices, FIFOs, and sockets. It skips symlinks. Dry-run computes and reports changes without applying them.

Dependencies and integration points: depends on Perl, `Getopt::Long`, local passwd/group databases, and the exact format produced by `find -ls`. It complements rsync backup/restore workflows when attributes were captured as text.

Risks: parsing is format-sensitive and locale/date-output sensitive. Chowning can clear setuid/setgid bits, so the script repeats chmod after chown when high bits are set. Input filenames must be properly escaped; malformed input aborts. Running with owner/group restoration requires privileges and may map names unexpectedly without a map file.

Test signals: feed fixture `find -ls` lines for each supported file type, escaped names, mapping-file overrides, missing files, type mismatches, dry-run mode, and setuid/setgid preservation after chown.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/file-attr-restore -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/files-to-excludes -->
# sources/sync-backup/rsync/support/files-to-excludes

Purpose: transform a list of file paths into rsync include/exclude filter rules that transfer exactly those files plus their containing directories.

Important APIs/types/functions: `main()` reads paths through `fileinput`, tracks directory prefixes in a set, and prints filter rules. Argparse accepts zero or more input files, defaulting to stdin.

Control flow: for each input line, strip whitespace and leading slashes, split by `/`, emit `+ /dir/` rules for every parent directory not already printed, emit `+ /full/path` for the file, then after all input emit `- /dir/*` for each tracked directory and a final `- /*`.

State and persistence behavior: no filesystem mutation. Output order for parent include rules follows input discovery; directory exclude rules are sorted.

Dependencies and integration points: consumed by rsync as `--exclude-from=FILE` or merged filter rules. It is especially useful when copying sparse file lists while keeping delete behavior controlled.

Risks: blank lines become `+ /` because the code tests the split list rather than the stripped line; callers should filter empty input. Paths are treated as text and not shell-escaped. Directory names with repeated slashes are partially skipped only for empty components in parent traversal.

Test signals: fixture lists should validate parent includes, final excludes, duplicate suppression, absolute path normalization, and behavior with blank or malformed lines.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/files-to-excludes -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/git-set-file-times -->
# sources/sync-backup/rsync/support/git-set-file-times

Purpose: set checked-out file mtimes to the commit time of the last Git commit that changed each file, optionally listing what would change.

Important APIs/types/functions: `main()`, `print_line()`, `NULL_COMMIT_RE`, and argparse options `--git-dir`, `--tree`, `--prefix`, `--quiet`, `--list`, and file filters.

Control flow: locate `.git` from `git rev-parse` when not supplied, list tracked files from either `git ls-files -z` or `git ls-tree -z -r --name-only`, remove modified working-tree files from the mutation set unless listing, stream `git log -r --name-only --format=... -z --no-renames`, and for each commit-time/file batch still in scope either print current-vs-target time or call `os.utime(..., follow_symlinks=False)`.

State and persistence behavior: mutates mtimes of unmodified tracked files in the working tree, never follows symlinks for timestamp setting, and stops once all target files have been resolved. Modified files retain their current mtimes.

Dependencies and integration points: depends on Python 3, Git CLI, UTC datetime formatting, and a Git checkout or explicit tree. It is useful for reproducible exported trees and rsync workflows that care about mtimes.

Risks: it ignores renames, so renamed files take the last commit that touched the current path. The `git status -z` parsing assumes porcelain status width and may not handle every status combination. `--tree` with `--prefix` can target paths outside the current checkout if misused.

Test signals: run on a small repository with modified and unmodified files, symlinks, file subset filters, `--list` and `--list --list`, explicit `--tree`, and renamed files to document expected no-renames behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/git-set-file-times -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/idmap -->
# sources/sync-backup/rsync/support/idmap

Purpose: generate rsync `--usermap` or `--groupmap` strings from passwd/group-style files for local transfers involving mounted backups with different UID/GID assignments.

Important APIs/types/functions: `NAME_ID_RE` parses `name:...:id` records. `main()` reads one or more files via `fileinput` and emits comma-separated mapping pairs. Argparse requires exactly one of `--from` or `--to`.

Control flow: scan each input line, skip non-matching records, build `name:id` pairs for `--to` or `id:name` pairs for `--from`, and print the comma-joined result.

State and persistence behavior: no persistent state or filesystem mutation; output is a command-line fragment for rsync.

Dependencies and integration points: depends on Python 3 and passwd/group file syntax. The output plugs directly into rsync `--usermap` or `--groupmap`.

Risks: the regex only accepts word-character names, so names with dashes or other valid system characters are skipped. Large mapping files can produce very long command lines. It does not validate duplicate names/IDs or local availability.

Test signals: fixture passwd and group files should cover `--from`, `--to`, skipped malformed lines, numeric IDs, and names outside `\w+` if behavior needs to be documented.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/idmap -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/install_deps_ubuntu.sh -->
# sources/sync-backup/rsync/support/install_deps_ubuntu.sh

Purpose: convenience script for installing rsync build dependencies on Ubuntu/Debian systems.

Important APIs/types/functions: no functions; it runs a sequence of `sudo apt install -y` commands for compiler, documentation, ACL/xattr, checksum, compression, and OpenSSL development packages.

Control flow: invoke apt for base tools (`gcc`, `g++`, `gawk`, `autoconf`, `automake`, `python3-cmarkgfm`), then separate package groups for ACL, attr, xxhash, zstd, lz4, and OpenSSL.

State and persistence behavior: mutates the host package database and installs system packages via sudo.

Dependencies and integration points: depends on bash, sudo, apt, and Debian-family package names. It prepares the environment for configuring/building rsync and related docs/features.

Risks: no `set -e`, so a failed install command may not stop later commands. It assumes package names and repository availability. It is intentionally distro-specific and should not be run blindly in non-Debian environments.

Test signals: on a fresh Ubuntu/Debian container, execution should install all listed packages and leave the rsync configure/build able to find ACL, xattr, xxhash, zstd, lz4, and OpenSSL headers.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/install_deps_ubuntu.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/instant-rsyncd -->
# sources/sync-backup/rsync/support/instant-rsyncd

Purpose: interactive bash helper that creates and starts a simple unprivileged rsync daemon serving one writable module rooted in the current directory.

Important APIs/types/functions: no shell functions; important generated files are `rsyncd.conf`, optional `<module>.secrets`, `start`, `stop`, `rsyncd.log`, and `rsyncd.pid`.

Control flow: prompt or read arguments for module, port, auth user, and rsync path; create the module directory; write a minimal daemon config with `use chroot = no`; optionally prompt for a password and write a protected secrets file; generate start/stop scripts; start the daemon; print log output and an `rsync://user@host:port/module/` URL; then run `rsync --list-only` as a smoke test.

State and persistence behavior: creates a module directory and several control/config files in the current directory, starts a background daemon, and leaves start/stop scripts for later operation.

Dependencies and integration points: depends on bash, rsync daemon mode, hostname, local filesystem permissions, and optional rsync daemon auth. It is a test/reproduction aid for daemon-related issues.

Risks: creates a writable module with `read only = false` and `use chroot = no`, so it is unsuitable as a hardened production config without edits. It uses unsanitized module/user values in generated config. Existing files with the same names can be overwritten or cause confusing state.

Test signals: create a temporary directory, run with explicit module/port/no auth and with auth, verify generated config, start/stop scripts, pid behavior, and successful `--list-only` connection.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/instant-rsyncd -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/json-rsync-version -->
# sources/sync-backup/rsync/support/json-rsync-version

Purpose: normalize rsync `--version --version` output into JSON, including support for older rsync versions that do not emit native JSON.

Important APIs/types/functions: `main()`, `TWEAK_NAME` for renamed capability keys, `MOVE_OPTIM` for options that belong under optimizations, and argparse's optional `rsync` command argument.

Control flow: read version text from stdin when no rsync command is supplied, otherwise execute `[rsync, --version, --version]`; pass through native JSON unchanged; parse the version/protocol line, copyright, web site, list-style sections, and comma-style capability/optimization sections; coerce `no` to false and `N-bit` strings to integer bit counts; ensure standard keys exist; infer GPL version from major version; and dump JSON.

State and persistence behavior: no persistent state. It emits a single JSON object to stdout.

Dependencies and integration points: depends on Python 3, subprocess, json, and rsync version-output formatting. It supports tooling that wants structured rsync build capability metadata.

Risks: parser state depends on section headers and indentation. The variable `saw_comma` is initialized only after the first non-special section header, so unexpected indented lines before a header would fail. License inference is simplistic. Unknown formatting in future rsync versions can misclassify fields.

Test signals: feed native JSON, current text output, legacy text output, no-capability output, `no foo`, `64-bit`, and misplaced `asm/SIMD` optimizations; verify stable JSON keys and pass-through behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/json-rsync-version -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/logfilter -->
# sources/sync-backup/rsync/support/logfilter

Purpose: Perl filter that extracts rsync daemon log lines belonging to a selected module or module subpath.

Important APIs/types/functions: main loop only. It defines regex prefixes for syslog and rsync log-file formats and tracks matching pids in `%pids`.

Control flow: take a module/path regex argument, parse each input log line for pid and message, detect session-start messages of the form `rsync on|to MODULE from`, mark or unmark that pid depending on whether the module matches, and print subsequent lines for marked pids.

State and persistence behavior: no file mutation; in-memory pid tracking persists across input lines so related transfer messages are emitted after the initial module match.

Dependencies and integration points: depends on Perl and rsync daemon log formats. It can read stdin or named log files.

Risks: the module argument is used as a regular expression, which is powerful but can surprise users expecting a literal name. Pid reuse inside a single log stream could misattribute lines if start/stop patterns are missing. Format changes may break parsing.

Test signals: sample syslog and rsyncd-format logs should cover matching modules, subdirectory matches, nonmatching modules, pid state reset, and regex metacharacters in module names.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/logfilter -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/lsh -->
# sources/sync-backup/rsync/support/lsh

Purpose: Perl local-shell replacement that emulates a remote shell for localhost-only rsync testing, including optional user switching and optional `rrsync` forced-command emulation.

Important APIs/types/functions: option parsing via `Getopt::Long`; main command construction; `usage()`. Options include ignored ssh-like flags, `-l USER`, `--no-cd`, `--sudo`, `--rrsync=DIR`, and `--rropts=STR`.

Control flow: parse ssh-style options until host/command, accept only `localhost` or `lh`, derive login user from `user@host` or `-l`, optionally switch UID/GID directly or prepend `sudo -H -u`, chdir to the target user's home unless disabled, and either exec `/bin/sh -c <command>` or set `SSH_ORIGINAL_COMMAND` and exec `rrsync` with requested options.

State and persistence behavior: mutates process UID/GID, environment variables (`USER`, `USERNAME`, `HOME`, `SSH_ORIGINAL_COMMAND`), current directory, and then replaces itself with the target command.

Dependencies and integration points: depends on Perl, system passwd/group databases, optional sudo, `/bin/sh`, and optional `rrsync`. It integrates with rsync via `RSYNC_RSH` or `-e`.

Risks: direct UID/GID switching requires privileges and can fail partially; the script checks both real and effective IDs. Command execution through `/bin/sh -c` preserves shell-evaluation risks consistent with remote-shell semantics. Only localhost names are accepted by design.

Test signals: use as `RSYNC_RSH` for local push/pull tests, cover `lh` no-chdir behavior, `localhost` home chdir, `-l` user switching, `--sudo`, and `--rrsync` option forwarding.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/lsh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/lsh.sh -->
# sources/sync-backup/rsync/support/lsh.sh

Purpose: simpler POSIX-shell local remote-shell shim for rsync tests that only pretends to connect to `localhost` or `lh`.

Important APIs/types/functions: no functions; it parses a small subset of ssh-like options, `-l USER`, and `--no-cd`.

Control flow: consume options until host, reject non-local hosts, set `do_cd=n` for `lh`, optionally build a `sudo -H -u USER sh -c` command with a home-directory `cd`, otherwise chdir to the current user's home when requested and `eval` the remaining command.

State and persistence behavior: may change current directory and may execute through sudo. No persistent files are touched.

Dependencies and integration points: depends on `/bin/sh`, `sed`, `perl` for home lookup under `-l`, and sudo for alternate users. It is used by tests such as `testsuite/00-hello_test.py` through `RSYNC_RSH`.

Risks: `eval "${@}"` deliberately applies shell parsing to the remote command and should remain test-only. It ignores many options without validating their arguments beyond the simple parser. Host validation is intentionally narrow.

Test signals: rsync local remote-shell transfers to and from `lh:` and `localhost:`, `-l USER` paths, and arguments containing shell-special characters.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/lsh.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/mnt-excl -->
# sources/sync-backup/rsync/support/mnt-excl

Purpose: generate rsync exclude rules for mount points under a source path, catching bind mounts that `--one-file-system` may not distinguish.

Important APIs/types/functions: `main()` normalizes the requested path and scans `MNT_FILE = /proc/mounts`.

Control flow: preserve whether the input path was slash-content style, resolve the path with `realpath()`, derive the parent/trailing anchor used by rsync filters, read mount paths from `/proc/mounts`, and print `- /relative/mount` for each mount beneath but not equal to the requested root.

State and persistence behavior: no mutation; emits exclude rules on stdout.

Dependencies and integration points: Linux-specific `/proc/mounts`, Python 3, and rsync exclude/filter syntax. Intended usage is piping into `rsync --exclude-from=-`.

Risks: mount paths with spaces are escaped in `/proc/mounts`; the script blindly uses `line.split()[1]`, so unusual escaping may not decode as users expect. It is Linux-centric. Realpath normalization changes symlinked source semantics.

Test signals: mock or fixture `/proc/mounts` behavior is hard-coded, so integration tests on a temporary mount namespace are most realistic. Validate differences between `/dir` and `/dir/` anchoring.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/mnt-excl -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/munge-symlinks -->
# sources/sync-backup/rsync/support/munge-symlinks

Purpose: recursively add or remove rsync daemon's symlink-munging prefix `/rsyncd-munged/` from symlink targets.

Important APIs/types/functions: `main()`, `find_symlinks()`, `process_one_arg()`, constants `SYMLINK_PREFIX` and `PREFIX_LEN`, and argparse flags `--munge`, `--unmunge`, and `--all`.

Control flow: for each argument, process it if it is a symlink or recursively scan it if it is a directory; read each link target; in unmunge mode remove one prefix or all repeated prefixes with `--all`; in munge mode add the prefix unless already munged or `--all` forces another; replace the symlink by unlinking and recreating it; print the resulting mapping.

State and persistence behavior: mutates symlink objects in place. Directory traversal does not follow symlinks as directories.

Dependencies and integration points: depends on Python 3 and filesystem symlink support. It aligns with rsyncd.conf's `munge symlinks` behavior.

Risks: unlink/recreate is not atomic, so a failed recreate can leave the symlink missing. Permissions or races in writable directories can affect correctness. Non-symlink non-directory arguments are only reported to stderr, not fatal.

Test signals: temporary symlink trees should cover munge, unmunge, repeated prefixes with and without `--all`, directory recursion, and recreate failure handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/munge-symlinks -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/nameconvert -->
# sources/sync-backup/rsync/support/nameconvert

Purpose: stdin/stdout daemon helper protocol for converting user and group IDs to names and names to IDs.

Important APIs/types/functions: `main()` reads requests and uses Python `pwd` and `grp` modules. Supported request prefixes are `uid`, `gid`, `usr`, and `grp`.

Control flow: for each input line, split into request and argument, dispatch to `pwd.getpwuid`, `grp.getgrgid`, `pwd.getpwnam`, or `grp.getgrnam`, print an empty line for unknown names/IDs, and exit with an error on malformed or unsupported requests.

State and persistence behavior: stateless stream processor; no filesystem mutation.

Dependencies and integration points: depends on Python 3 and local NSS/passwd/group resolution. Used by rsync daemon configurations via the `name converter` setting, often when chrooting changes visibility of system account databases.

Risks: lookups can block or vary depending on NSS backends. Malformed input terminates the process, which is appropriate for protocol errors but can break a daemon session. It trusts local system account data.

Test signals: feed each valid request type, unknown users/groups, malformed request lines, and verify flushing per response for daemon interaction.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/nameconvert -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/rrsh.sh -->
# sources/sync-backup/rsync/support/rrsh.sh

Purpose: shell helper for abdiff/testing that emulates sshd forced-command execution of `rrsync DIR`.

Important APIs/types/functions: no functions. It consumes the configured `RRSYNC` executable and restricted `DIR`, strips rsync remote-shell options until `lh` or `localhost`, sets `SSH_ORIGINAL_COMMAND`, and execs rrsync.

Control flow: parse and skip selected ssh-style options (`-l`, other dash options), require a pretend local host, collect the remaining rsync server command, export it as `SSH_ORIGINAL_COMMAND`, and `exec "$RRSYNC" "$DIR"`.

State and persistence behavior: only environment mutation before exec. No files are changed directly.

Dependencies and integration points: depends on `/bin/sh` and an rrsync executable. It lets tests exercise rrsync's parsing path without an actual ssh daemon.

Risks: parser is intentionally minimal and accepts only local pretend hosts. It does not enforce options itself; all restriction semantics are delegated to rrsync.

Test signals: use as rsync `-e "sh rrsh.sh <rrsync> <dir>"` and confirm push/pull commands are passed through `SSH_ORIGINAL_COMMAND` exactly as sshd would provide.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/rrsh.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/rrsync -->
# sources/sync-backup/rsync/support/rrsync

Purpose: restricted rsync forced-command wrapper for ssh authorized_keys deployments, limiting rsync server operations to a configured directory and optional read/write/delete policy.

Important APIs/types/functions: constants `RSYNC`, `LOGFILE`, option policy tables `short_disabled`, `short_disabled_subdir`, `short_no_arg`, `short_with_num`, and `long_opts`; functions `main()`, `validated_arg()`, `lock_or_die()`, `die()`, and `OurArgParser.error()`.

Control flow: parse wrapper options and resolve the restricted dir, optionally lock the directory, read `SSH_ORIGINAL_COMMAND`, require `rsync --server`, determine sender/push mode, apply read-only/write-only/no-delete/no-overwrite policy by disabling rsync options or appending server options, parse the server command using a restricted regex, validate every option and option argument, expand braces/globs for transfer args, reject `..` under non-root restricted dirs, ensure real paths stay under the restricted dir, log the final command if `rrsync.log` exists, and exec or run `/usr/bin/rsync --server ... -- . <args>`.

State and persistence behavior: changes current directory to the restricted dir, optionally holds an advisory flock on that directory, appends to `rrsync.log`, and then either `execlp()`s rsync or waits for a child process. It can add `--munge-links` and `--ignore-existing` to server options.

Dependencies and integration points: depends on Python 3, optional `braceexpand`, glob, socket reverse lookup, fcntl locking, sshd-provided `SSH_ORIGINAL_COMMAND` and `SSH_CONNECTION`, and rsync server option conventions.

Risks: this is security-sensitive argument parsing. Any newly added rsync server option must be reflected in `long_opts`/short tables with the right validation type. It assumes the rsync protocol/command line has not been maliciously hijacked after validation. `realpath()` validation can be affected by races between validation and rsync execution, though the wrapper narrows intended paths significantly. Logging does reverse DNS opportunistically and can block or return unexpected tuple formatting.

Test signals: tests should cover read-only and write-only enforcement, delete-option disabling, subdir disabling of symlink-sensitive short options, absolute path allowance, unsafe symlink/path rejection, brace expansion, glob behavior, files-from/log-file option-argument validation, lock contention, `ssh host true`, and passthrough of valid server commands.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/rrsync -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/rsync-no-vanished -->
# sources/sync-backup/rsync/support/rsync-no-vanished

Purpose: bash wrapper around `/usr/bin/rsync` that suppresses vanished-file warnings and treats rsync exit code 24 as success for client runs.

Important APIs/types/functions: constants `REAL_RSYNC`, `IGNOREEXIT=24`, and `IGNOREOUT` regex. No functions are defined.

Control flow: if any argument is `--server`, immediately exec real rsync so server-side protocol is untouched. Otherwise enable `pipefail`, run rsync with stderr piped through `grep -E -v` while preserving stdout on its original stream, capture rsync's pipeline status, map return code 24 to 0, and exit with the adjusted code.

State and persistence behavior: no persistent state; it filters process output.

Dependencies and integration points: depends on bash arrays/process redirection, grep, and rsync exit-code semantics. It can be installed under another name or even as `rsync` because server mode is bypassed.

Risks: filtering is regex-based and may hide lines that match the vanished pattern but matter in context. Only code 24 is remapped. Quoting around `$REAL_RSYNC` assumes the path has no spaces.

Test signals: vanished-file scenarios should produce zero exit and filtered stderr; unrelated warnings/errors should remain visible and preserve nonzero exit. Server-mode invocation must exec real rsync without filtering.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/rsync-no-vanished -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/rsync-slash-strip -->
# sources/sync-backup/rsync/support/rsync-slash-strip

Purpose: bash wrapper that strips one trailing slash from each non-root rsync command-line argument before invoking real rsync, changing `src/` semantics to match `src`.

Important APIs/types/functions: constant `REAL_RSYNC=/usr/bin/rsync`; main loop builds `args=()`.

Control flow: iterate original arguments, bypass immediately to real rsync if `--server` is present, preserve `/` exactly, otherwise append `${arg%/}` to remove one trailing slash, then exec real rsync with transformed arguments.

State and persistence behavior: no persistent state. It only transforms argv.

Dependencies and integration points: depends on bash arrays and rsync. It is intended as a user command alias/wrapper, not a server-side filter.

Risks: it strips trailing slashes from every argument, including option values and remote specs, which may be surprising. Users must use `src/.` or `src//` when they really want directory contents. Server mode must bypass to avoid corrupting rsync protocol invocation.

Test signals: verify `src/` becomes `src`, `/` remains `/`, `src//` becomes `src/`, and server-mode arguments are untouched.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/rsync-slash-strip -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/rsyncstats -->
# sources/sync-backup/rsync/support/rsyncstats

Purpose: Perl report generator for rsync daemon transfer logs, producing daily, hourly, archive-section, and domain summaries.

Important APIs/types/functions: main parsing/report loop, Perl formats `top1/line1`, `top2/line2`, `top3/line3`, `top8/line8`, comparator subs `datecompare`, `domnamcompare`, `bytecompare`, `faccompare`, and `usage()`. Options include `--hourly-report`, `--domain-report`, `--total-report`, `--depth-limit`, `--domain`, `--section`, and `--file`.

Control flow: parse options, open the log file, optionally print filters, parse lines matching syslog-like or rsyncd-like prefixes and default transfer-log fields, normalize itemized `%i` operations to send/recv, build module/file path keys up to a depth limit, filter by section/domain, aggregate file and byte counts by date, hour, section, and domain, then render formatted reports for selected dimensions.

State and persistence behavior: read-only over the log file; all aggregation is in memory. It exits if no data matched.

Dependencies and integration points: depends on Perl, `Getopt::Long`, rsync daemon transfer log format, and default `/var/log/rsyncd.log` unless overridden.

Risks: regex parsing is tightly coupled to log format and IPv4 bracket field shape. Domain classification treats numeric-looking hosts or short names as `unresolved`. The code has legacy globals without `strict`, making typo bugs easier. Send/recv separation is noted as TODO and not reflected in separate totals.

Test signals: fixture logs should cover syslog and rsyncd prefixes, `%o` and `%i` operation styles, section/domain/depth filters, no-data errors, and each optional report format.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/rsyncstats -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/support/savetransfer.c -->
# sources/sync-backup/rsync/support/savetransfer.c

Purpose: C proxy helper that runs a program while copying stdin to stdout and saving either the data going into the program or coming out of it. It is used to inspect rsync protocol streams through remote-shell paths.

Important APIs/types/functions: `main()`, `run_program()`, `set_nonblocking()`, and `set_blocking()`. Global state includes `buf[4096]` and `save_data_from_program`.

Control flow: parse `-i` or `-o`, open/truncate the output file in binary mode, ignore `SIGPIPE`, fork/exec the requested program with one side of a pipe connected to its stdin or stdout, put stdio into binary mode where needed, set stdin nonblocking and stdout blocking, then loop with a 30-second `select()` timeout reading stdin, writing the same bytes to stdout and the capture file. Timeout or EOF ends the loop.

State and persistence behavior: creates or truncates the capture file and proxies bytes between process descriptors. It does not wait for the child explicitly, so process lifetime is mostly governed by pipe closure and exec behavior.

Dependencies and integration points: includes `../rsync.h` for portability macros such as `NONBLOCK_FLAG`, `O_BINARY`, `SIGACTION`, and platform headers. It integrates with rsync examples via `--rsh` and `--rsync-path`.

Risks: the 30-second inactivity timeout is a hard-coded behavior that can delay completion or abort slow transfers. Partial writes are treated as fatal rather than retried. It may not notice child exit promptly when saving input and no more data arrives. Capture files can contain sensitive protocol/data bytes.

Test signals: run with simple producer/consumer commands in both `-i` and `-o` modes, verify captured streams match expected data, binary bytes are preserved, timeout behavior is understood, and failed exec/pipe/write paths report errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/support/savetransfer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/syscall.c -->
# sources/sync-backup/rsync/syscall.c

Purpose: rsync's portability and policy layer around filesystem syscalls. It enforces dry-run/read-only/list-only behavior, abstracts platform differences, handles fake-super and metadata preservation, and adds symlink-race-safe `*_at` variants for daemon-without-chroot receiver operations.

Important APIs/types/functions: basic wrappers include `do_unlink`, `do_symlink`, `do_link`, `do_lchown`, `do_mknod`, `do_rmdir`, `do_open`, `do_chmod`, `do_rename`, `do_ftruncate`, `do_mkdir`, `do_mkstemp`, stat/lstat/fstat/lseek, timestamp setters, `do_fallocate`, `do_punch_hole`, `do_open_nofollow`, and `do_open_checklinks`. Safe parent-dir variants include `do_unlink_at`, `do_symlink_at`, `do_link_at`, `do_lchown_at`, `do_mknod_at`, `do_rmdir_at`, `do_open_at`, `do_chmod_at`, `do_rename_at`, `do_mkdir_at`, `do_stat_at`, `do_lstat_at`, and `do_utimensat_at`. Confinement helpers are `secure_relative_open()`, `path_has_dotdot_component()`, Linux `openat2_beneath()`/`secure_relative_open_linux()`, `secure_relative_open_resolve_beneath()`, `rand_bytes()`, and `secure_mkstemp()`.

Control flow: most mutating wrappers first short-circuit dry-run and reject read-only/list-only. Plain wrappers call the platform syscall with rsync-specific tweaks such as fake-super file placeholders, symlink readback, `O_NOATIME`, chmod portability, socket mknod emulation, or preallocation length adjustment. The `*_at` wrappers are gated to daemon mode with `use chroot = no`; otherwise they fall back to the plain wrapper. In the gated case they split the path, open the parent directory through `secure_relative_open()`, invoke an at-style syscall against the resulting dirfd, preserve errno across close, and return the syscall result.

State and persistence behavior: mutates filesystem objects, metadata, allocation state, and timestamps according to transfer options. It reads global rsync mode/config variables such as `dry_run`, `am_root`, `am_sender`, `read_only`, `list_only`, `inplace`, `preallocate_files`, `sparse_files`, `preserve_perms`, `preserve_executability`, `open_noatime`, `copy_links`, and `copy_unsafe_links`. It also defines logical `curr_dir`/`curr_dir_len` for tests and secure module re-anchoring.

Dependencies and integration points: depends on `rsync.h`, `ifuncs.h`, platform feature macros, Linux `openat2`, `O_RESOLVE_BENEATH`, ACL/xattr/fake-super callers, generator/receiver code that chooses safe variants, and cleanup/error policy in higher layers. `secure_relative_open()` integrates with daemon module state (`module_dir`, `module_dirlen`, `curr_dir`) to allow in-module `..` climbs for relative alt-dest paths on kernels that can enforce `RESOLVE_BENEATH`.

Risks: this file is security-critical. Fallback behavior differs by platform: kernels without `openat2` or `O_RESOLVE_BENEATH` reject all literal `..` components and reject symlinked directories in the portable walk, trading compatibility for safety. Some operations lack portable at-style equivalents, notably socket creation by pathname and macOS crtime setting, leaving documented residual behavior or dropped metadata preservation. Fake-super branches must use `O_NOFOLLOW` correctly to avoid basename symlink redirection. `secure_mkstemp()` rejects only `../` and `/../` rather than every trailing/bare `..` component, so it should be reviewed against `path_has_dotdot_component()` consistency. Preallocation and hole punching are sensitive to filesystem support and sparse-file options.

Test signals: focused C harnesses in this subset cover `secure_relative_open()` dot-dot rejection and `do_chmod_at()` symlink escape behavior. Broader regression should exercise every `*_at` wrapper under daemon/no-chroot with escaping parent symlinks, legitimate in-tree symlinks on kernels with resolve-beneath support, fallback platforms, fake-super creation, read-only/list-only refusal, dry-run no-op, sparse plus preallocate, timestamp fallback tiers, and `do_open_checklinks()` with copy-link options.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/t_chmod_secure.c -->
# sources/sync-backup/rsync/t_chmod_secure.c

Purpose: standalone C test harness for `do_chmod_at()` confinement in daemon-without-chroot mode, especially the symlink parent-component attack associated with CVE-2026-29518 follow-up hardening.

Important APIs/types/functions: `kernel_resolve_beneath_supported()`, `check()`, and `main()`. It defines rsync globals required by `syscall.c` and declares external `am_daemon`/`am_chrooted`.

Control flow: chdir to the supplied module directory, simulate `am_daemon=1` and `am_chrooted=0`, probe whether the running kernel supports resolve-beneath semantics, then run four scenarios: chmod through an in-tree directory symlink, chmod through an escaping symlink, chmod a plain relative path, and chmod a top-level file. `check()` validates return success/rejection and final mode.

State and persistence behavior: mutates modes of fixture files inside the provided test directory and verifies the outside trap file remains unchanged.

Dependencies and integration points: links with rsync syscall/object stubs, uses `openat2_usable()` when available, and expects a shell test wrapper to create `realdir`, `inside_link`, `escape_link`, `../trap`, sentinel files, and `topfile`.

Risks: expected behavior for in-tree symlinks is platform-dependent: kernels with resolve-beneath should allow them, portable fallback rejects them. The test must therefore probe runtime support instead of hardcoding one outcome. It is meaningful only when daemon/no-chroot globals are set.

Test signals: success prints OK for all scenarios and returns 0. Failures indicate either escape not rejected, legitimate path broken unexpectedly for that platform tier, or ordinary chmod regression.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/t_chmod_secure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/t_secure_relpath.c -->
# sources/sync-backup/rsync/t_secure_relpath.c

Purpose: standalone C test harness for `secure_relative_open()` front-door validation of dangerous relative paths and basedirs containing literal `..` components.

Important APIs/types/functions: `check_relpath()`, `check_basedir()`, and `main()`. It defines required rsync globals and uses `secure_relative_open()`.

Control flow: chdir to a supplied test dir, set daemon/no-chroot globals, create `subdir`, and attempt to open suspect relpaths (`..`, `../foo`, `subdir/..`, `subdir/../subdir`, `foo/../bar`, `/foo`, `/`) and basedirs (`..`, `../subdir`, `subdir/..`, `foo/../bar`). Each check requires failure with `errno == EINVAL`.

State and persistence behavior: creates a `subdir` in the test directory and opens no persistent fd on success because success is treated as failure and closed.

Dependencies and integration points: links with `syscall.c` and test stubs. It exists to keep portable fallback behavior consistent with kernel-enforced resolve-beneath behavior.

Risks: it deliberately rejects paths that may resolve inside the tree after normalization, so callers needing such paths must normalize or rely on the special module-root reanchoring path in `secure_relative_open()`. The test only covers validation, not successful safe opens.

Test signals: every listed path must be rejected with EINVAL. Any valid fd or different errno is reported as a failure and returns nonzero.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/t_secure_relpath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/t_stub.c -->
# sources/sync-backup/rsync/t_stub.c

Purpose: simple rsync symbol stub file that lets standalone C test helpers link against selected rsync objects without the full rsync binary.

Important APIs/types/functions: global variables for rsync modes/config (`do_fsync`, `inplace`, `am_daemon`, `am_chrooted`, `module_id`, `module_dirlen`, preservation flags, `max_alloc`, `partial_dir`, `module_dir`, `daemon_filter_list`) and stub functions `rprintf()`, `rsyserr()`, `_exit_cleanup()`, `check_filter()`, `copy_xattrs()`, `free_xattr()`, `free_acl()`, `lp_name()`, `lp_use_chroot()`, `who_am_i()`, `csum_len_for_type()`, and `canonical_checksum()`.

Control flow: logging stubs print to stderr; `_exit_cleanup()` reports the requested exit and terminates; most feature hooks return inert defaults.

State and persistence behavior: initializes process globals used by linked rsync modules. No persistent filesystem state is changed by the stubs themselves.

Dependencies and integration points: included by test executables such as secure path/chmod harnesses. It intentionally relies on `curr_dir` being defined by `syscall.c`.

Risks: stubs can mask behavior that depends on real configuration, filters, xattrs, ACLs, or checksum choices. `max_alloc` is deliberately unlimited because zero would trip rsync allocation guards in tests.

Test signals: successful linkage and predictable stderr output from helper programs are the main signals. Tests that need real filters, xattrs, ACLs, or module config should not use this stub unchanged.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/t_stub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/t_unsafe.c -->
# sources/sync-backup/rsync/t_unsafe.c

Purpose: tiny standalone test harness for rsync's `unsafe_symlink()` helper.

Important APIs/types/functions: `main()` only, plus minimal rsync globals required for linking.

Control flow: require exactly `LINKDEST` and `SRCDIR` arguments, call `unsafe_symlink(argv[1], argv[2])`, print `unsafe` or `safe`, and return 0 unless usage is wrong.

State and persistence behavior: read-only; no filesystem mutation is performed by this harness.

Dependencies and integration points: links against rsync code that implements `unsafe_symlink()`. Used by shell tests to classify symlink targets under rsync's safe-links logic.

Risks: the harness exposes only a binary textual result and does not assert expected values itself. It sets `am_sender=1`, which matters for code paths that depend on sender/receiver role.

Test signals: shell-level fixtures pass link targets and source dirs and compare stdout to expected `safe` or `unsafe`.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/t_unsafe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testrun.c -->
# sources/sync-backup/rsync/testrun.c

Purpose: small C wrapper that runs a testsuite shell script with a timeout and returns the child script's exit status.

Important APIs/types/functions: `main()`, constants `DEFAULT_TIMEOUT_SECS` and `TESTRUN_TIMEOUT`.

Control flow: parse timeout from the environment or default to 5 minutes, fork, in the child replace `argv[0]` with `sh` and `execvp()` the provided script/options, and in the parent poll `waitpid(..., WNOHANG)` once per second. If elapsed sleeps exceed the timeout, send SIGTERM and exit 1. If the child exits normally, return its status; if it dies by signal, return 255.

State and persistence behavior: creates a child process and may terminate it. No files are directly mutated.

Dependencies and integration points: depends on POSIX fork/exec/wait/kill and rsync portability headers. It is part of the rsync test harness, guarding shell tests from hanging indefinitely.

Risks: timeout check uses `slept++ > timeout_secs`, so actual timeout is roughly one second beyond the configured value. It sends only SIGTERM, not SIGKILL, so stubborn descendants may survive. It only reports the direct child's normal exit status.

Test signals: run with a fast successful script, a failing script, a script that exits by signal, and a sleep longer than `TESTRUN_TIMEOUT` to confirm exit mapping and timeout diagnostics.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testrun.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/00-hello_test.py -->
# sources/sync-backup/rsync/testsuite/00-hello_test.py

Purpose: foundational Python smoke test for rsync command availability, help output, local directory copying, local remote-shell behavior, and old-argument compatibility.

Important APIs/types/functions: imports `FROMDIR`, `TODIR`, `SRCDIR`, `RSYNC`, `RSYNC_PEER`, `checkit()`, `run_rsync()`, `test_fail()`, and later `rsync_argv()` from `rsyncfns`. Local helpers are `append_line()` and `copy_weird()`.

Control flow: set `RSYNC_RSH` to `support/lsh.sh`, verify `--version`, `--info=help`, and `--debug=help` exit successfully, create a source directory with shell-special characters in its name, append lines before successive transfers, and validate local copy plus pull/push transfers via `lh:` with and without `-s`. It then tests `--old-args` and `RSYNC_OLD_ARGS=1` by copying two files through a single remote argument string `one two` and confirming both files arrive.

State and persistence behavior: creates and mutates files under test `FROMDIR` and `TODIR`, changes current directory temporarily for old-args tests, and mutates a copy of the environment for the subprocess case.

Dependencies and integration points: depends on the Python rsync test harness, built rsync binaries, `support/lsh.sh`, and local-shell semantics for `lh:` hosts.

Risks: uses shell-sensitive path names and old-args behavior intentionally; failures may indicate quoting regressions rather than transfer engine problems. It imports `subprocess` mid-file and runs one command outside `run_rsync()` to inject environment.

Test signals: any nonzero help command fails the test; `checkit()` validates source/destination equality for transfer cases; explicit file-existence checks catch old-args and environment-variable compatibility regressions.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/testsuite/00-hello_test.py -->
