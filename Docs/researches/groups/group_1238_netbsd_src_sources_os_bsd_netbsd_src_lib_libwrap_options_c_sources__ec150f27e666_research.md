# Group Research: group_1238_netbsd_src_sources_os_bsd_netbsd_src_lib_libwrap_options_c_sources__ec150f27e666

Scope: `Docs/research_subset_a.md`. All listed source files were read completely; no file was sampled.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/options.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/options.c

## Summary
Implements TCP wrappers `hosts_options(5)` option parsing and execution. It parses colon-separated access-control options, validates option arguments, performs percent expansion where required, and dispatches handlers for access decisions and process/socket side effects.

## Main Responsibilities
- Parse option fields with escaped `\:` support and optional `=` separators.
- Enforce option metadata: required argument, optional argument, no argument, must-be-last, and percent-expanded argument.
- Execute `allow` and `deny` by non-local jump to `hosts_access()`.
- Implement runtime options including `user`, `group`, `umask`, `linger`, `keepalive`, `spawn`, `twist`, `rfc931`, `setenv`, `nice`, `severity`, and `banners`.
- Support dry-run verification mode for tools such as `tcpdmatch`.

## Risks
Option processing intentionally performs irreversible side effects. `spawn` and `twist` execute shell commands, `setenv` mutates process environment, and `user`/`group` change credentials. `get_field()` mutates the input string and keeps static parsing state, so it is not reentrant.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/options.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/percent_x.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/percent_x.c

## Summary
Expands TCP wrappers `%<char>` substitutions in strings used by banners and shell commands.

## Main Responsibilities
- Expand `%a`, `%A`, `%c`, `%d`, `%h`, `%H`, `%n`, `%N`, `%p`, `%s`, `%u`, and `%%`.
- Pull expansion values from `request_info` evaluation helpers.
- Sanitize expansion strings by replacing shell-unsafe characters with `_`.
- Abort after warning if expansion would exceed the caller-provided buffer.

## Risks
The sanitizer edits expansion strings in place, which can affect cached request fields returned by evaluation helpers. Overflow handling calls `sleep(5)` and `exit(0)` rather than returning an error.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/percent_x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/refuse.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/refuse.c

## Summary
Logs and terminates a refused TCP wrappers request.

## Main Responsibilities
- Log a denial with `deny_severity`.
- Format the remote endpoint through `eval_client(request)`.
- Terminate via `clean_exit(request)` so datagram services drain pending input.

## Risks
This function does not return. Correct behavior depends on `clean_exit()` handling protocol-specific cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/refuse.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/rfc931.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/rfc931.c

## Summary
Implements RFC 931/AUTH/IDENT/RFC 1413 remote username lookup for a connection.

## Main Responsibilities
- Validate matching local and remote address families.
- Support IPv4 and conditionally IPv6.
- Bind the query socket to the same local address as the protected connection.
- Connect to the remote ident server on port 113.
- Use `alarm()` and `setjmp`/`longjmp` timeout handling.
- Parse `USERID` responses and verify returned port numbers before accepting a username.

## Risks
The routine intercepts `SIGALRM` globally and uses a static jump buffer, so it is not thread-safe and can interfere with callers using alarms. The result is explicitly unsuitable for authentication.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/rfc931.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/shell_cmd.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/shell_cmd.c

## Summary
Executes a TCP wrappers `spawn` shell command in a child process.

## Main Responsibilities
- Fork a child and wait for that child in the parent.
- In the child, ignore `SIGHUP`, redirect standard descriptors to `/dev/null`, and exec `/bin/sh -c`.
- Log fork, open, dup, wait, or exec failures.

## Risks
Commands are shell-executed, so safety depends on prior construction and `percent_x()` sanitization. The parent waits with `wait()`, which can consume unrelated exited children before the target exits.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/shell_cmd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/socket.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/socket.c

## Summary
Provides socket-specific endpoint discovery and address/name conversion for TCP wrappers request evaluation.

## Main Responsibilities
- Install socket methods into `request_info`.
- Determine client and server socket addresses with `getpeername()`, UDP `recvfrom(..., MSG_PEEK)`, and `getsockname()`.
- Convert addresses to numeric host strings using `getnameinfo()`.
- Resolve and verify hostnames with reverse and forward DNS checks.
- Drain unread UDP datagrams during cleanup.

## Risks
Endpoint storage is static and not reentrant. Hostname trust depends on DNS consistency and can mark names `paranoid` on verification failure. UDP peeking leaves payload unread until cleanup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/socket.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/tcpd.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/tcpd.h

## Summary
Central TCP wrappers header defining request metadata, host metadata, update keys, evaluation APIs, socket hooks, globals, and access-control result codes.

## Main Responsibilities
- Define `struct host_info` and `struct request_info`.
- Declare public APIs such as `hosts_access()`, `hosts_ctl()`, `request_init()`, `request_set()`, `eval_*()`, `process_options()`, `percent_x()`, `shell_cmd()`, and `rfc931()`.
- Define request update keys including file descriptor, daemon, user, client/server names, addresses, and sockaddr pointers.
- Define `AC_PERMIT`, `AC_DENY`, and `AC_ERROR`.

## Risks
The structures use fixed-size strings and cached sockaddr pointers. Callers must preserve initialization invariants, usually by using `request_init()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/tcpd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/update.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libwrap/update.c

## Summary
Initializes and updates TCP wrappers `request_info` structures.

## Main Responsibilities
- Reset request structures from a static default instance.
- Set default fd, daemon name, pid, and host back-pointers.
- Apply variadic updates for fd, daemon, user, names, addresses, and sockaddr pointers.
- Warn and stop on invalid update keys.

## Risks
The variadic API has no compile-time type checking. String fields are truncated to `STRING_LENGTH`; sockaddr pointers are stored directly and must remain valid.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libwrap/update.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/liby/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/liby/Makefile

## Summary
Builds the traditional yacc support library `liby`.

## Main Responsibilities
- Sets `NOPIC`.
- Defines `LIB=y`.
- Builds `main.c` and `yyerror.c`.
- Includes `bsd.lib.mk`.

## Integration Notes
Provides fallback `main()` and `yyerror()` routines for yacc-generated programs linked with `-ly`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/liby/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/liby/main.c -->
# File Research: sources/os/bsd/netbsd-src/lib/liby/main.c

## Summary
Provides a minimal yacc-compatible `main()` implementation.

## Main Responsibilities
- Declare external `yyparse()`.
- Ignore command-line arguments.
- Return `yyparse()` result.

## Risks
Programs using this default entry point get no argument handling or setup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/liby/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/liby/yyerror.c -->
# File Research: sources/os/bsd/netbsd-src/lib/liby/yyerror.c

## Summary
Provides the default yacc `yyerror()` routine.

## Main Responsibilities
- Assert the message is non-null.
- Print the message to `stderr`.
- Return `0`.

## Risks
The fallback error report has no location, parser state, or program-name context.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/liby/yyerror.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libz/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libz/Makefile

## Summary
Builds NetBSD `libz` from the common imported zlib source directory.

## Main Responsibilities
- Uses `${NETBSDSRCDIR}/common/dist/zlib`.
- Builds core zlib and gzip stream sources into `LIB=z`.
- Installs `zconf.h`, `zlib.h`, and `zlib.pc`.
- Adds `-DZLIB_CONST` and zlib include paths.
- Defines a `test` target that builds and round-trips `minigzip`.

## Risks
Library behavior follows vendored zlib sources outside this file. The `minigzip` test intentionally omits normal `CFLAGS` to check standalone header usability.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libz/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/lua/Makefile

## Summary
Top-level build dispatcher for NetBSD Lua extension modules.

## Main Responsibilities
- Includes `bsd.own.mk`.
- Builds subdirectories only when `${MKPIC} != "no"`.
- Adds `bozohttpd`, `gpio`, `libm`, `sqlite`, and `syslog` to `SUBDIR`.
- Includes `bsd.subdir.mk`.

## Integration Notes
Lua modules require dynamically loadable shared objects, so they are skipped without PIC support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/lua/Makefile.inc

## Summary
Common make include for Lua modules.

## Main Responsibilities
- Sets default `WARNS?=4`.

## Integration Notes
Submodule Makefiles inherit this warning level unless they override it.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/bozohttpd/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/lua/bozohttpd/Makefile

## Summary
Builds the `bozohttpd` Lua module from the bozohttpd source tree.

## Main Responsibilities
- Defines `LUA_MODULES=bozohttpd`.
- Builds `glue.c` from the external bozohttpd Lua path.
- Links against `libbozohttpd`.
- Adds the bozohttpd source include path.
- Includes `bsd.lua.mk`.

## Integration Notes
The actual module source is in `libexec/httpd/lua`, not this directory.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/bozohttpd/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/gpio/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/lua/gpio/Makefile

## Summary
Builds the Lua GPIO extension module.

## Main Responsibilities
- Defines `LUA_MODULES=gpio`.
- Builds `gpio.c`.
- Includes `bsd.lua.mk`.

## Integration Notes
The module exposes NetBSD GPIO ioctls to Lua.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/gpio/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/gpio/gpio.c -->
# File Research: sources/os/bsd/netbsd-src/lib/lua/gpio/gpio.c

## Summary
Implements a Lua binding for NetBSD GPIO devices.

## Main Responsibilities
- Open GPIO device paths with `O_RDWR` and store fds in Lua userdata.
- Close fds explicitly or from `__gc`.
- Convert Lua pin arguments from integer pin numbers or string pin names into GPIO request structures.
- Issue `GPIOINFO`, `GPIOSET`, `GPIOUNSET`, `GPIOREAD`, `GPIOWRITE`, `GPIOTOGGLE`, and `GPIOATTACH` ioctls.
- Export GPIO pin state/configuration constants and module metadata.

## Risks
Access can mutate hardware state and requires device permissions. Most ioctl error messages identify only the operation name. `gpio_open()` depends on stack position after creating userdata.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/gpio/gpio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/libm/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/lua/libm/Makefile

## Summary
Builds the Lua `libm` extension module.

## Main Responsibilities
- Defines `LUA_MODULES=libm`.
- Builds `libm.c`.
- Links against NetBSD `libm`.
- Includes `bsd.lua.mk`.

## Integration Notes
The module exposes C math library functions and constants to Lua.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/libm/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/libm/libm.c -->
# File Research: sources/os/bsd/netbsd-src/lib/lua/libm/libm.c

## Summary
Exposes many `math.h` functions and constants as a Lua module named `libm`.

## Main Responsibilities
- Use macros to generate wrappers for common libm signatures.
- Provide special wrappers for `fma`, `nan`, `scalbn`, and `ilogb`.
- Validate Lua numeric or integer arguments before calling libm.
- Push results as Lua numbers, integers, or booleans.
- Export constants such as `M_PI`, `M_E`, and related logarithm/square-root constants.

## Risks
Argument validation is minimal and conversion uses Lua numeric APIs. Platform availability is conditional, for example `nextafter` is omitted on `__vax__`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/libm/libm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/sqlite/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/lua/sqlite/Makefile

## Summary
Builds the Lua SQLite extension module.

## Main Responsibilities
- Defines `LUA_MODULES=sqlite`.
- Builds `sqlite.c`.
- Links against NetBSD external public-domain SQLite.
- Includes `bsd.lua.mk`.

## Integration Notes
The module exposes SQLite database and statement APIs to Lua.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/sqlite/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/sqlite/sqlite.c -->
# File Research: sources/os/bsd/netbsd-src/lib/lua/sqlite/sqlite.c

## Summary
Implements a Lua binding for SQLite database connections and prepared statements.

## Main Responsibilities
- Initialize/shutdown SQLite and expose library version/source ID.
- Open databases with `sqlite3_open()` or `sqlite3_open_v2()`.
- Manage database and statement handles through userdata/metatables.
- Prepare, execute, step, reset, finalize, and inspect statements.
- Bind Lua numbers, strings, and nil values to parameters.
- Expose database error code/message, autocommit state, change count, result codes, and open flags.

## Risks
Most operations return numeric SQLite result codes rather than raising Lua errors. Blob columns are returned as nil. `stmt_clear_bindings()` clears bindings and then sets the statement pointer to `NULL`, making subsequent use invalid. Integer columns use 32-bit `sqlite3_column_int()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/sqlite/sqlite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/syslog/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/lua/syslog/Makefile

## Summary
Builds the Lua syslog extension module.

## Main Responsibilities
- Defines `LUA_MODULES=syslog`.
- Builds `syslog.c`.
- Includes `bsd.lua.mk`.

## Integration Notes
The module exposes libc syslog calls and constants to Lua.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/syslog/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/syslog/syslog.c -->
# File Research: sources/os/bsd/netbsd-src/lib/lua/syslog/syslog.c

## Summary
Implements Lua bindings for syslog operations and constants.

## Main Responsibilities
- Wrap `openlog`, `syslog`, `closelog`, and `setlogmask`.
- Emit log messages with `"%s"` to avoid format-string interpretation.
- Export syslog option, facility, and priority constants.
- Add module metadata fields.

## Risks
The binding exposes process-global syslog state. Lua callers can change log identity, facility, and mask for the hosting process.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/lua/syslog/syslog.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/npf/Makefile

## Summary
Top-level build dispatcher for NPF extension modules.

## Main Responsibilities
- Includes `bsd.own.mk`.
- Builds `ext_log`, `ext_normalize`, `ext_rndblock`, and `ext_route` only when `${MKPIC} != "no"`.
- Includes `bsd.subdir.mk`.

## Integration Notes
NPF extensions are shared modules and depend on PIC support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/ext_log/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/npf/ext_log/Makefile

## Summary
Builds the NPF `ext_log` module.

## Main Responsibilities
- Sets `MOD=ext_log`.
- Includes shared `../mod.mk`.

## Integration Notes
The shared make fragment determines source naming, module mode, install path, and `libnpf` dependency.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/ext_log/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/ext_log/npfext_log.c -->
# File Research: sources/os/bsd/netbsd-src/lib/npf/ext_log/npfext_log.c

## Summary
Implements the userland constructor and parameter parser for the NPF `log` extension.

## Main Responsibilities
- Provide no-op initialization.
- Construct extension objects named `log`.
- Treat the parameter as an interface name.
- Resolve the interface index with `if_nametoindex()`.
- If missing, create the interface with `SIOCIFCREATE`, bring it up, and resolve again.
- Store `log-interface` as a u32 extension parameter.

## Risks
Parameter parsing has side effects: an unknown interface name can create and enable an interface. Errors are returned as errno values and also warned through `warn()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/ext_log/npfext_log.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/ext_normalize/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/npf/ext_normalize/Makefile

## Summary
Builds the NPF `ext_normalize` module.

## Main Responsibilities
- Sets `MOD=ext_normalize`.
- Includes shared `../mod.mk`.

## Integration Notes
The actual source is inferred as `npfext_normalize.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/ext_normalize/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/ext_normalize/npfext_normalize.c -->
# File Research: sources/os/bsd/netbsd-src/lib/npf/ext_normalize/npfext_normalize.c

## Summary
Implements userland parameter parsing for the NPF `normalize` extension.

## Main Responsibilities
- Construct extension objects named `normalize`.
- Accept boolean options `random-id` and `no-df`.
- Accept numeric options `min-ttl` and `max-mss`.
- Store recognized parameters through `npf_ext_param_bool()` or `npf_ext_param_u32()`.
- Reject unknown parameters or missing required values with `EINVAL`.

## Risks
Numeric values are parsed with `atol()` and are not range-checked here beyond required presence. Invalid numeric text can collapse to zero.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/ext_normalize/npfext_normalize.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/ext_rndblock/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/npf/ext_rndblock/Makefile

## Summary
Builds the NPF `ext_rndblock` module.

## Main Responsibilities
- Sets `MOD=ext_rndblock`.
- Includes shared `../mod.mk`.

## Integration Notes
The module source is `npfext_rndblock.c`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/ext_rndblock/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/ext_rndblock/npfext_rndblock.c -->
# File Research: sources/os/bsd/netbsd-src/lib/npf/ext_rndblock/npfext_rndblock.c

## Summary
Implements userland parameter parsing for the NPF `rndblock` extension.

## Main Responsibilities
- Construct extension objects named `rndblock`.
- Require values for all parameters.
- Parse `mod` as an integer in `[1, LONG_MAX]`.
- Parse `percentage` as floating-point percent multiplied by 100 for kernel units based on 10000.
- Enforce `percentage` range `[1, 9999]`.
- Store values as u32 extension parameters.

## Risks
Parsing uses `atol()`/`atof()`, so malformed text may be accepted as zero and then rejected by range checks. Floating-point truncation determines final percentage precision.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/ext_rndblock/npfext_rndblock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/ext_route/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/npf/ext_route/Makefile

## Summary
Builds the NPF `ext_route` module.

## Main Responsibilities
- Sets `MOD=ext_route`.
- Includes shared `../mod.mk`.

## Integration Notes
This extension shares the common NPF module build path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/ext_route/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/ext_route/npfext_route.c -->
# File Research: sources/os/bsd/netbsd-src/lib/npf/ext_route/npfext_route.c

## Summary
Implements the userland constructor and parameter parser for the NPF `route` extension.

## Main Responsibilities
- Provide no-op initialization.
- Construct extension objects named `route`.
- Accept a parameter string and store it as `route-interface`.

## Risks
The parameter is not validated as an existing interface in this parser. Interface validation, if any, must occur later.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/ext_route/npfext_route.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/mod.mk -->
# File Research: sources/os/bsd/netbsd-src/lib/npf/mod.mk

## Summary
Shared build fragment for NPF extension modules.

## Main Responsibilities
- Sets warnings to 5 and disables lint.
- Builds each extension as a shared module with `LIBISMODULE=yes`.
- Installs modules under `/lib/npf` or `/lib/${MLIBDIR}/npf`.
- Derives `LIB=${MOD}` and source file `npf${MOD}.c`.
- Links against `libnpf`.

## Integration Notes
Each extension Makefile only needs to set `MOD`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/npf/mod.mk -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/Makefile

## Summary
Kernel include build dispatcher for NetBSD filesystem public headers.

## Main Responsibilities
- Lists filesystem subdirectories including `adosfs`, `autofs`, `cd9660`, and others.
- Includes `bsd.kinc.mk`.

## Integration Notes
Controls which filesystem header directories participate in kernel/user include installation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/adosfs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/adosfs/Makefile

## Summary
Installs public ADOSFS headers.

## Main Responsibilities
- Sets `INCSDIR=/usr/include/adosfs`.
- Installs `adosfs.h`.
- Includes `bsd.kinc.mk`.

## Integration Notes
The implementation sources are kernel build inputs elsewhere; this Makefile is for header installation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/adosfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/adosfs/adlookup.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/adosfs/adlookup.c

## Summary
Implements ADOSFS vnode lookup over AmigaDOS directory hash chains.

## Main Responsibilities
- Check directory execute permission and read-only constraints for delete/rename.
- Use NetBSD namecache before scanning.
- Handle synthetic `.` and `..`, including unlocking the parent for dot-dot `vget`.
- Hash the requested component and scan the selected AmigaDOS hash chain.
- Compare names case-insensitively unless `ADOSFS_EXACTMATCH` is enabled.
- Return `EJUSTRETURN` for last-component create/rename misses on writable directories.
- Cache positive and negative lookup results.

## Risks
Directory traversal depends on on-disk hash-chain integrity. Dot-dot lookup intentionally unlocks the parent to avoid deadlock. Chain-length tracking in `tabi` is sensitive to corrupt media.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/adosfs/adlookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/adosfs/adosfs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/adosfs/adosfs.h

## Summary
Defines public mount arguments and kernel-private ADOSFS data structures, constants, macros, and prototypes.

## Main Responsibilities
- Define `struct adosfs_args`.
- Define AmigaDOS timestamps, `enum anode_type`, `struct anode`, and `struct adosfsmount`.
- Define block type constants, data offsets, filesystem variant macros, and conversion helpers.
- Declare utility functions and vnode operations.

## Risks
Many fields map directly to big-endian on-disk block words. Correct block-size and `nwords` derivation are critical for all table-size macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/adosfs/adosfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/adosfs/adutil.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/adosfs/adutil.c

## Summary
Provides ADOSFS helper routines for block validation, checksums, permissions, case folding, hashing, and endian conversion.

## Main Responsibilities
- Validate AmigaDOS block checksum, primary type, and secondary type.
- Map secondary block types to `anode_type`.
- Translate AmigaDOS protection bits to Unix permission bits.
- Fold ASCII and optional international characters for comparisons.
- Compute AmigaDOS directory hash values.
- Read big-endian words from buffers on non-big-endian systems.

## Risks
Checksum and type validation are the main guardrails against corrupt media. Permission translation has compatibility behavior for extended uid/gid bits and old protection semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/adosfs/adutil.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/adosfs/advfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/adosfs/advfsops.c

## Summary
Implements ADOSFS VFS operations including mount, unmount, root lookup, statvfs, vnode loading, bitmap loading, file-handle conversion, sync, init/done, and module attach/detach.

## Main Responsibilities
- Enforce read-only mounting.
- Resolve, authorize, and open the block device.
- Derive geometry from disklabel/partition data and read the boot block `dostype`.
- Validate DOS type and compute root block, block counts, block size, and data block size.
- Load root vnode and allocation bitmap/free block counts.
- Load `anode` data from on-disk blocks for directories, files, links, and symlinks.
- Convert AmigaDOS symlink syntax to Unix-style paths.
- Register VFS operations and sysctl node.

## Risks
Mount correctness depends on disklabel fields and boot block format. `adosfs_loadvnode()` parses fixed offsets from AmigaDOS blocks; malformed media can produce invalid names, link targets, chains, or permissions. The filesystem is read-only but still exposes NFS file handles without generation validation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/adosfs/advfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/adosfs/advnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/adosfs/advnops.c

## Summary
Implements ADOSFS vnode operations for a read-only AmigaDOS filesystem.

## Main Responsibilities
- Define vnode operation table with mutating operations mapped to read-only or unsupported helpers.
- Report attributes from `anode` metadata.
- Read regular files through UBC for FFS variant or explicit block reads for OFS variant.
- Validate OFS data blocks by type and checksum.
- Map logical file blocks through AmigaDOS file-list block chains.
- Enumerate directories by walking per-directory hash chains and producing `dirent` records.
- Check read/execute permissions and deny writes.
- Return symlink targets and reclaim anode resources.

## Risks
`adosfs_bmap()` depends on valid file-list chains and caches the last indirect block. Directory offsets are synthetic slot counts based on `sizeof(struct dirent)`, not byte offsets in on-disk directories.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/adosfs/advnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/autofs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/autofs/Makefile

## Summary
Installs public AUTOFS headers.

## Main Responsibilities
- Sets `INCSDIR=/usr/include/fs/autofs`.
- Installs `autofs_ioctl.h` and `autofs_mount.h`.
- Includes `bsd.kinc.mk`.

## Integration Notes
These headers define the mount argument and daemon ioctl ABI used by userland automount components.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/autofs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs.c

## Summary
Implements AUTOFS control-device operations, request queuing, trigger/wait logic, caching, timeouts, and daemon interaction.

## Main Responsibilities
- Define `/dev/autofs` open, close, and ioctl handlers.
- Maintain global request queue, condition variable, lock, device-open state, daemon session id, and request ids.
- Build trigger paths and keys from autofs nodes.
- Deduplicate concurrent requests for the same path/key.
- Queue requests for `automountd` and wait for completion.
- Support interruptible waits with temporary signal mask handling.
- Time out pending requests via callout and workqueue.
- Retry failed triggers according to tunables.
- Cache successful nodes and flush caches on update.

## Risks
This code coordinates kernel VFS threads and userland `automountd`. Correctness depends on lock ordering between vnode locks, `sc_lock`, and mount locks. Only one daemon can open the device.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs.h

## Summary
Kernel-private AUTOFS header defining nodes, mounts, request structures, global state, tunables, debug macros, and internal APIs.

## Main Responsibilities
- Define `AUTOFS_ROOTINO`, `VFSTOAUTOFS()`, and `VTOI()`.
- Declare vnode ops, pools, global softc, workqueue, and tunables.
- Define `struct autofs_node` with RB-tree child relationships, vnode pointer, cache state, wildcard state, callout, retry count, and creation time.
- Define `struct autofs_mount`, `struct autofs_request`, and `struct autofs_softc`.
- Declare trigger, cache, flush, node, and timeout functions.

## Risks
Node names are ordered by `strcmp()` in an RB tree. Many routines require the owning mount lock or global softc lock; misuse can corrupt tree/request state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs_ioctl.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs_ioctl.h

## Summary
Defines the user/kernel ioctl ABI for the AUTOFS daemon.

## Main Responsibilities
- Define control path `AUTOFS_PATH` as `/dev/autofs`.
- Define fixed maximum path length `AUTOFS_MAXPATHLEN`.
- Define `struct autofs_daemon_request`.
- Define `struct autofs_daemon_done`.
- Define ioctl commands `AUTOFSREQUEST` and `AUTOFSDONE`.

## Risks
All string fields are fixed 256-byte arrays. Kernel and userland must preserve this ABI exactly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs_mount.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs_mount.h

## Summary
Defines the public mount argument structure for AUTOFS.

## Main Responsibilities
- Define `struct autofs_args` with map source `from`, `master_options`, and `master_prefix`.

## Integration Notes
The VFS mount path copies these user strings into `struct autofs_mount`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs_vfsops.c

## Summary
Implements AUTOFS VFS operations and module lifecycle.

## Main Responsibilities
- Allocate/destroy global softc, pools, condition variable, mutex, and timeout workqueue.
- Mount autofs instances by copying user options/prefix, creating root node, and setting statvfs metadata.
- Support `MNT_UPDATE` as cache flush.
- Support `MNT_GETARGS`.
- Unmount by flushing vnodes, failing outstanding requests, deleting nodes, and freeing mount state.
- Load vnodes from autofs node pointers through vcache.
- Register sysctl tunables and module attach/detach hooks.

## Risks
Unmount marks outstanding daemon requests done with `ENXIO` and waits for them to drain. Node deletion assumes vnodes are flushed and no new triggers can appear. Module unload is blocked while `/dev/autofs` is open.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs_vnops.c

## Summary
Implements AUTOFS vnode operations and node tree management.

## Main Responsibilities
- Trigger automounts from lookup, readdir, and optionally getattr/stat.
- Release vnode locks during daemon-triggered mount operations and reacquire afterward.
- Detect filesystems mounted on top of autofs nodes and delegate operations to the mounted root vnode.
- Lookup `.`, `..`, namecache entries, and autofs child nodes.
- Allow `mkdir` only for automountd descendants, creating synthetic directory nodes.
- Produce synthetic directory entries and attributes.
- Reclaim vnodes without freeing nodes; nodes are freed during explicit tree deletion.
- Manage node creation, lookup, and deletion.

## Risks
Triggering requires careful vnode reference and lock handling so automountd can mount over the trigger vnode. Directory offsets are based on generated dirent record lengths. Node tree mutations require `am_lock`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/autofs/autofs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/Makefile

## Summary
Installs public CD9660/ISO filesystem headers.

## Main Responsibilities
- Sets `INCSDIR=/usr/include/isofs/cd9660`.
- Installs `cd9660_extern.h`, `cd9660_mount.h`, `cd9660_node.h`, `cd9660_rrip.h`, `iso.h`, and `iso_rrip.h`.
- Includes `bsd.kinc.mk`.

## Integration Notes
These headers define ABI and kernel interfaces for ISO 9660 filesystem support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_bmap.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_bmap.c

## Summary
Implements logical-to-physical block mapping for CD9660 files.

## Main Responsibilities
- Return the underlying device vnode when requested.
- Convert logical file block numbers to device block numbers using `iso_start`, mount block shift, and `DEV_BSHIFT`.
- Compute limited read-ahead run length based on file size and `MAXBSIZE`.

## Risks
The mapping assumes ISO files are contiguous extents. Correctness depends on `iso_start`, `i_size`, and mount block shift initialization.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_bmap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_extern.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_extern.h

## Summary
Defines CD9660 kernel mount structure, filesystem type enum, block macros, globals, and filename conversion prototypes.

## Main Responsibilities
- Define sysctl value `CD9660_UTF8_JOLIET`.
- Define `enum ISO_FTYPE`.
- Define `struct iso_mnt` with flags, Joliet level, device, ownership/mask overrides, block geometry, root metadata, type, and Rock Ridge skip values.
- Provide block offset/size macros.
- Declare VFS prototypes, pools, tunables, vnode op vectors, `isodirino()`, and filename conversion functions.

## Risks
This header is central to mount/node/lookup coupling. Block shift and mask fields must match the mounted image’s logical block size.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_lookup.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_lookup.c

## Summary
Implements pathname component lookup for CD9660 directories.

## Main Responsibilities
- Check directory execute permission and read-only delete/rename constraints.
- Consult namecache before scanning.
- Require an exclusive directory vnode lock when scanning.
- Support associated-file lookup using leading `=` outside RRIP mode.
- Reuse last lookup offset with fallback scan from the beginning.
- Read directory blocks and validate ISO directory record lengths and boundaries.
- Compare ISO/Joliet names or Rock Ridge names.
- Compute inode numbers from directory records and retrieve vnodes through vcache.
- Cache positive and negative results.
- Provide `cd9660_blkatoff()`.

## Risks
The scanner stops on illegal record lengths or records crossing block boundaries. RRIP case-insensitive matching is mount-option controlled. Directory offset reuse needs the fallback pass to avoid missed entries.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_lookup.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_mount.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_mount.h

## Summary
Defines public mount arguments and mount flag bits for ISO 9660 filesystems.

## Main Responsibilities
- Define `struct iso_args`.
- Define flags to disable Rock Ridge, enable generation numbers, enable extended attributes, disable Joliet, disable case translation, enable case-insensitive Rock Ridge, and override uid/gid.
- Define printable bit description `ISOFSMNT_BITS`.

## Integration Notes
Userland mount tools and kernel mount code share this structure and flag layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_node.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_node.c

## Summary
Implements CD9660 node pool lifecycle, inactive/reclaim operations, default attribute/timestamp extraction, ISO timestamp conversion, and ISO directory-record inode-number construction.

## Main Responsibilities
- Initialize and destroy `cd9660_node_pool` and ISO mount malloc type.
- Mark inactive nodes recyclable when mode is zero.
- Reclaim vnodes and return `iso_node` objects to the pool.
- Derive default file type, permissions, link count, uid, and gid from directory records and optional extended attributes.
- Derive timestamps from extended attributes or directory record dates.
- Convert 7-byte and 17-byte ISO timestamps to `timespec`.
- Compute directory inode numbers from extent and extended attribute length.

## Risks
Extended attribute parsing is conditional and falls back to permissive read/execute defaults. Timestamp timezone offsets are treated as unreliable outside a bounded range. `isodirino()` must remain compatible with vnode loading code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_node.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_node.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_node.h

## Summary
Defines CD9660 vnode-private node structures, Rock Ridge inode metadata, flags, conversion macros, and vnode operation prototypes.

## Main Responsibilities
- Define `doff_t` as directory offset type.
- Define `ISO_RRIP_INODE`.
- Define `struct iso_node` embedding `genfs_node`, vnode/device references, inode identity, mount pointer, directory lookup caches, extent/start/size, and derived inode attributes.
- Define `VTOI()` and `ITOV()` conversions.
- Declare CD9660 vnode operation functions and helpers.

## Risks
`doff_t` is `long`, with comments noting large directories may exceed 2 GB in theory. The directory offset cache is tightly coupled to lookup behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_node.h -->