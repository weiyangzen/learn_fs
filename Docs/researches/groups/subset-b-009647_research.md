# Research Group subset-b-009647

This grouped report covers the assigned ksmbd-tools build, administrative CLI, shared header, mountd IPC, and DCE/RPC sources. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/.travis.yml -->
# sources/user-network-fs/ksmbd-tools/.travis.yml

## Purpose

Defines the legacy Travis CI matrix for ksmbd-tools. It validates both build systems and all Kerberos feature modes on Ubuntu jammy.

## Important APIs, Types, and Functions

The job matrix installs libnl, GLib transitive build tooling, MIT Kerberos, Heimdal Kerberos, ninja, and user-local Meson. It runs autotools `distcheck` and Meson `dist` with krb5 disabled, MIT krb5 enabled, and Heimdal krb5 enabled.

## Control Flow

Each job prepares either `./autogen.sh && ./configure` or a fresh `build` directory, then runs the distribution target. Kerberos jobs inject implementation-specific `LIBKRB5_CFLAGS` and `LIBKRB5_LIBS` for autotools or set Meson `krb5_name` for Heimdal.

## State and Persistence Behavior

The file has no runtime state. CI state is limited to package installation, generated build directories, generated dist tarballs, and local PATH changes for pip-installed Meson.

## Dependencies and Integration Points

It exercises configure.ac, all Makefile.am files, Meson build files, generated man pages, systemd unit substitution, and optional krb5 feature probes.

## Risks and Edge Cases

The CI provider is legacy and can drift from current toolchain behavior. The pip Meson install and exact krb5-config names are environment-sensitive. Passing distcheck here does not exercise runtime netlink or kernel integration.

## Test Signals

Useful signals are successful `make distcheck` and `meson dist` across all six matrix entries, especially generated tarball contents and Kerberos compile probes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/.travis.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/Makefile.am -->
# sources/user-network-fs/ksmbd-tools/Makefile.am

## Purpose

Top-level autotools packaging file for ksmbd-tools. It wires the addshare, adduser, control, mountd, and tools subdirectories into one distribution and install graph.

## Important APIs, Types, and Functions

Exports `SUBDIRS`, `EXTRA_DIST`, `pkgsysconfdir`, `dist_pkgsysconf_DATA`, `man_MANS`, and `systemdsystemunit_DATA`. It uses the configured `in_script` sed command to generate man pages and the systemd unit from `.in` templates.

## Control Flow

Autotools descends into subdirectories, distributes common include and build metadata, renders `ksmbd.conf.5`, `ksmbdpwd.db.5`, and `ksmbd.service`, then runs install hooks that create runtime/config directories and install a default config if absent.

## State and Persistence Behavior

Install-time state includes `$(runstatedir)`, `$(sysconfdir)/ksmbd`, the default `ksmbd.conf`, and installed generated man/unit files. The uninstall hook removes the installed config to keep distcheck clean.

## Dependencies and Integration Points

Depends on configure.ac substitutions, `ksmbd.conf.example`, template inputs, and all subdirectory Makefile.am files.

## Risks and Edge Cases

The install hook conditionally writes a default config, so packaging scripts must account for conffile ownership. The uninstall hook is distcheck-friendly but can surprise package managers if used outside a packaging context.

## Test Signals

`make distcheck`, install/uninstall into DESTDIR, and verification that generated templates contain correct sbindir, sysconfdir, runstatedir, and version substitutions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/Makefile.am -->
# sources/user-network-fs/ksmbd-tools/addshare/Makefile.am

## Purpose

Build-system description for the `addshare autotools` component in ksmbd-tools.

## Important APIs, Types, and Functions

Defines `libaddshare.a` from `share_admin.c`, `addshare.c`, and `share_admin.h`, installs the generated `ksmbd.addshare.8` man page, and creates an sbindir symlink named `ksmbd.addshare` to the shared `ksmbd.tools` executable.

## Control Flow

Automake builds a noinst static library, renders the man page through `in_script`, then install hooks replace any old symlink and create the new command entry point.

## State and Persistence Behavior

Install state is the generated man page and the symlink. No runtime data is owned here.

## Dependencies and Integration Points

Uses GLib flags, libnl flags through common AM_CFLAGS, top-level include paths, and configure substitutions for sysconfdir and runstatedir.

## Risks and Edge Cases

The CLI is a symlink into a multi-call binary, so symlink target and `set_tool_main` dispatch must agree. Static library source lists must match Meson.

## Test Signals

Autotools build, install into DESTDIR, verify man page generation and that `ksmbd.addshare --help` dispatches correctly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/addshare.c -->
# sources/user-network-fs/ksmbd-tools/addshare/addshare.c

## Purpose

CLI front end for `ksmbd.addshare`. It parses command options, validates a share name, loads current configuration, dispatches add/update/delete behavior, and notifies mountd after successful changes.

## Important APIs, Types, and Functions

Important APIs are `addshare_main`, `usage`, getopt option descriptors, `command_add_share`, `command_update_share`, `command_delete_share`, `load_config`, `cp_parse_lock`, and `kill(..., SIGHUP)`. It uses GLib automatic cleanup and `gptrarray_to_strv` for repeated `-o` options.

## Control Flow

The command loop records a requested operation and option strings, requires exactly one SHARE argument, validates it with `shm_share_name`, defaults paths to `PATH_PWDDB` and `PATH_SMBCONF`, loads users and shares, auto-selects add versus update when no operation is supplied, then calls the selected share-admin command.

## State and Persistence Behavior

Persistent state is the rewritten `ksmbd.conf` performed by share_admin.c. After a successful command it reads the lock file to find mountd and sends SIGHUP unless the lock cannot be parsed.

## Dependencies and Integration Points

Depends on config parsing, tools helpers, management share/user state, kernel share name limits from `ksmbd_server.h`, and the share_admin command contract.

## Risks and Edge Cases

Multiple `-a/-u/-d` flags overwrite the selected command instead of being rejected. SIGHUP failure does not convert a successful config write into a failed exit. The loaded parser state must be removed on every exit path.

## Test Signals

Test with add, update, delete, auto add/update, invalid UTF-8 or too-long names, repeated options, custom config/password paths, absent lock file, and live mountd reload notification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/addshare.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/ksmbd.addshare.8.in -->
# sources/user-network-fs/ksmbd-tools/addshare/ksmbd.addshare.8.in

## Purpose

Manual-page template for `ksmbd.addshare` and its share configuration behavior.

## Important APIs, Types, and Functions

Documents command synopsis, options, default paths, version/help behavior, and related files/utilities. Build systems substitute version, sysconfdir, sbindir, and runstatedir where present.

## Control Flow

The template is transformed into a man page during autotools or Meson builds. It describes the CLI control flow implemented in the matching C file.

## State and Persistence Behavior

No runtime state, but it documents persistent files, lock/fifo paths, kernel sysfs control, or daemon behavior depending on the command.

## Dependencies and Integration Points

Integrated with build template substitution and the matching CLI source.

## Risks and Edge Cases

The man page can drift from getopt options, default limits, and runtime behavior. Generated paths must match compile-time macros.

## Test Signals

Tests should compare documented options with getopt tables and verify generated man-page substitution in both build systems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/ksmbd.addshare.8.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/meson.build -->
# sources/user-network-fs/ksmbd-tools/addshare/meson.build

## Purpose

Build-system description for the `addshare Meson` component in ksmbd-tools.

## Important APIs, Types, and Functions

Creates static library `addshare`, compiles `share_admin.c`, `addshare.c`, and header, renders `ksmbd.addshare.8`, and installs the command symlink to the shared libexec binary.

## Control Flow

Meson applies component path defines, links against GLib, configures the man page from `in_data`, and installs the symlink.

## State and Persistence Behavior

Build-tree static library and generated man page; install-tree man page and symlink.

## Dependencies and Integration Points

Consumes top-level `include_dirs`, `glib_dep`, `runstatedir`, and `in_data`.

## Risks and Edge Cases

Path expression behavior depends on Meson option values. Build parity with Makefile.am is required.

## Test Signals

Meson compile, install into DESTDIR, and compare generated command/man artifacts with autotools.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/share_admin.c -->
# sources/user-network-fs/ksmbd-tools/addshare/share_admin.c

## Purpose

Implements the share database mutation engine behind `ksmbd.addshare`. It can prompt interactively for share parameters, complete users/groups/paths, merge command-line `key=value` options, rewrite `ksmbd.conf`, and handle special global-section deletion semantics.

## Important APIs, Types, and Functions

Important functions include `command_add_share`, `command_update_share`, `command_delete_share`, `process_options`, `__prompt_options_stdin`, `new_conf_ml`, `get_conf_contents`, `new_share_nl`, `new_share_kl`, and `__gptrarray_add_share_kl`. It is driven by the `KSMBD_SHARE_CONF` enum and default strings from management/share.h.

## Control Flow

For add/update, options are either supplied by `-o` or generated from existing/default config and edited in raw terminal mode. The selected options are parsed through `cp_parse_external_smbconf_group`, then the whole parser group table is serialized in deterministic-ish share/key order and written with `set_conf_contents`. Delete removes the group, except deleting `global` rewrites global values to defaults.

## State and Persistence Behavior

Persistent state is the full `ksmbd.conf` contents; original formatting and comments are intentionally not preserved except generated comments/default markers. Interactive state includes raw terminal settings and completion lists that are cleared as input changes.

## Dependencies and Integration Points

Depends on GLib arrays/lists/hash tables, passwd/group enumeration, directory reads for path completion, config parser helpers, user/share managers, global root_dir, and kernel share limits.

## Risks and Edge Cases

The raw terminal prompt must restore termios on all exits. Completion and path lookup can observe local system users/groups/directories. Rewriting the full config is simple but can drop manual formatting. The `__defconf_fmt` table must stay 1:1 with `KSMBD_SHARE_CONF`.

## Test Signals

Tests should cover noninteractive `-o` writes, prompt navigation/editing/completion, global section updates, global delete reset, duplicate share rejection, unavailable destination writes, and parse/reload of the generated config.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/share_admin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/share_admin.h -->
# sources/user-network-fs/ksmbd-tools/addshare/share_admin.h

## Purpose

Small public header for addshare command implementations.

## Important APIs, Types, and Functions

Defines `command_fn` as `int(char *smbconf, char *name, char **options)` and declares `command_add_share`, `command_update_share`, and `command_delete_share`.

## Control Flow

`addshare.c` selects one command and transfers ownership of path/name/options to it. The implementation frees those inputs on exit.

## State and Persistence Behavior

No direct persistence. The declared functions persist by rewriting `ksmbd.conf`.

## Dependencies and Integration Points

Included by addshare.c and share_admin.c.

## Risks and Edge Cases

The ownership convention is implicit; future callers must not reuse arguments after command invocation.

## Test Signals

Compile coverage plus CLI add/update/delete tests validate the contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/addshare/share_admin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/Makefile.am -->
# sources/user-network-fs/ksmbd-tools/adduser/Makefile.am

## Purpose

Build-system description for the `adduser autotools` component in ksmbd-tools.

## Important APIs, Types, and Functions

Defines `libadduser.a` from password hashing, user administration, CLI, and headers; renders `ksmbd.adduser.8`; installs `ksmbd.adduser` as a symlink to `ksmbd.tools`.

## Control Flow

Builds the static library and generated man page, then uses install/uninstall hooks to keep the command symlink current.

## State and Persistence Behavior

Install state is the man page and symlink. Password database state is handled by runtime code, not the build file.

## Dependencies and Integration Points

Depends on GLib, libnl flags, common includes, generated config macros, and source parity with Meson.

## Risks and Edge Cases

The MD4 and password-database source files must stay included in both build systems. Symlink dispatch can fail if the shared binary is not installed.

## Test Signals

Autotools compile, distcheck, DESTDIR install, and CLI smoke tests for `--help` and `--version`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/adduser.c -->
# sources/user-network-fs/ksmbd-tools/adduser/adduser.c

## Purpose

CLI front end for `ksmbd.adduser`. It parses user-management options, validates the account name, loads config and password database state, dispatches add/update/delete, and notifies mountd.

## Important APIs, Types, and Functions

Important APIs are `adduser_main`, `usage`, getopt descriptors, `command_add_user`, `command_update_user`, `command_delete_user`, `usm_user_name`, `load_config`, `cp_parse_lock`, and SIGHUP notification.

## Control Flow

The parser records the last requested operation, optional password, and custom pwddb/config paths. It requires exactly one USER, validates UTF-8/name rules, loads config, auto-selects add/update by `usm_lookup_user`, calls user_admin.c, then signals mountd if a lock file is available.

## State and Persistence Behavior

Persistent state is the rewritten `ksmbdpwd.db`; config is loaded to enforce delete safety against shares requiring a user.

## Dependencies and Integration Points

Depends on tools, config_parser, management/user, management/share, user_admin.h, and kernel account-name limits.

## Risks and Edge Cases

Operation flags override each other rather than being mutually exclusive errors. A successful database write can still return success if mountd notification fails. Password supplied on the command line is visible to process listings.

## Test Signals

Test add/update/delete/auto behavior, invalid names, colon rejection, empty password handling, custom database paths, user deletion when referenced by shares, and reload notification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/adduser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/ksmbd.adduser.8.in -->
# sources/user-network-fs/ksmbd-tools/adduser/ksmbd.adduser.8.in

## Purpose

Manual-page template for `ksmbd.adduser` and its user/password database configuration behavior.

## Important APIs, Types, and Functions

Documents command synopsis, options, default paths, version/help behavior, and related files/utilities. Build systems substitute version, sysconfdir, sbindir, and runstatedir where present.

## Control Flow

The template is transformed into a man page during autotools or Meson builds. It describes the CLI control flow implemented in the matching C file.

## State and Persistence Behavior

No runtime state, but it documents persistent files, lock/fifo paths, kernel sysfs control, or daemon behavior depending on the command.

## Dependencies and Integration Points

Integrated with build template substitution and the matching CLI source.

## Risks and Edge Cases

The man page can drift from getopt options, default limits, and runtime behavior. Generated paths must match compile-time macros.

## Test Signals

Tests should compare documented options with getopt tables and verify generated man-page substitution in both build systems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/ksmbd.adduser.8.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/md4_hash.c -->
# sources/user-network-fs/ksmbd-tools/adduser/md4_hash.c

## Purpose

Standalone MD4 implementation used to produce SMB NT password hashes after UTF-16LE password conversion.

## Important APIs, Types, and Functions

Exports `md4_init`, `md4_update`, and `md4_final` declared in md4_hash.h. Internal helpers implement the three MD4 rounds, little-endian block conversion, padding, and final digest extraction.

## Control Flow

`md4_update` accumulates bytes into 64-byte blocks, transforms full blocks, and keeps a byte counter. `md4_final` appends MD4 padding and bit length, performs the final transform, writes the little-endian 16-byte digest, and zeroes the context.

## State and Persistence Behavior

State is only `struct md4_ctx`: four hash words, a 16-word block, and byte count. No heap or file state is used.

## Dependencies and Integration Points

Depends on memory functions, asm byteorder helpers, and md4_hash.h.

## Risks and Edge Cases

MD4 is cryptographically broken but required for NT hash compatibility. The code assumes platform integer sizes matching the typedef macros. It is sensitive to endian helper availability.

## Test Signals

Test with RFC1320 MD4 vectors and known NTLM hash vectors after UTF-16LE conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/md4_hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/md4_hash.h -->
# sources/user-network-fs/ksmbd-tools/adduser/md4_hash.h

## Purpose

Declares the MD4 context and API used by user password hashing.

## Important APIs, Types, and Functions

Defines `MD4_BLOCK_WORDS`, `MD4_HASH_WORDS`, `struct md4_ctx`, and functions `md4_init`, `md4_update`, and `md4_final`.

## Control Flow

Callers initialize the context, feed arbitrary byte chunks, and finalize into a 16-byte digest.

## State and Persistence Behavior

The context is caller-owned transient memory and is zeroed by finalization.

## Dependencies and Integration Points

Used by user_admin.c and implemented by md4_hash.c.

## Risks and Edge Cases

Callers must provide a sufficiently large output buffer and must not reuse a finalized context without reinitialization.

## Test Signals

Compile tests and known digest vectors cover the declaration contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/md4_hash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/meson.build -->
# sources/user-network-fs/ksmbd-tools/adduser/meson.build

## Purpose

Build-system description for the `adduser Meson` component in ksmbd-tools.

## Important APIs, Types, and Functions

Creates static library `adduser` from MD4, user admin, CLI, and headers; renders `ksmbd.adduser.8`; installs the `ksmbd.adduser` symlink.

## Control Flow

Applies compile-time sysconfdir/runstatedir defines, depends on GLib, configures the man page, and creates a symlink to `ksmbd.tools`.

## State and Persistence Behavior

Build outputs are the static library and man page; install outputs are the man page and symlink.

## Dependencies and Integration Points

Uses top-level include dirs, GLib dependency, in_data, and runstatedir.

## Risks and Edge Cases

The password hashing file must remain in the library. Meson and automake source lists must not diverge.

## Test Signals

Meson compile/dist and CLI smoke tests for password command dispatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/user_admin.c -->
# sources/user-network-fs/ksmbd-tools/adduser/user_admin.c

## Purpose

Implements user database mutation for `ksmbd.adduser`. It prompts for passwords, derives NT hashes, serializes users, and prevents deleting users still required by global or share configuration.

## Important APIs, Types, and Functions

Important functions include `command_add_user`, `command_update_user`, `command_delete_user`, `process_password`, `__prompt_password_stdin`, `__utf16le_convert`, `__md4_hash`, `__base64_encode`, `get_conf_contents`, and `__is_transient_user`.

## Control Flow

Add checks for duplicates, obtains a password, converts UTF-8 to UTF-16LE, MD4-hashes it, Base64-encodes the 16-byte hash, adds the user to the user manager, and rewrites pwddb. Update replaces an existing password. Delete first scans global guest and share user maps to ensure the account is transient.

## State and Persistence Behavior

Persistent state is the full `ksmbdpwd.db` file, serialized as sorted non-guest `name:hash` lines. Interactive state is raw terminal password entry with confirmation and UTF-8 validation.

## Dependencies and Integration Points

Depends on GLib, termios, config parser printable checks, tools charset/base64 helpers, MD4 implementation, management/user and share maps.

## Risks and Edge Cases

The password prompt must restore terminal echo/canonical mode. The command-line password path can leak secrets. MD4 is required for NT hash compatibility but is not a general-purpose secure hash. `get_conf_contents` rewrites the whole database.

## Test Signals

Tests should cover known NT hash vectors, prompt mismatch and invalid UTF-8, empty and max-length passwords, add/update/delete persistence, and deletion refusal for guest or share-referenced users.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/user_admin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/user_admin.h -->
# sources/user-network-fs/ksmbd-tools/adduser/user_admin.h

## Purpose

Public command header for adduser operations.

## Important APIs, Types, and Functions

Defines `MAX_NT_PWD_LEN` as 129 and declares `command_fn` plus add, update, and delete command functions.

## Control Flow

The CLI selects a command and transfers ownership of pwddb/name/password strings to the implementation.

## State and Persistence Behavior

No direct persistence; declared commands rewrite `ksmbdpwd.db`.

## Dependencies and Integration Points

Included by adduser.c and user_admin.c.

## Risks and Edge Cases

Ownership semantics are implicit and should be documented if reused.

## Test Signals

Validated by compile coverage and adduser CLI behavior tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/adduser/user_admin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/autogen.sh -->
# sources/user-network-fs/ksmbd-tools/autogen.sh

## Purpose

Minimal bootstrap script for the autotools build.

## Important APIs, Types, and Functions

Runs `autoreconf --install --verbose`.

## Control Flow

There is no branching. The script delegates macro discovery, auxiliary file installation, and generated configure script creation to autoreconf.

## State and Persistence Behavior

Creates or updates generated autotools files such as configure, aclocal output, build-aux helpers, and Makefile.in files.

## Dependencies and Integration Points

Requires autoconf, automake, libtoolize support, and m4 macros referenced by configure.ac.

## Risks and Edge Cases

It does not set `set -e`; failures depend on shell exit behavior of the single command. Generated files may vary across autotools versions.

## Test Signals

Run from a clean checkout, then run `./configure` and `make distcheck`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/autogen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/configure.ac -->
# sources/user-network-fs/ksmbd-tools/configure.ac

## Purpose

Autoconf entry point for ksmbd-tools. It discovers compiler, dependency, installation, runtime-directory, systemd, pthread, GLib, libnl, and optional Kerberos capabilities.

## Important APIs, Types, and Functions

Defines project metadata from `include/version.h`, substitutes `ksmbd_tools_version`, `in_script`, `runstatedir`, `systemdsystemunitdir`, and `PTHREAD_LIBS`, and emits `config.h`. Important options are `--enable-krb5`, `--with-rundir`, and `--with-systemdsystemunitdir`.

## Control Flow

After base tool checks it resolves krb5 only when enabled, probes krb5 headers and ABI differences, requires GLib and libnl/libnl-genl, finds pthread support, and configures Makefiles for root, addshare, adduser, control, mountd, and tools.

## State and Persistence Behavior

Persists feature results as config.h macros such as `CONFIG_KRB5`, `HAVE_KRB5_AUTH_CON_GETRECVSUBKEY`, `HAVE_KRB5_KEYBLOCK_KEYVALUE`, `HAVE_KRB5_AUTHENTICATOR_CLIENT`, and `HAVE_KRB5_AUTH_CON_GETAUTHENTICATOR_DOUBLE_POINTER`.

## Dependencies and Integration Points

Consumes pkg-config modules `glib-2.0`, `libnl-3.0`, `libnl-genl-3.0`, optional `krb5`, optional systemd, and m4/autotools macros.

## Risks and Edge Cases

Kerberos support is off by default, and optional mode can silently disable support if headers are missing. ABI probes must stay aligned with both MIT and Heimdal. `runstatedir` fallback behavior affects lock and fifo paths.

## Test Signals

Configure and distcheck with krb5 disabled, MIT krb5 enabled, and Heimdal krb5 enabled. Inspect config.h and generated template substitutions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/control/Makefile.am -->
# sources/user-network-fs/ksmbd-tools/control/Makefile.am

## Purpose

Build-system description for the `control autotools` component in ksmbd-tools.

## Important APIs, Types, and Functions

Defines `libcontrol.a` from `control.c`, renders `ksmbd.control.8`, and installs an sbindir symlink to `ksmbd.tools`.

## Control Flow

The library is linked into the multi-call tool; the generated man page and symlink are installed by standard automake targets plus hooks.

## State and Persistence Behavior

Install state is symlink and man page only.

## Dependencies and Integration Points

Uses configured sysconfdir/runstatedir defines and GLib/libnl/common include flags.

## Risks and Edge Cases

control.c uses sysfs and runstatedir paths at runtime, so build-time substitutions must match installed service paths.

## Test Signals

Autotools build and install smoke test; `ksmbd.control --help` should work without kernel support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/control/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/control/control.c -->
# sources/user-network-fs/ksmbd-tools/control/control.c

## Purpose

Implements `ksmbd.control`, an administrative CLI for shutting down, reloading, listing shares, toggling kernel debug components, and printing the kernel module version.

## Important APIs, Types, and Functions

Important functions are `control_main`, `control_shutdown`, `control_reload`, `control_list`, `control_show_version`, and `control_debug`. It uses `/sys/class/ksmbd-control/kill_server`, `/sys/class/ksmbd-control/debug`, `/sys/module/ksmbd/version`, `PATH_FIFO`, and `PATH_LOCK`.

## Control Flow

The CLI dispatches immediately on the first action option. Shutdown SIGTERMs mountd via the parsed lock and writes `hard` to the kernel control attribute. Reload sends SIGHUP. List creates a per-client FIFO, asks mountd with SIGUSR1, blocks for SIGIO, and splices FIFO data to stdout. Debug writes a component string then reads back active components.

## State and Persistence Behavior

Runtime state includes sysfs control attributes, the mountd lock file, and transient `ksmbd.fifo.<pid>` FIFOs. No config files are modified.

## Dependencies and Integration Points

Depends on config_parser lock parsing, tools logging/version helpers, pthread signal masks, fcntl async I/O, sysfs ksmbd control, and mountd's SIGUSR1 list protocol.

## Risks and Edge Cases

Sysfs files may not support lseek on all kernels; version/debug paths assume seekable attributes. The FIFO protocol depends on signal delivery and cleanup on interrupt. Action options are mutually exclusive by first match rather than validation.

## Test Signals

Tests include help/version without kernel support, reload with fake lock, FIFO list integration with mountd, shutdown/debug/version on a system with the kernel module, and cleanup of FIFOs on failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/control/control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/control/ksmbd.control.8.in -->
# sources/user-network-fs/ksmbd-tools/control/ksmbd.control.8.in

## Purpose

Manual-page template for `ksmbd.control` and its runtime control of mountd and kernel ksmbd behavior.

## Important APIs, Types, and Functions

Documents command synopsis, options, default paths, version/help behavior, and related files/utilities. Build systems substitute version, sysconfdir, sbindir, and runstatedir where present.

## Control Flow

The template is transformed into a man page during autotools or Meson builds. It describes the CLI control flow implemented in the matching C file.

## State and Persistence Behavior

No runtime state, but it documents persistent files, lock/fifo paths, kernel sysfs control, or daemon behavior depending on the command.

## Dependencies and Integration Points

Integrated with build template substitution and the matching CLI source.

## Risks and Edge Cases

The man page can drift from getopt options, default limits, and runtime behavior. Generated paths must match compile-time macros.

## Test Signals

Tests should compare documented options with getopt tables and verify generated man-page substitution in both build systems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/control/ksmbd.control.8.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/control/meson.build -->
# sources/user-network-fs/ksmbd-tools/control/meson.build

## Purpose

Build-system description for the `control Meson` component in ksmbd-tools.

## Important APIs, Types, and Functions

Creates static library `control` from `control.c`, renders `ksmbd.control.8`, and installs the control symlink.

## Control Flow

Configures compile-time path defines, builds against GLib, configures the man page, then installs a symlink to libexec `ksmbd.tools`.

## State and Persistence Behavior

Static library in build tree and man/symlink in install tree.

## Dependencies and Integration Points

Top-level include dirs, GLib, in_data, and runstatedir.

## Risks and Edge Cases

Runtime sysfs control paths are fixed in C; build only controls config/run paths. Symlink install target must match where tools subdir installs `ksmbd.tools`.

## Test Signals

Meson compile and install smoke test of the symlink.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/control/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/asn1.h -->
# sources/user-network-fs/ksmbd-tools/include/asn1.h

## Purpose

Declares a compact ASN.1 DER/BER decoder and encoder surface used by SPNEGO/Kerberos negotiation code.

## Important APIs, Types, and Functions

Defines ASN.1 classes, tags, primitive/constructed flags, error codes, well-known OID arrays for SPNEGO, NTLMSSP, KRB5, KRB5U2U, and MSKRB5, `struct asn1_ctx`, `struct asn1_octstr`, and read/write helpers such as `asn1_open`, `asn1_header_decode`, `asn1_oid_decode`, `asn1_header_encode`, and `asn1_oid_encode`.

## Control Flow

Callers initialize a context over a buffer, decode headers to get class/constructed/tag/end-of-content, read octets or OIDs, and use encoder helpers to construct headers and OID payloads.

## State and Persistence Behavior

State is cursor-based in `asn1_ctx`: begin, end, pointer, and error. The OID arrays are header-level static data in each translation unit that includes the header.

## Dependencies and Integration Points

Integrated with management/spnego and optional Kerberos support; depends only on basic C types.

## Risks and Edge Cases

The header defines non-const static OID arrays, which creates per-translation-unit copies and permits accidental mutation. Length and EOC handling are security-sensitive for untrusted negotiation blobs.

## Test Signals

Tests should cover DER header lengths, invalid lengths, OID round trips for all declared mechanisms, empty/truncated buffers, and nested constructed values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/asn1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/config_parser.h -->
# sources/user-network-fs/ksmbd-tools/include/config_parser.h

## Purpose

Public interface for parsing ksmbd configuration, password database, subauth, and lock files.

## Important APIs, Types, and Functions

Defines `struct smbconf_group`, global `struct smbconf_parser parser`, inline helpers `cp_printable`, `cp_smbconf_eol`, `cp_pwddb_eol`, parser lifecycle functions, file parsers, key/value conversion helpers, list parsing/freeing, and `cp_group_kv_steal`.

## Control Flow

Runtime code initializes parser state, parses `ksmbd.conf` and `ksmbdpwd.db`, transforms string values into booleans, numbers, config options, and lists, then destroys state through remove_config or parser-specific cleanup.

## State and Persistence Behavior

Parser state is global and mutable: hash-table groups plus current/global/ipc pointers. It also reads lock/subauth files and exposes derived configuration to management modules.

## Dependencies and Integration Points

Used by all CLIs, mountd startup/reload, addshare/adduser mutation paths, and tools load/remove helpers.

## Risks and Edge Cases

Global parser state makes reentrancy and reload ordering important. Key comparison is case/space normalized in implementation, so callers should use helper APIs rather than raw hash behavior.

## Test Signals

Tests should parse comments, duplicate groups/keys, empty values, list separators, numeric suffixes, invalid lock files, and load/remove cycles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/config_parser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/ipc.h -->
# sources/user-network-fs/ksmbd-tools/include/ipc.h

## Purpose

Declares the userspace side of the ksmbd generic-netlink IPC channel.

## Important APIs, Types, and Functions

Defines IPC message size/buffer constants, `struct ksmbd_ipc_msg`, payload macro `KSMBD_IPC_MSG_PAYLOAD`, allocation/free/send functions, event processing, and init/destroy lifecycle.

## Control Flow

mountd initializes netlink, sends startup config, waits for kernel events, wraps received payloads as `ksmbd_ipc_msg`, pushes them to worker handling, and sends responses back through `ipc_msg_send`.

## State and Persistence Behavior

IPC state is owned by mountd/ipc.c: a netlink socket and queued heap messages. Message payloads are size-limited to 16 KiB for kernel compatibility.

## Dependencies and Integration Points

Depends on `linux/ksmbd_server.h` ABI structures and mountd worker processing.

## Risks and Edge Cases

Message size limits and payload struct layout must match kernel expectations. Callers own allocated messages and must free after send or processing.

## Test Signals

Tests need netlink integration with a matching kernel module plus allocation boundary tests for oversize messages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/linux/ksmbd_server.h -->
# sources/user-network-fs/ksmbd-tools/include/linux/ksmbd_server.h

## Purpose

Userspace copy of the ksmbd kernel IPC ABI. It defines generic-netlink family metadata, request/response payload structures, event IDs, flags, and RPC status codes shared between mountd and the kernel module.

## Important APIs, Types, and Functions

Important structures include startup/shutdown, login, share config, tree connect/disconnect, logout, RPC, and SPNEGO request/response messages. Important enums/macros cover `ksmbd_event`, tree connection statuses, user/share/global flags, RPC method flags, RPC error/status codes, and config option values.

## Control Flow

mountd fills startup requests from global configuration, receives typed kernel requests, dispatches them to user/share/session/tree/RPC/SPNEGO handlers, and replies with the matching event type. The header notes that response event values must equal request value plus one.

## State and Persistence Behavior

No direct state, but every structure represents serialized state across netlink. Many structures are packed or include flexible payload tails whose size fields control parsing.

## Dependencies and Integration Points

Used by ipc.c, management modules, addshare/adduser validation limits, RPC service code, and kernel-side ksmbd.

## Risks and Edge Cases

ABI drift is the central risk: field order, sizes, event numbering, and flags must stay synchronized with the kernel. Flexible payload offsets and fixed name/hash limits are easy boundary-error sites.

## Test Signals

Tests should pair a userspace build with kernel IPC tests for each event, verify response event numbering, and fuzz short/oversized payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/linux/ksmbd_server.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/session.h -->
# sources/user-network-fs/ksmbd-tools/include/management/session.h

## Purpose

Declares session-management state for users connected to ksmbd shares.

## Important APIs, Types, and Functions

Defines `struct ksmbd_session` with session id, user pointer, update lock, tree connection list, and ref counter. Exposes capacity checking, tree connect/disconnect handlers, and init/destroy.

## Control Flow

The implementation tracks sessions, enforces `global_conf.sessions_cap`, associates tree connections with users, and removes tree connections on disconnect or logout paths.

## State and Persistence Behavior

State is an in-memory session table with referenced users and child tree connections. It is not persisted across mountd restart.

## Dependencies and Integration Points

Integrated with tree_conn management and kernel tree connect/disconnect IPC events.

## Risks and Edge Cases

Reference counts and lock ordering must prevent stale user/tree pointers. Capacity handling affects denial of new sessions.

## Test Signals

Tests should connect multiple sessions, enforce max active sessions, disconnect tree connections, and verify cleanup on user logout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/session.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/share.h -->
# sources/user-network-fs/ksmbd-tools/include/management/share.h

## Purpose

Declares the share-management model and configuration keys for ksmbd shares.

## Important APIs, Types, and Functions

Defines `struct ksmbd_share`, user/host map enums, `KSMBD_SHARE_CONF` key enum, key/default arrays, helpers for global/broken config entries, flag helpers, lookup/refcount APIs, connection accounting, map lookups, iteration, and share-config response serialization.

## Control Flow

Config parsing creates shares from smbconf groups; mountd looks up shares for share-config and tree-connect requests; addshare uses the enum/default arrays to prompt and rewrite configuration.

## State and Persistence Behavior

State is an in-memory share table containing path, masks, force uid/gid, flags, veto list, guest account, user maps, host maps, comments, locks, reference counts, and connection counts. Persistence is via `ksmbd.conf` rewritten by addshare.

## Dependencies and Integration Points

Depends on GLib hash tables/locks and kernel response structures from ksmbd_server.h.

## Risks and Edge Cases

The enum order is an ABI-like contract for addshare descriptions and defaults. Host matching is noted as simplistic. Refcount and map-lock discipline are critical under concurrent worker processing.

## Test Signals

Tests should parse all share keys, validate name hashing/equality, map users/groups, enforce hosts allow/deny, open/close connection limits, and serialize share config payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/share.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/spnego.h -->
# sources/user-network-fs/ksmbd-tools/include/management/spnego.h

## Purpose

Declares SPNEGO authentication handling for mountd.

## Important APIs, Types, and Functions

Exposes `spnego_handle_authen_request(struct ksmbd_spnego_authen_request *, struct ksmbd_spnego_authen_response *)`.

## Control Flow

The implementation consumes a kernel SPNEGO auth request, negotiates NTLM/Kerberos mechanisms as configured, and fills a combined login/SPNEGO response.

## State and Persistence Behavior

State is request/response payload memory plus any implementation-side Kerberos context; no persistence is declared here.

## Dependencies and Integration Points

Depends on `linux/ksmbd_server.h`, ASN.1 helpers, user management, and optional Kerberos config macros.

## Risks and Edge Cases

Authentication blob parsing is security-sensitive and must reject malformed ASN.1/mechanism tokens. Optional Kerberos support changes behavior at compile time.

## Test Signals

Tests need NTLM/SPNEGO negotiation vectors, Kerberos-enabled and disabled builds, malformed blobs, and response size bounds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/spnego.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/tree_conn.h -->
# sources/user-network-fs/ksmbd-tools/include/management/tree_conn.h

## Purpose

Declares tree-connection state for a connected user/share pair.

## Important APIs, Types, and Functions

Defines `struct ksmbd_tree_conn` with id, share pointer, and flags; flag helpers; and handlers for tree connect/disconnect requests.

## Control Flow

A tree-connect request resolves user/share policy, creates a connection object, attaches it to a session, and fills kernel response flags/status. Disconnect releases the share connection.

## State and Persistence Behavior

State is in-memory and linked from sessions. It references shares and carries connection flags such as guest, read-only, writable, admin, and update.

## Dependencies and Integration Points

Depends on management/share, management/user/session implementation, and kernel tree connection ABI.

## Risks and Edge Cases

Correct release on disconnect matters for share connection limits. Flag computation must match share/user policy.

## Test Signals

Tests should cover allowed/denied users, guest access, read/write flags, admin users, too-many-connections, and disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/tree_conn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/user.h -->
# sources/user-network-fs/ksmbd-tools/include/management/user.h

## Purpose

Declares the user-management model and login/logout handlers for mountd.

## Important APIs, Types, and Functions

Defines `struct ksmbd_user` with name, Base64 password hash, decoded hash, uid/gid, flags, state, locks, failed login count, and supplementary groups. Exposes lookup, refcount, add/remove/update, guest-account addition, iteration, and login/logout IPC handlers.

## Control Flow

Config loading populates the user table from pwddb and system passwd/group lookups. Login requests compare account state and password hash, map to uid/gid/groups, and logout updates session/account state.

## State and Persistence Behavior

State is in-memory user records plus persisted `ksmbdpwd.db` for non-guest accounts. Guest accounts and supplementary groups are derived at load time.

## Dependencies and Integration Points

Used by adduser, share policy, session/tree connect, RPC account lookup, and SPNEGO/login handlers.

## Risks and Edge Cases

Password hash storage and decoding must respect kernel hash-size limits. Refcounts and locks protect concurrent IPC handling. Deleting users while shares reference them is guarded by adduser but runtime reload ordering remains important.

## Test Signals

Tests should cover user name validation, guest account creation, hash decode, login success/failure flags, supplementary groups, failed counts, and reload replacement.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/management/user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc.h -->
# sources/user-network-fs/ksmbd-tools/include/rpc.h

## Purpose

Core declaration surface for ksmbd's lightweight DCE/RPC and NDR implementation used by IPC named-pipe services.

## Important APIs, Types, and Functions

Defines DCE/RPC flags, packet types, fragment flags, serialization constants, headers, NDR pointer/string wrappers, request structs for SRVSVC/WKSSVC/SAMR/LSARPC, syntax/context structures, `ksmbd_dcerpc`, `ksmbd_rpc_pipe`, NDR read/write helpers, pipe reset, RPC init/destroy, and open/write/read/ioctl/close entry points.

## Control Flow

Kernel RPC IPC calls open a pipe, write a request payload, parse DCE/RPC headers and service-specific arguments, later read a response payload, and close the pipe. Service implementations install entry callbacks for array serialization.

## State and Persistence Behavior

State is per-pipe: DCE payload cursor, request/response pointers, decoded headers, service request unions, pending entries, processed counters, and callback pointers. A global pipe table is maintained in rpc.c.

## Dependencies and Integration Points

Integrated with kernel `ksmbd_rpc_command` ABI, GLib arrays/tables, SRVSVC/WKSSVC/SAMR/LSARPC service files, and smbacl helpers.

## Risks and Edge Cases

The parser is intentionally partial and pointer/offset heavy. Fragmentation, endian flags, fixed payload limits, and service callback contracts are high-risk. Pipe and handle tables must be cleaned on close/destroy.

## Test Signals

Tests should exercise bind/alt-context negotiation, endian conversion, string conversion, fixed-buffer overflow, multi-part array responses, unknown opnums, and pipe lifecycle.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc_lsarpc.h -->
# sources/user-network-fs/ksmbd-tools/include/rpc_lsarpc.h

## Purpose

Declares LSARPC service support for domain/account lookup over DCE/RPC.

## Important APIs, Types, and Functions

Defines handle sizes, domain string size, `struct policy_handle`, `struct lsarpc_names_info`, read/write request handlers, and init/destroy lifecycle.

## Control Flow

rpc.c dispatches LSARPC write/read phases into this service. The implementation tracks policy handles and converts SIDs and account names into NDR responses.

## State and Persistence Behavior

State includes an LSARPC policy-handle table, per-request lookup entries, and a cached uppercase host-derived domain name.

## Dependencies and Integration Points

Depends on smbacl SID structures, user management, generic RPC helpers, and GLib tables.

## Risks and Edge Cases

Handle identity uses binary handles stored in GLib hash tables, so hash/equality semantics must match handle memory. SID/name mapping returns partial success for unmapped identities.

## Test Signals

Tests should open/query/close policies, lookup known and unknown SIDs/names, and verify handle cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc_lsarpc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc_samr.h -->
# sources/user-network-fs/ksmbd-tools/include/rpc_samr.h

## Purpose

Declares SAMR service support for account/domain management queries over DCE/RPC.

## Important APIs, Types, and Functions

Defines `struct connect_handle` with a 20-byte handle, refcount, and associated user; declares SAMR read/write handlers and init/destroy.

## Control Flow

rpc.c dispatches SAMR write/read phases. The implementation tracks connect/domain/user handles, domain entries, user lookups, user-info responses, group membership, and security descriptors.

## State and Persistence Behavior

State includes a SAMR connect-handle table, refcounts, optional user pointer, domain entries, and cached uppercase domain name.

## Dependencies and Integration Points

Depends on smbacl, user management, generic RPC helpers, and GLib.

## Risks and Edge Cases

Handle refcounts must match open/close call sequences. User pointers must remain valid across reloads or be released correctly by implementation.

## Test Signals

Tests should cover connect, enum/lookup/open domain, lookup/open user, query user info, query security, group membership, alias membership, close, and bad handles.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc_samr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc_srvsvc.h -->
# sources/user-network-fs/ksmbd-tools/include/rpc_srvsvc.h

## Purpose

Declares SRVSVC service entry points for share enumeration and share info RPCs.

## Important APIs, Types, and Functions

Exposes `rpc_srvsvc_read_request` and `rpc_srvsvc_write_request` over `ksmbd_rpc_pipe` and `ksmbd_rpc_command`.

## Control Flow

Generic RPC dispatch calls write to parse and collect share entries, then read to serialize DCE/RPC response data.

## State and Persistence Behavior

State is kept in the shared RPC pipe entries and decoded SRVSVC request in `ksmbd_dcerpc`.

## Dependencies and Integration Points

Depends on rpc.h and share management implementation.

## Risks and Edge Cases

Unsupported levels/opnums and restricted anonymous context must map to correct RPC status codes.

## Test Signals

Tests should enumerate shares at levels 0/1, get info for allowed/denied/missing shares, and enforce restricted context behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc_srvsvc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc_wkssvc.h -->
# sources/user-network-fs/ksmbd-tools/include/rpc_wkssvc.h

## Purpose

Declares WKSSVC workstation information service entry points.

## Important APIs, Types, and Functions

Exposes `rpc_wkssvc_read_request` and `rpc_wkssvc_write_request`.

## Control Flow

Generic RPC write parses NetWkstaGetInfo arguments; read serializes level 100 workstation info.

## State and Persistence Behavior

State lives in `ksmbd_dcerpc.wi_req` during one request.

## Dependencies and Integration Points

Depends on rpc.h and global workgroup/server configuration.

## Risks and Edge Cases

Only level 100 is implemented; other levels must return invalid-level errors.

## Test Signals

Tests should request level 100, unknown levels, restricted anonymous context, and malformed server-name strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/rpc_wkssvc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/smbacl.h -->
# sources/user-network-fs/ksmbd-tools/include/smbacl.h

## Purpose

Declares SMB SID, ACL, ACE, and security descriptor helpers used by SAMR/LSARPC responses.

## Important APIs, Types, and Functions

Defines constants for SID authorities, ACE types, descriptor flags, SID type values, `struct smb_ntsd`, `struct smb_sid`, `struct smb_acl`, `struct smb_ace`, and helpers to read/write/copy/compare SIDs, initialize domain SIDs, build security descriptors, and resolve domain names.

## Control Flow

Service code uses these helpers to parse incoming SIDs, emit domain/user SIDs, and build self-relative security descriptors with DACLs.

## State and Persistence Behavior

No persistent state in the header. Implementations derive domain SID subauthorities from global configuration.

## Dependencies and Integration Points

Depends on linux types, GLib, rpc.h NDR helpers, and LSARPC domain constants.

## Risks and Edge Cases

SID subauthority bounds and descriptor size accounting are security-sensitive. Callers must supply valid DCE/RPC cursors and output buffers.

## Test Signals

Tests should read/write SIDs, compare SIDs, initialize domain SID from subauth, map known/unknown domains, and validate generated security descriptor layout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/smbacl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/tools.h -->
# sources/user-network-fs/ksmbd-tools/include/tools.h

## Purpose

Common utility header for the ksmbd-tools multi-call binary, logging, paths, global configuration, charset conversion, Base64, config load/remove, and GLib hash iteration helpers.

## Important APIs, Types, and Functions

Defines `struct smbconf_global`, path constants, health flags, logging levels/macros, charset enum, tool dispatch declarations, helper functions such as `base64_encode`, `ksmbd_gconvert`, `set_conf_contents`, `load_config`, `remove_config`, `show_version`, and hash iteration macros.

## Control Flow

All CLIs use tool dispatch and logging; config load populates `global_conf`, parser, users, and shares; mountd uses health flags to reload/list/stop; adduser/addshare use string-array and config-write helpers.

## State and Persistence Behavior

Global state includes `global_conf`, `ksmbd_health_status`, `log_level`, and `tool_main`. Persistence is through `set_conf_contents` and the config/password files.

## Dependencies and Integration Points

Depends on GLib, POSIX process/signal I/O, generated config.h, and all component main functions.

## Risks and Edge Cases

Global mutable state limits reentrancy. Compile-time `SYSCONFDIR` and `RUNSTATEDIR` must match packaging/service files. Logging macros inject tool name and pid into every message.

## Test Signals

Tests should cover multi-call dispatch by argv name/symlink, config load/remove cycles, Base64 round trips, charset conversion, config atomic write behavior, and logging level filtering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/tools.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/version.h -->
# sources/user-network-fs/ksmbd-tools/include/version.h

## Purpose

Single-source version header for both build systems and runtime version output.

## Important APIs, Types, and Functions

Defines `KSMBD_TOOLS_VERSION` as `3.5.3`.

## Control Flow

configure.ac and meson.build parse this macro to set project/package version; tools code uses it for `--version` and template substitution.

## State and Persistence Behavior

No runtime state.

## Dependencies and Integration Points

Integrated by autotools, Meson, and man-page/unit template generation.

## Risks and Edge Cases

Version extraction depends on the macro spelling and quote format.

## Test Signals

Tests should verify `./configure --version`, Meson project version, generated man pages, and `ksmbd.* --version` all agree.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/worker.h -->
# sources/user-network-fs/ksmbd-tools/include/worker.h

## Purpose

Declares the worker IPC queue entry point for mountd.

## Important APIs, Types, and Functions

Exposes `wp_ipc_msg_push(struct ksmbd_ipc_msg *msg)`.

## Control Flow

ipc.c pushes kernel events into worker processing through this function; worker.c dispatches events to user, share, session, tree, RPC, and SPNEGO handlers.

## State and Persistence Behavior

Queued `ksmbd_ipc_msg` objects are heap-allocated and transfer ownership to the worker pipeline.

## Dependencies and Integration Points

Depends on ipc.h message structure and mountd worker implementation.

## Risks and Edge Cases

Ownership and queue backpressure are implicit here; callers must not free messages after push unless the implementation says so.

## Test Signals

Tests require event injection through ipc.c or worker unit tests for each IPC event type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/include/worker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/ksmbd.conf.5.in -->
# sources/user-network-fs/ksmbd-tools/ksmbd.conf.5.in

## Purpose

Manual-page template documenting `ksmbd.conf`, the share and global configuration file consumed by mountd.

## Important APIs, Types, and Functions

Documents file format, section/key syntax, comments, duplicate semantics, share names, user mapping, and global/share parameters such as interfaces, protocol limits, guest settings, signing, encryption, masks, user lists, veto files, VFS objects, and connection limits.

## Control Flow

The template is rendered by autotools or Meson by substituting sysconfdir and version. Runtime code implements the documented parser and behavior in config_parser and management modules.

## State and Persistence Behavior

Persistent state described is `@sysconfdir@/ksmbd/ksmbd.conf` and example config. `ksmbd.addshare` rewrites this file and can notify mountd by SIGHUP.

## Dependencies and Integration Points

Integrated with addshare, mountd, config_parser, management/share, and system packaging.

## Risks and Edge Cases

Documentation must remain synchronized with `KSMBD_SHARE_CONF`, defaults, parser semantics, and compile-time Kerberos support. Some options are commented out or marked not retained by addshare.

## Test Signals

Tests include generated man-page substitution, option/default parity checks against parser tables, and manual examples parsed by config_parser.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/ksmbd.conf.5.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/ksmbd.service.in -->
# sources/user-network-fs/ksmbd-tools/ksmbd.service.in

## Purpose

Template for a systemd service that starts `ksmbd.mountd`.

## Important APIs, Types, and Functions

Uses substitutions for `@sbindir@` and `@runstatedir@`. The unit declares network ordering, loads the `ksmbd` kernel module before start, runs mountd in foreground mode, and stores `PIDFile=@runstatedir@/ksmbd.lock`.

## Control Flow

systemd starts the service after `network.target`, runs `modprobe ksmbd`, then executes `ksmbd.mountd -n`. Restart is disabled by default.

## State and Persistence Behavior

Runtime state is the mountd lock/pid file under runstatedir and kernel module state.

## Dependencies and Integration Points

Depends on systemd, modprobe, the kernel ksmbd module, generated path substitutions, and the installed `ksmbd.mountd` symlink.

## Risks and Edge Cases

If runstatedir does not match the compiled PATH_LOCK value, service tracking and control commands can fail. Kernel module load failures prevent service startup.

## Test Signals

Install into a staging systemd unit directory and verify `systemd-analyze verify`, correct path substitution, and service start/stop with the kernel module available.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/ksmbd.service.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/ksmbdpwd.db.5.in -->
# sources/user-network-fs/ksmbd-tools/ksmbdpwd.db.5.in

## Purpose

Manual-page template for the ksmbd password database format.

## Important APIs, Types, and Functions

Documents `name:password` lines, user-name UTF-8/length/colon constraints, and NT password hash derivation: UTF-8 password to UTF-16LE, MD4, then Base64 with padding.

## Control Flow

Rendered by build systems and referenced by adduser and mountd docs. Runtime parsing is performed by config_parser/user management.

## State and Persistence Behavior

Persistent state is `@sysconfdir@/ksmbd/ksmbdpwd.db`, modified by `ksmbd.adduser` and reloaded by mountd.

## Dependencies and Integration Points

Depends on adduser, md4_hash, tools charset/Base64 helpers, and user management.

## Risks and Edge Cases

Docs must match actual max password length and hash encoding behavior. Command-line password use has operational secrecy concerns not fully captured by file format docs.

## Test Signals

Tests include generated substitution, known hash examples, invalid user lines, empty passwords, and reload after database updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/ksmbdpwd.db.5.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/meson.build -->
# sources/user-network-fs/ksmbd-tools/meson.build

## Purpose

Top-level Meson build definition for ksmbd-tools. It mirrors the autotools configuration in a Meson/Ninja graph.

## Important APIs, Types, and Functions

Declares the C project version by reading `include/version.h`, sets `gnu99`, creates common include directories, resolves GLib, libnl-genl, optional systemd, optional krb5, pthread, and config.h feature macros.

## Control Flow

Meson probes krb5 ABI members/functions when the feature dependency is found, computes `runstatedir`, installs `ksmbd.conf.example`, renders man pages and `ksmbd.service`, then enters addshare, adduser, control, mountd, and tools subdirectories.

## State and Persistence Behavior

Generates build-tree `config.h`, generated man pages, systemd unit, static libraries from subdirs, and final `ksmbd.tools` through the tools subdir.

## Dependencies and Integration Points

Requires Meson >=0.61.5, GLib >=2.58, libnl-genl >=3.0, pthread, optional krb5, optional systemd pkg-config variables, and subdir Meson files.

## Risks and Edge Cases

The `runstatedir` fallback contains a disabled version check and defaults through localstatedir/run. Meson and autotools must stay behaviorally identical for package consumers.

## Test Signals

`meson setup`, `meson compile`, and `meson dist` with krb5 disabled, enabled with MIT, and enabled with Heimdal dependency naming.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/meson_options.txt -->
# sources/user-network-fs/ksmbd-tools/meson_options.txt

## Purpose

Defines Meson options controlling runtime directory, systemd unit installation, and Kerberos support.

## Important APIs, Types, and Functions

Options are string `rundir`, string `systemdsystemunitdir`, feature `krb5` defaulting disabled, and string `krb5_name` defaulting `krb5`.

## Control Flow

Top-level meson.build reads these options to compute `runstatedir`, choose whether/where to install the unit, resolve krb5 dependencies, and choose MIT versus Heimdal pkg-config names.

## State and Persistence Behavior

No runtime state. Build configuration state is stored in the Meson build directory.

## Dependencies and Integration Points

Integrated by top-level `meson.build` and CI jobs.

## Risks and Edge Cases

Packagers must set `krb5=enabled` explicitly for Kerberos. Empty versus explicit path values change install layout.

## Test Signals

Meson setup with default options, explicit `-Drundir=...`, explicit `-Dsystemdsystemunitdir=...`, and both krb5 dependency names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/meson_options.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/Makefile.am -->
# sources/user-network-fs/ksmbd-tools/mountd/Makefile.am

## Purpose

Build-system description for the `mountd autotools` component in ksmbd-tools.

## Important APIs, Types, and Functions

Defines `libmountd.a` from worker, IPC, RPC service, security descriptor, and daemon sources; renders `ksmbd.mountd.8`; installs `ksmbd.mountd` as a symlink to `ksmbd.tools`.

## Control Flow

Automake compiles the daemon static library and generated man page. Install hooks create the command symlink used by the systemd unit.

## State and Persistence Behavior

Install state is man page and symlink. Runtime state is created by mountd code in runstatedir and netlink/kernel state.

## Dependencies and Integration Points

Requires GLib and libnl flags plus generated config macros for optional Kerberos and paths.

## Risks and Edge Cases

This source list must include all RPC service files and stay synchronized with Meson. Missing libnl flags break IPC compilation.

## Test Signals

Autotools distcheck, link test through `ksmbd.tools`, and `ksmbd.mountd --help` dispatch.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/ipc.c -->
# sources/user-network-fs/ksmbd-tools/mountd/ipc.c

## Purpose

Implements mountd's generic-netlink IPC transport to the ksmbd kernel module.

## Important APIs, Types, and Functions

Important functions are `ipc_msg_alloc`, `ipc_msg_free`, `ipc_msg_send`, `ipc_process_event`, `ipc_init`, `ipc_destroy`, `ipc_ksmbd_starting_up`, `nlink_msg_cb`, and generic event handlers. It defines netlink policies and command handlers for all `KSMBD_EVENT_*` types.

## Control Flow

Initialization allocates a netlink socket, disables seq checks, installs callbacks, connects to NETLINK_GENERIC, increases receive buffer size, registers/resolves the ksmbd family, sends a startup event filled from `global_conf`, and marks health running. Event processing waits in select, receives messages, validates version, and pushes supported request payloads to the worker queue. Sending wraps `ksmbd_ipc_msg` payloads as netlink attributes whose type equals the event id.

## State and Persistence Behavior

State is the static netlink socket `sk`, registered family metadata, queued heap IPC messages, and kernel-visible startup configuration. Interface list payloads are copied into startup config and freed from global config after send.

## Dependencies and Integration Points

Depends on libnl/libnl-genl, kernel ABI structures, tools/global_conf, worker queue, config parser list freeing, user/share management handlers downstream.

## Risks and Edge Cases

ABI policy min lengths must match kernel structures. Startup aborts on initialization failure. The 16 KiB message cap and fixed payload sizing can reject large share/RPC payloads. Version mismatch skips messages.

## Test Signals

Tests require a matching kernel module for startup and event round trips, plus unit tests for allocation limits, startup payload interface packing, and unsupported event handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/ksmbd.mountd.8.in -->
# sources/user-network-fs/ksmbd-tools/mountd/ksmbd.mountd.8.in

## Purpose

Manual-page template for `ksmbd.mountd` and its the user-mode daemon behavior.

## Important APIs, Types, and Functions

Documents command synopsis, options, default paths, version/help behavior, and related files/utilities. Build systems substitute version, sysconfdir, sbindir, and runstatedir where present.

## Control Flow

The template is transformed into a man page during autotools or Meson builds. It describes the CLI control flow implemented in the matching C file.

## State and Persistence Behavior

No runtime state, but it documents persistent files, lock/fifo paths, kernel sysfs control, or daemon behavior depending on the command.

## Dependencies and Integration Points

Integrated with build template substitution and the matching CLI source.

## Risks and Edge Cases

The man page can drift from getopt options, default limits, and runtime behavior. Generated paths must match compile-time macros.

## Test Signals

Tests should compare documented options with getopt tables and verify generated man-page substitution in both build systems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/ksmbd.mountd.8.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/meson.build -->
# sources/user-network-fs/ksmbd-tools/mountd/meson.build

## Purpose

Build-system description for the `mountd Meson` component in ksmbd-tools.

## Important APIs, Types, and Functions

Creates static library `mountd` from worker, IPC, generic RPC, SRVSVC, WKSSVC, SAMR, LSARPC, security descriptor, and daemon sources; renders `ksmbd.mountd.8`; installs symlink.

## Control Flow

Meson builds all daemon support into one static library with GLib and libnl dependencies, configures the man page, and creates the command symlink.

## State and Persistence Behavior

Build static library and generated man page; install man page and symlink. Runtime daemon state is outside the build file.

## Dependencies and Integration Points

Requires top-level `include_dirs`, `glib_dep`, `libnl_dep`, runstatedir, and config.h.

## Risks and Edge Cases

RPC and IPC source omissions would produce runtime feature gaps. Build parity with Makefile.am is important for packaging.

## Test Signals

Meson compile/dist and `ksmbd.mountd --help`; runtime IPC tests require the kernel module.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/meson.build -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/mountd.c -->
# sources/user-network-fs/ksmbd-tools/mountd/mountd.c

## Purpose

Implements the `ksmbd.mountd` daemon entry point, manager/worker process model, config reload, share listing protocol, daemonization, and signal handling.

## Important APIs, Types, and Functions

Important functions are `mountd_main`, `manager_init`, `manager_init_wait`, `worker_init`, `worker_init_wait`, `worker_sa_sigaction`, `list_config`, and `__splice_pipe`.

## Control Flow

The CLI parses port, foreground/daemon mode, config path, password DB path, verbosity, and version/help. The manager optionally forks/daemonizes, parses lock/subauth, then repeatedly starts a worker. The worker loads config, initializes signal handlers, processes netlink IPC, reloads config on SIGHUP, and lists shares through a pipe/FIFO protocol on SIGUSR1.

## State and Persistence Behavior

Persistent/runtime state includes `global_conf.pid`, lock file from `cp_parse_lock`, runstatedir FIFO paths, syslog/stdout logging mode, loaded config/user/share state, and health flags controlling reload/list/stop.

## Dependencies and Integration Points

Depends on tools, config_parser, ipc, management/share, signals, fork/pipe/splice/fcntl, and the kernel IPC channel.

## Risks and Edge Cases

Signal forwarding between manager and worker is subtle. FIFO list output depends on SIGUSR1/SIGIO ordering. Worker restart only occurs for `-ECHILD`; other errors terminate. Daemon mode redirects stdio and reports readiness with SIGUSR1.

## Test Signals

Tests should cover foreground and daemon startup, lock handling, config reload, share listing through control, worker crash/restart behavior, and clean shutdown on SIGTERM.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/mountd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc.c -->
# sources/user-network-fs/ksmbd-tools/mountd/rpc.c

## Purpose

Implements the generic DCE/RPC/NDR engine and named-pipe lifecycle used by ksmbd's RPC IPC support.

## Important APIs, Types, and Functions

Important APIs include pipe table management, `dcerpc_set_ext_payload`, `rpc_pipe_reset`, NDR integer/string/pointer/array helpers, DCE/RPC header read/write, bind parsing/ack/nack, `rpc_open_request`, `rpc_write_request`, `rpc_read_request`, `rpc_ioctl_request`, `rpc_close_request`, and `rpc_restricted_context`.

## Control Flow

Open creates a pipe and DCE context for a kernel handle. Write parses the incoming DCE/RPC header, bind or request header, then dispatches to SRVSVC, WKSSVC, SAMR, or LSARPC write handlers. Read attaches the response buffer, handles bind responses or service read handlers, and writes headers/status. Close removes the pipe. Array helpers estimate how many entries fit in fixed buffers and leave `RETURN_READY` set for continuation.

## State and Persistence Behavior

State includes global `pipes_table` guarded by `GRWLock`, per-pipe pending entries/callbacks, and per-DCE payload cursor, flags, request/response pointers, decoded service-specific request unions, and pointer counters.

## Dependencies and Integration Points

Depends on GLib, endian conversion, kernel RPC ABI, service modules, tools charset conversion, and global anonymous restriction config.

## Risks and Edge Cases

The implementation is deliberately partial and hand-coded; NDR alignment, endian handling, string length, fixed-buffer overflow, multi-fragment responses, and handle cleanup are high-risk. `try_realloc_payload` grows dynamic buffers but fixed external buffers must be exact.

## Test Signals

Tests should cover bind negotiation, unsupported syntaxes/opnums, little/big endian integer round trips, UTF-16 string conversion, fixed-buffer overflow, multi-part share enumeration, pipe collision/close, and restricted-context denial.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc_lsarpc.c -->
# sources/user-network-fs/ksmbd-tools/mountd/rpc_lsarpc.c

## Purpose

Implements the LSARPC DCE/RPC service for policy handles, domain information, SID lookup, and name lookup.

## Important APIs, Types, and Functions

Important functions include policy-handle table alloc/lookup/free, `lsarpc_get_primary_domain_info_*`, `lsarpc_open_policy2_return`, `lsarpc_query_info_policy_*`, `lsarpc_lookup_sid2_*`, `lsarpc_lookup_names3_*`, `lsarpc_close_*`, public read/write entry points, and init/destroy.

## Control Flow

Initialization caches an uppercase hostname-derived domain name and creates the policy-handle table. The write phase parses opnum-specific handles, levels, SID arrays, or names. The read phase validates handles, writes domain role/account-domain responses, maps SIDs to names and names to domain SIDs/users, appends RPC return status, and writes DCE/RPC headers.

## State and Persistence Behavior

State includes global `ph_table`, `domain_name`, per-request `lsarpc_names_info` entries in the pipe, and handles embedded in `dce->lr_req`. Lookup entries are freed by the pipe entry callback.

## Dependencies and Integration Points

Depends on management/user, smbacl SID helpers, generic RPC/NDR helpers, passwd lookup by uid, GLib tables/strings, and global domain subauth config.

## Risks and Edge Cases

The switch cases use `case A || B`, which evaluates as a constant expression rather than two case labels; behavior relies on frag_length to distinguish close versus primary-domain info and deserves scrutiny. Binary handles are stored with string hash/equality, a potential mismatch for embedded NULs. Name parsing mutates strings with `strtok`.

## Test Signals

Tests should cover open/query/close policy, primary-domain info, lookup SID for known and unknown users, lookup names with domain prefixes, bad handles, malformed arrays, and the opnum 0/close ambiguity.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc_lsarpc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc_samr.c -->
# sources/user-network-fs/ksmbd-tools/mountd/rpc_samr.c

## Purpose

Implements the SAMR DCE/RPC service for domain and user account queries used by Windows clients.

## Important APIs, Types, and Functions

Important functions include connect-handle table alloc/lookup/free, `samr_connect5_*`, enum/lookup/open domain, lookup/open user, query user info, query security, group/alias membership, close handlers, domain entry initialization, and public read/write entry points.

## Control Flow

Initialization creates uppercase hostname and Builtin domain entries plus the handle table. The write phase parses opnum-specific handles, names, RIDs, and access masks. The read phase validates handles/refcounts, resolves users through user management, writes NDR domain arrays, user RID/type arrays, large user-info level 0x15 structures, security descriptors via smbacl, group membership, alias membership, status, and DCE/RPC headers.

## State and Persistence Behavior

State includes global `ch_table`, `domain_entries`, `domain_name`, `num_domain_entries`, handle refcounts, and an optional user pointer stored in a connect handle after lookup-names. Responses use per-DCE decoded `sm_req` state.

## Dependencies and Integration Points

Depends on management/user, smbacl, generic RPC helpers, GLib, hostname, and global subauth config.

## Risks and Edge Cases

Handle/user lifetime across reloads is sensitive. `profile_path` allocation appears short for the added separator and `profile` suffix. Many NDR structures are hand-coded with fixed constants. Only a subset of SAMR is implemented.

## Test Signals

Tests should cover every supported opnum, bad handles, unknown users, refcounted close sequences, user info buffer layout, security descriptor generation, group membership constants, restricted context, and fuzzed short requests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc_samr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc_srvsvc.c -->
# sources/user-network-fs/ksmbd-tools/mountd/rpc_srvsvc.c

## Purpose

Implements the SRVSVC DCE/RPC service for share enumeration and share information.

## Important APIs, Types, and Functions

Important functions include share type/entry size/representation/data callbacks, `srvsvc_parse_share_info_req`, `srvsvc_share_enum_all_invoke`, `srvsvc_share_get_info_invoke`, `srvsvc_share_info_return`, and public read/write request entry points.

## Control Flow

The write phase parses server name, level, request container, max size, resume handle, or share name. It collects browseable/available shares or a single allowed share, respecting host allow/deny maps and restricted context. The read phase chooses level 0 or 1 serializers, writes NDR union/container data, total entries, resume handle, return status, and DCE/RPC headers.

## State and Persistence Behavior

State is per-pipe share references held in `pipe->entries`, decoded request strings in `dce->si_req`, entry callbacks, and processed counters. Entries are released by `__share_entry_processed`.

## Dependencies and Integration Points

Depends on management/share reference APIs, generic RPC/NDR helpers, and kernel RPC status codes.

## Risks and Edge Cases

Only levels 0 and 1 are supported. Host filtering uses simple share maps. Buffer-size continuation must preserve pending entries and free request strings only when complete. Restricted context changes status from invalid parameter to access denied.

## Test Signals

Tests should enumerate with no shares, multiple browseable/unbrowseable shares, max-size constrained responses, get info for missing/denied/allowed shares, levels 0/1/unsupported, and restricted anonymous access.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc_srvsvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc_wkssvc.c -->
# sources/user-network-fs/ksmbd-tools/mountd/rpc_wkssvc.c

## Purpose

Implements the WKSSVC NetWkstaGetInfo DCE/RPC service.

## Important APIs, Types, and Functions

Important functions are `wkssvc_parse_netwksta_info_req`, `wkssvc_netwksta_info_invoke`, `wkssvc_netwksta_info_return`, level-100 representation/data callbacks, and public read/write request entry points.

## Control Flow

The write phase parses a unique server-name string and requested info level. The read phase supports level 100 only, writing NT platform id, server name, workgroup/domain name, version major/minor, return status, and DCE/RPC headers.

## State and Persistence Behavior

State is one decoded `wi_req` in the DCE context. Server-name memory is freed after response serialization.

## Dependencies and Integration Points

Depends on generic RPC helpers, global `work_group`, tools charset conversion, and restricted-context logic.

## Risks and Edge Cases

Only level 100 is implemented. The server-name echo behavior is minimal. Unsupported levels must return invalid-level without leaking parsed strings.

## Test Signals

Tests should request level 100 with normal and empty server names, unsupported levels, restricted context, and malformed string payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/rpc_wkssvc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/smbacl.c -->
# sources/user-network-fs/ksmbd-tools/mountd/smbacl.c

## Purpose

Implements SID, ACL, and security descriptor helpers shared by SAMR and LSARPC.

## Important APIs, Types, and Functions

Important functions are `smb_read_sid`, `smb_write_sid`, `smb_copy_sid`, `smb_init_domain_sid`, `smb_compare_sids`, `set_domain_name`, `build_sec_desc`, plus internal ACE/DACL builders.

## Control Flow

SID read/write marshal revision, authority bytes, and subauthorities through NDR helpers. Domain SID initialization uses `global_conf.gen_subauth`. Domain-name resolution recognizes ksmbd's local domain, Unix users/groups SIDs, or falls back to SID string. Security descriptor building writes a self-relative descriptor with a DACL containing Everyone, Administrators, Account Operators, and owner RID ACEs.

## State and Persistence Behavior

No persistent state. It reads global subauth values and writes into the current DCE/RPC response payload.

## Dependencies and Integration Points

Depends on rpc.h NDR helpers, tools/global_conf, GLib, and LSARPC domain-name constants.

## Risks and Edge Cases

Subauthority count validation is critical. ACL size is patched after writing, so offset restoration must be exact. Access masks and RID constants are hard-coded and should match Windows expectations.

## Test Signals

Tests should round-trip SIDs, compare known SIDs, resolve local/unix/unknown domains, build security descriptors for sample RIDs, and verify ACL size and ACE count.
<!-- END_FILE_RESEARCH: sources/user-network-fs/ksmbd-tools/mountd/smbacl.c -->
