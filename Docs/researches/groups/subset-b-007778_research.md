# subset-b-007778 Research

Grouped research for the requested OpenAFS source files. Each section preserves the original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/mkstemp.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/mkstemp.c

## Purpose
Provides a roken fallback implementation of `mkstemp` when the platform C library does not provide one. It turns trailing `X` characters in a caller-supplied template into a process-id-derived suffix and repeatedly attempts an exclusive create until it gets a unique temporary file.

## Important APIs, Types, And Functions
The only exported function is `mkstemp(char *template)`, compiled under `#ifndef HAVE_MKSTEMP` and exposed through `roken.h` as `rk_mkstemp` on platforms missing the native function. It uses `getpid`, `strlen`, `open`, `O_RDWR | O_CREAT | O_EXCL`, mode `0600`, and `errno == EEXIST`.

## Control Flow
The implementation walks backward over trailing `X` characters, replacing them with decimal digits from the process id. It then tries `open`. On any success, or any failure other than name collision, it returns the file descriptor or `-1`. For `EEXIST`, it increments the generated suffix through digits and lowercase letters, carrying forward until a new candidate exists or the generated string is exhausted.

## State And Persistence
The caller's template buffer is modified in place and the created file persists on disk. There is no module global state. The created file descriptor is returned open and must be closed by the caller.

## Dependencies And Integration Points
This is part of Heimdal roken portability support vendored into OpenAFS. It is selected by configure-time feature detection and consumed by code including `roken.h`.

## Risks And Test Signals
The name space is weak compared with modern `mkstemp` implementations because it starts with process-id digits and then performs predictable increments. It assumes a valid template with trailing `X` characters and can underflow if misused. Useful tests cover collision retry, file mode `0600`, in-place template update, no-overwrite behavior, and native-vs-fallback configure builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/mkstemp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/net_read.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/net_read.c

## Purpose
Implements `net_read`, a blocking helper that attempts to read exactly the requested byte count from a socket or file descriptor, returning early only on EOF or error.

## Important APIs, Types, And Functions
The exported function is `net_read(rk_socket_t fd, void *buf, size_t nbytes)`. Unix builds call `read`; Windows builds call `recv`, and under `SOCKET_IS_NOT_AN_FD` can fall back to `_read` when WinSock reports an uninitialized or non-socket handle.

## Control Flow
The function loops while bytes remain, advancing a character pointer by each successful read. Unix retries `EINTR`; Windows deliberately does not retry WinSock `WSAEINTR`, since that can mean a blocking call was cancelled. A zero-length read returns zero immediately, signaling peer close or EOF rather than returning a partial byte count.

## State And Persistence
There is no persistent state. The only side effect is filling the caller-provided buffer with consecutive bytes read from the descriptor.

## Dependencies And Integration Points
It depends on roken socket abstraction macros from `roken.h` and is declared there as a general utility for network protocol code that needs full-record reads.

## Risks And Test Signals
Callers must be prepared for all-or-zero/error behavior; a short read followed by EOF is reported as zero, not the number already copied. Blocking sockets can hang until all requested bytes arrive. Tests should cover EINTR retry on Unix, EOF mid-record, WinSock fallback paths, and exact-size reads over sockets and pipes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/net_read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/net_write.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/net_write.c

## Purpose
Implements `net_write`, a companion to `net_read` that keeps writing until the requested buffer length has been sent or an error occurs.

## Important APIs, Types, And Functions
The exported function is `net_write(rk_socket_t fd, const void *buf, size_t nbytes)`. Unix builds use `write`; Windows builds use `send`, with optional fallback to `_write` under `SOCKET_IS_NOT_AN_FD`.

## Control Flow
The function maintains a remaining byte count and advances the buffer pointer after every successful write. Unix retries interrupted writes. Windows first tries socket I/O and switches permanently to `_write` when the handle appears not to be a WinSock socket. On any non-retryable negative result it returns that error; otherwise it returns `nbytes` after the full buffer is transmitted.

## State And Persistence
There is no persistent state. The side effect is network or descriptor output. The function does not frame data, flush streams, or close descriptors.

## Dependencies And Integration Points
The helper depends on roken's `rk_socket_t`, socket-error macros, and platform I/O headers. It is declared in `roken.h` for portable protocol code.

## Risks And Test Signals
The helper can block indefinitely on blocking descriptors. On Windows, the error retry branch checks `errno == EINTR` rather than `rk_SOCK_ERRNO`, which matters outside the `_write` fallback path. Tests should exercise partial writes, EINTR, closed peer errors, zero-byte writes, and fallback behavior with file descriptors on Windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/net_write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/realloc.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/realloc.c

## Purpose
Provides roken's allocator wrapper `rk_realloc`, mainly to normalize behavior and support macro remapping of `realloc` through `roken.h`.

## Important APIs, Types, And Functions
The only function is `rk_realloc(void *ptr, size_t size)`. It undefines any `realloc` macro before including/using libc allocation so the wrapper can call the real allocator.

## Control Flow
If `ptr` is `NULL`, the function delegates to `malloc(size)`. Otherwise it delegates to `realloc(ptr, size)`.

## State And Persistence
The persistent state is heap memory managed by the C runtime. The function may move or free the old allocation exactly as `realloc` would.

## Dependencies And Integration Points
On MSVC builds, `roken.h.in` can map `realloc` to `rk_realloc` so all roken-linked binaries share the same allocator family. This file is a small but important part of that ABI boundary.

## Risks And Test Signals
Semantics are intentionally libc-like, including implementation-defined handling of `size == 0`. Test signals are compile coverage with allocator macro remapping, successful `NULL` allocation, resize preservation, and cross-DLL allocation/free consistency on Windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/realloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/rename.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/rename.c

## Purpose
Implements `rk_rename` for platforms whose native `rename` does not unlink an existing destination before replacing it.

## Important APIs, Types, And Functions
The exported function is `rk_rename(const char *oldname, const char *newname)`. `roken.h.in` uses it when `RENAME_DOES_NOT_UNLINK` is configured; otherwise `rk_rename` is a macro to native `rename`.

## Control Flow
The function first calls `rename(oldname, newname)`. If it fails with `EEXIST` or `EACCES`, it tries `unlink(newname)` and then retries `rename` only if the unlink succeeds. It returns the final status code.

## State And Persistence
This function mutates filesystem namespace state. It may delete the destination path before the second rename attempt.

## Dependencies And Integration Points
It depends on POSIX-style `rename`, `unlink`, and `errno`, wrapped through roken portability headers. It is used by callers that want Unix replacement semantics across platforms.

## Risks And Test Signals
The unlink-plus-rename sequence is not atomic and can race with other processes; it can also delete the destination and fail to install the source. Tests should cover replacement of regular files, permission errors, missing source, same-file behavior, and platform configurations where native rename already replaces targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/rename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/roken-common.h -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/roken-common.h

## Purpose
Defines common roken portability constants, calling convention macros, process-execution status helpers, and declarations for utility functions shared by generated `roken.h` variants.

## Important APIs, Types, And Functions
The header defines `ROKEN_LIB_FUNCTION`, `ROKEN_LIB_CALL`, C++ linkage wrappers, fallback constants for sockets, syslog, paths, file descriptors, `PATH_MAX`, signals, `getaddrinfo` error codes, name-info flags, and shutdown constants. It declares `simple_exec*`, `wait_for_process*`, `pipe_execv`, `eread`, `ewrite`, socket helpers, timeval helpers, pid-file helpers, environment helpers, `rk_warnerr`, `rk_realloc`, string-pool helpers, data dump helpers, close-on-exec helpers, `ct_memcmp`, `rk_random_init`, and `rk_mkdir`.

## Control Flow
There is no executable control flow. The header controls compilation by filling gaps when system headers or libraries do not provide common interfaces.

## State And Persistence
The file itself stores no runtime state, but it declares APIs that manage process children, environment arrays, pid files under `_PATH_VARRUN`, sockets, time values, and heap-backed string pools.

## Dependencies And Integration Points
`roken.h.in` includes this header after platform headers and type definitions are established. OpenAFS uses the resulting roken interface to compile Heimdal-derived portability code consistently across Unix and Windows.

## Risks And Test Signals
Macro collisions are the main risk: fallback definitions for `min`, `max`, syslog constants, path constants, and function names can affect consumers. Test signals are broad compile coverage across Unix, MSVC, IPv6/no-IPv6, and missing-feature configure matrices, plus runtime smoke tests for declared helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/roken-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/roken.h.in -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/roken.h.in

## Purpose
Template for the generated public roken header. It collects platform headers, defines roken socket and allocator abstractions, maps missing libc/POSIX APIs to `rk_*` implementations, and declares the portability surface used by Heimdal-derived code inside OpenAFS.

## Important APIs, Types, And Functions
It defines `rk_socket_t`, `rk_closesocket`, socket error macros, `rk_SOCK_INIT`, `rk_SOCK_EXIT`, MSVC integer and POSIX-like types, `ssize_t`, `rk_UNCONST`, WinSock `msghdr`/`sendmsg_w32`, allocator wrappers, string wrappers, `strerror_r` compatibility, network address APIs, passwd/group helpers, pidfile, byte-swap, flock, `net_read`, `net_write`, getopt globals, `addrinfo` and `sockaddr_storage` fallbacks, time/date functions, `setprogname`/`getprogname`, vis/unvis APIs, `closefrom`, `timegm`, tree-search macros, random macros, and Linux `SOCK_CLOEXEC` socket wrapping.

## Control Flow
The file is preprocessor-driven. Configure macros decide whether names such as `setenv`, `snprintf`, `strlcpy`, `mkstemp`, `getaddrinfo`, or `tsearch` resolve to native functions or roken replacements.

## State And Persistence
The header creates no state directly. It exposes state-bearing APIs for environment variables, pid files, sockets, random number initialization, memory allocation, and program-name globals.

## Dependencies And Integration Points
Generated from the build system and included by nearly every roken source file. It is the ABI and macro contract between OpenAFS, vendored Heimdal code, system C libraries, WinSock, and MSVC runtime quirks.

## Risks And Test Signals
Because it remaps standard function names, include order and feature-test accuracy are critical. Risks include prototype drift, accidental macro substitution in third-party headers, allocator mismatch on Windows, and wrong socket-handle assumptions. Test signals include all supported platform builds, configure-header regeneration, compile checks with `ROKEN_NO_DEFINE_ALLOCATORS`, and runtime tests for the replacement APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/roken.h.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/setenv.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/setenv.c

## Purpose
Provides a fallback `setenv` implementation for platforms lacking it or needing a roken-compatible prototype.

## Important APIs, Types, And Functions
The exported function is `setenv(const char *var, const char *val, int rewrite)`, mapped to `rk_setenv` by `roken.h` when needed. Unix builds use `asprintf` and `putenv`; Windows builds use `GetEnvironmentVariable` and `SetEnvironmentVariable`.

## Control Flow
If `rewrite` is false and the variable already exists, it returns success without changing state. Unix builds allocate a `NAME=value` string and pass it to `putenv`, intentionally leaking the string because many `putenv` implementations keep the pointer. Windows builds call `SetEnvironmentVariable` directly.

## State And Persistence
The process environment is modified. Unix fallback allocations can persist until process exit.

## Dependencies And Integration Points
The function depends on roken formatting helpers, libc environment APIs, or Win32 environment APIs. It is declared by `roken.h.in` and used by portability code that wants BSD/POSIX `setenv` semantics.

## Risks And Test Signals
Unix memory retention is intentional but can matter for repeated changes in long-running processes. The implementation does not validate invalid names containing `=`. Tests should cover rewrite/no-rewrite, empty value, missing variable, Windows behavior, and interaction with subsequent `getenv` and `unsetenv`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/setenv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/setprogname.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/setprogname.c

## Purpose
Implements `setprogname` on platforms without it, setting the global program-name used by roken warning/error helpers.

## Important APIs, Types, And Functions
The exported function is `setprogname(const char *argv0)`. When native `__progname` is absent, it assigns the basename of `argv0` to the external `__progname`.

## Control Flow
The function ignores `NULL`, finds the final slash, optionally handles backslash path delimiters, then stores the basename. On Windows it duplicates the basename, lowercases it, and strips a `.exe` suffix. On Unix it points `__progname` into the original `argv0` string.

## State And Persistence
The persistent state is the process-global `__progname` pointer. Windows builds allocate memory for the stored program name and do not free it.

## Dependencies And Integration Points
`warnerr.c` and err/warn wrappers call `getprogname`, which depends on this state when the platform lacks native support. `roken.h.in` maps `setprogname` to `rk_setprogname` when needed.

## Risks And Test Signals
On Unix, the stored pointer has the lifetime of `argv0`; callers should pass stable storage. Windows retains allocated memory. Tests should cover slash and backslash paths, `.exe` stripping, case normalization, `NULL`, and warning output prefixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/setprogname.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/snprintf.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/snprintf.c

## Purpose
Provides portable `snprintf`, `vsnprintf`, `asprintf`, `vasprintf`, `asnprintf`, and `vasnprintf` replacements for platforms with missing or non-C99 implementations, especially older MSVC environments.

## Important APIs, Types, And Functions
Core internals are `struct snprintf_state`, `sn_reserve`, `sn_append_char`, `as_reserve`, `as_append_char`, `pad`, `append_number`, `append_string`, `append_char`, and `xyzprintf`. Exported wrappers include `rk_snprintf`, `rk_asprintf`, `rk_asnprintf`, `rk_vasprintf`, `rk_vasnprintf`, and `rk_vsnprintf`.

## Control Flow
`xyzprintf` parses printf format strings, collecting flags, width, precision, and size modifiers, then dispatches supported conversions for characters, strings, signed/unsigned integers, octal, hex, pointers, `%n`, literal `%`, and unknown specifiers. Fixed-buffer output appends only while space remains; allocated-output mode grows a heap buffer by doubling or by needed size, respecting `max_sz` when supplied. Public wrappers set up state and terminate the output buffer.

## State And Persistence
Fixed-buffer calls mutate caller-provided memory. `as*` calls allocate heap strings returned through `char **`; callers own them. There is no global state.

## Dependencies And Integration Points
`roken.h.in` remaps standard formatting names to these functions under MSVC or missing-feature configurations. Many other roken files rely on `asprintf`, including `setenv` and `write_pid`.

## Risks And Test Signals
The implementation supports a practical subset, not full modern printf semantics: no floating point, limited length modifiers, and hand-written formatting edge cases. `%n` writes bytes actually appended, not necessarily total formatted length in truncation cases. Test signals should cover truncation return values, allocated formatting, max-size failures, flags/width/precision, `NULL` strings, integer boundaries, pointer output, and MSVC replacement builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/snprintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/socket.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/socket.c

## Purpose
Supplies portable socket-address helpers and socket option wrappers for IPv4/IPv6 code, plus Windows socket-to-file-descriptor bridging and a Linux `SOCK_CLOEXEC` fallback wrapper.

## Important APIs, Types, And Functions
Exports include `socket_set_any`, `socket_set_address_and_port`, `socket_addr_size`, `socket_sockaddr_size`, `socket_get_address`, `socket_get_port`, `socket_set_port`, `socket_set_portrange`, `socket_set_debug`, `socket_set_tos`, `socket_set_nonblocking`, `socket_set_reuseaddr`, `socket_set_ipv6only`, `socket_to_fd`, `rk_SOCK_IOCTL`, and `rk_socket`.

## Control Flow
Address helpers switch on `sa_family`, filling or inspecting `sockaddr_in` and, when configured, `sockaddr_in6`. Unsupported families either return zero/NULL or terminate with `errx` for setter APIs. Option helpers call `setsockopt`, `fcntl`, or `ioctl` only when relevant compile-time constants exist. `rk_socket` retries without `SOCK_CLOEXEC` if the kernel rejects that flag with `EINVAL`.

## State And Persistence
The functions mutate socket address structures or kernel socket options. `socket_to_fd` transfers close ownership to the C runtime file descriptor on Windows.

## Dependencies And Integration Points
The file depends on `roken.h` for socket abstraction and error macros. It supports network code that needs portable address-family handling without scattering platform conditionals.

## Risks And Test Signals
Fatal `errx` on unsupported families can surprise library callers. Several option setters ignore errors. `socket_set_address_and_port` and port helpers expect ports already in network byte order. Tests should cover IPv4/IPv6 address mutation, nonblocking toggles, option-setting availability, Windows `_open_osfhandle`, and Linux `SOCK_CLOEXEC` fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/strerror_r.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/strerror_r.c

## Purpose
Normalizes `strerror_r` behavior behind `rk_strerror_r` when the platform lacks a compatible POSIX-style prototype or provides the GNU string-returning variant.

## Important APIs, Types, And Functions
The exported function is `rk_strerror_r(int eno, char *strerrbuf, size_t buflen)`. MSVC uses `strerror_s`; other builds either wrap native `strerror_r` or copy `strerror(eno)` with `strlcpy`.

## Control Flow
MSVC writes into the caller buffer and, on failure, attempts a generic formatted message. GNU-style fallback calls `strerror_r`, and if the returned pointer differs from the supplied buffer, copies that string into the buffer and reports `ERANGE` on truncation. No-native fallback copies from `strerror`.

## State And Persistence
Only the caller's buffer is mutated. No module state is retained.

## Dependencies And Integration Points
`roken.h.in` either defines `rk_strerror_r` as native `strerror_r` or declares this function, letting callers use a consistent integer return interface.

## Risks And Test Signals
The MSVC fallback format string appears suspicious (`"Error % occurred."` lacks a numeric conversion), so error-path coverage matters. The non-native branch compares `strlcpy` return with `buflen` and should be tested for exact truncation. Signals include known errno messages, too-small buffers, GNU and POSIX libc variants, and invalid error numbers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/strerror_r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/strlcat.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/strlcat.c

## Purpose
Provides a fallback `strlcat` implementation for platforms missing the BSD function.

## Important APIs, Types, And Functions
The exported function is `strlcat(char *dst, const char *src, size_t dst_sz)`, mapped to `rk_strlcat` by `roken.h` when needed. It uses `strnlen_s`, `strnlen`, or `strlen` depending on platform support.

## Control Flow
The function computes the existing destination length bounded by `dst_sz` when possible. If the destination buffer is already full or malformed relative to the supplied size, it returns `len + strlen(src)` without writing. Otherwise it appends via `strlcpy(dst + len, src, dst_sz - len)` and returns the total length it tried to create.

## State And Persistence
The destination buffer may be modified and NUL-terminated if space allows. No global state exists.

## Dependencies And Integration Points
Used by roken and downstream code as a safer concatenation primitive in missing-feature builds.

## Risks And Test Signals
When no bounded `strnlen` exists, the fallback `strlen(dst)` can read past `dst_sz` for unterminated input. Tests should cover empty/full buffers, truncation return values, one-byte buffers, unterminated destination under supported bounded builds, and native-vs-fallback macro mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/strlcat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/strlcpy.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/strlcpy.c

## Purpose
Provides a fallback `strlcpy` implementation for platforms missing the BSD function.

## Important APIs, Types, And Functions
The exported function is `strlcpy(char *dst, const char *src, size_t dst_sz)`, mapped to `rk_strlcpy` as needed. MSVC 2005+ uses `strncpy_s(..., _TRUNCATE)` and still returns `strlen(src)`.

## Control Flow
The generic implementation copies up to `dst_sz` bytes, stopping at NUL. If the destination fills before the source ends, it forces the last byte to NUL when possible and returns the number of bytes copied plus the remaining source length, matching the attempted source length.

## State And Persistence
The destination buffer is mutated. No global state is used.

## Dependencies And Integration Points
Many roken shims depend on `strlcpy` for bounded string copies, including `strerror_r`.

## Risks And Test Signals
The generic loop can call `strlen` on the post-copy source pointer, so source must be NUL-terminated. Tests should verify return values under no truncation, truncation, `dst_sz == 0`, single-byte destination, and MSVC secure CRT behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/strlcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/strnlen.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/strnlen.c

## Purpose
Implements `strnlen` for platforms lacking it: bounded measurement of a NUL-terminated string.

## Important APIs, Types, And Functions
The single exported function is `strnlen(const char *s, size_t len)`, usually macro-mapped to `rk_strnlen` by `roken.h`.

## Control Flow
The function increments an index until either `len` bytes have been inspected or `s[i]` is NUL, then returns the count.

## State And Persistence
No state is stored or modified.

## Dependencies And Integration Points
Used directly or indirectly by safer string helpers such as `strlcat` when native `strnlen` is unavailable.

## Risks And Test Signals
The caller must pass a valid pointer to at least `len` readable bytes. Tests should cover NUL before limit, no NUL within limit, zero length, and macro mapping in missing-feature builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/strnlen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/strsep.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/strsep.c

## Purpose
Provides a fallback `strsep` tokenizer for systems that lack it.

## Important APIs, Types, And Functions
The exported function is `strsep(char **str, const char *delim)`, macro-mapped to `rk_strsep` by `roken.h` when needed.

## Control Flow
If `*str` is `NULL`, it returns `NULL`. Otherwise it saves the current token start, advances `*str` by `strcspn` until a delimiter or NUL, terminates the token in place when a delimiter is found, advances past the delimiter, or sets `*str` to `NULL` at end-of-string.

## State And Persistence
The input string is modified in place by replacing delimiters with NUL bytes. The caller's cursor pointer is updated.

## Dependencies And Integration Points
Used by roken consumers that expect BSD tokenizer semantics, including empty-field preservation unlike `strtok`.

## Risks And Test Signals
The function requires mutable input. Tests should cover leading, trailing, adjacent, and absent delimiters; empty delimiter strings; and repeated calls until `NULL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/strsep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/strtok_r.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/strtok_r.c

## Purpose
Implements reentrant `strtok_r` for platforms where only non-reentrant tokenization is available.

## Important APIs, Types, And Functions
The exported function is `strtok_r(char *s1, const char *s2, char **lasts)`, declared through `roken.h.in` when needed.

## Control Flow
If `s1` is `NULL`, tokenization resumes at `*lasts`. Leading delimiters are skipped, an empty remainder returns `NULL`, then the function scans until the next delimiter, terminates the token in place, updates `*lasts`, and returns the token start.

## State And Persistence
No internal static state is used. Caller-provided `*lasts` persists tokenization progress and the mutable input string is modified.

## Dependencies And Integration Points
Provides thread-safe tokenization semantics for roken consumers on older platforms.

## Risks And Test Signals
The function assumes `lasts` and resume pointers are valid; if called with `s1 == NULL` and an uninitialized `*lasts`, it will dereference invalid memory. Tests should cover multiple independent tokenizer states, delimiter-only strings, empty tokens behavior, and final `NULL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/strtok_r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/tsearch.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/tsearch.c

## Purpose
Provides public-domain binary tree search APIs compatible with `tsearch`, `tfind`, `tdelete`, and `twalk` when the platform lacks them.

## Important APIs, Types, And Functions
Internal `node_t` stores a key pointer and left/right links. Exported functions are `rk_tsearch`, `rk_twalk`, `rk_tdelete`, and `rk_tfind`; `trecurse` implements traversal. `VISIT` values come from `search.h`.

## Control Flow
`rk_tsearch` walks the tree using the caller comparison function, returning an existing node on equality or allocating/linking a new node at the leaf. `rk_tfind` performs the same search without insertion. `rk_twalk` recursively calls the action callback in leaf/preorder/postorder/endorder order. `rk_tdelete` finds the target, splices replacement children or successor nodes, frees the removed node, and returns the parent pointer tracked during search.

## State And Persistence
The tree root and nodes live in caller-managed storage reachable through `void **rootp`. Nodes are heap allocated; keys are not copied or freed.

## Dependencies And Integration Points
`roken.h.in` maps standard tree-search names to these functions when native APIs are missing.

## Risks And Test Signals
The tree is unbalanced and can degrade to linear behavior or deep recursion. Key lifetime is the caller's responsibility. Tests should cover insertion, duplicate lookup, ordered traversal events, deleting leaf/one-child/two-child/root nodes, missing deletes, and compare-function correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/tsearch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/unsetenv.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/unsetenv.c

## Purpose
Provides a fallback `unsetenv` for platforms missing it.

## Important APIs, Types, And Functions
The exported function is `unsetenv(const char *name)`, declared as `rk_unsetenv` by `roken.h` when needed. It operates on the global `environ` array.

## Control Flow
The function rejects `NULL` names or missing `environ`, computes the variable-name length up to `=` or NUL, finds the first matching `NAME=` entry, and shifts all subsequent environment pointers left by one position.

## State And Persistence
The process environment vector is modified in place. The removed environment string is not freed, which matches the uncertainty around ownership of environment storage.

## Dependencies And Integration Points
Works with `setenv.c` and other roken environment helpers. Feature detection determines whether consumers call this implementation.

## Risks And Test Signals
Only the first matching entry is removed; duplicate environment variables can remain. Empty names are not explicitly rejected. Tests should cover existing/missing variables, names containing `=`, duplicates, empty names, and interaction with `setenv`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/unsetenv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/verr.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/verr.c

## Purpose
Implements BSD-style `verr` for platforms lacking `err.h` support.

## Important APIs, Types, And Functions
The exported function is `verr(int eval, const char *fmt, va_list ap)`. It delegates formatting to `rk_warnerr` with errno output enabled, then exits with `eval`.

## Control Flow
There is no recovery path: print program name, message, and saved errno text through `rk_warnerr`, then call `exit(eval)`.

## State And Persistence
It reads `errno` indirectly in `rk_warnerr`, writes to `stderr`, and terminates the process.

## Dependencies And Integration Points
Works with `err.c`, `warnerr.c`, `getprogname`, and roken's fallback `err.h` surface.

## Risks And Test Signals
This function is process-terminating, so unit tests need subprocess isolation. Signals include correct exit status, stderr prefix, errno preservation, `NULL` format handling, and compatibility with native `verr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/verr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/verrx.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/verrx.c

## Purpose
Implements BSD-style `verrx`, the no-errno variant of `verr`.

## Important APIs, Types, And Functions
The exported function is `verrx(int eval, const char *fmt, va_list ap)`. It delegates to `rk_warnerr` with errno output disabled and then exits.

## Control Flow
The function formats any caller message to `stderr` and immediately terminates with `exit(eval)`.

## State And Persistence
It writes diagnostics and exits the process. No heap or module state is used.

## Dependencies And Integration Points
Used by `errx.c` and callers expecting BSD `errx`/`verrx` behavior in roken portability builds.

## Risks And Test Signals
Subprocess tests should verify no errno suffix is printed, exit code is preserved, program-name prefixing works, and `NULL` messages produce sane output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/verrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/vsyslog.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/vsyslog.c

## Purpose
Provides a fallback `vsyslog` for platforms without one, including `%m` expansion using the saved `errno` value.

## Important APIs, Types, And Functions
The exported function is `vsyslog(int pri, const char *fmt, va_list ap)`. Private `simple_vsyslog` logs the raw format string if allocation fails.

## Control Flow
The function saves `errno`, copies and expands the format string by replacing `%m` with `strerror(saved_errno)`, allocates a formatted message with `vasprintf`, then calls `syslog(pri, "%s", buf)`. Any allocation failure falls back to logging the original format string literally.

## State And Persistence
No module state is retained. It writes to the system logger and uses transient heap buffers.

## Dependencies And Integration Points
`roken.h.in` maps `vsyslog` to `rk_vsyslog` when missing. It depends on roken `vasprintf`, libc `strerror`, and system `syslog`.

## Risks And Test Signals
The low-memory fallback intentionally discards variable arguments. `%m` expansion reallocates the format buffer and must preserve pointer offsets. Tests should cover `%m`, multiple `%m`, allocation-failure simulation if possible, normal format arguments, and syslog facility/priority preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/vsyslog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/vwarn.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/vwarn.c

## Purpose
Implements BSD-style `vwarn`, printing a warning that includes the current `errno` text.

## Important APIs, Types, And Functions
The exported function is `vwarn(const char *fmt, va_list ap)`, delegating to `rk_warnerr(1, fmt, ap)`.

## Control Flow
No branching is performed locally; all formatting and errno handling happens in `rk_warnerr`.

## State And Persistence
Writes to `stderr` and reads `errno` through `rk_warnerr`.

## Dependencies And Integration Points
Used by `warn.c` and roken's fallback err/warn family. It depends on program-name state for prefixes.

## Risks And Test Signals
Tests should verify errno suffix inclusion, format handling, program-name prefixing, and that the function does not exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/vwarn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/vwarnx.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/vwarnx.c

## Purpose
Implements BSD-style `vwarnx`, printing a warning without appending `errno`.

## Important APIs, Types, And Functions
The exported function is `vwarnx(const char *fmt, va_list ap)`, delegating to `rk_warnerr(0, fmt, ap)`.

## Control Flow
The function directly calls the shared warning formatter and returns.

## State And Persistence
It writes to `stderr` but does not mutate process state.

## Dependencies And Integration Points
Used by `warnx.c` and `verrx.c`-style warning paths in the roken fallback err API.

## Risks And Test Signals
Tests should verify no errno suffix, correct prefix, `NULL` format behavior, and non-terminating behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/vwarnx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/warn.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/warn.c

## Purpose
Implements BSD-style variadic `warn`, a non-terminating warning that includes `errno`.

## Important APIs, Types, And Functions
The exported function is `warn(const char *fmt, ...)`. It builds a `va_list` and calls `vwarn`.

## Control Flow
The wrapper starts variadic argument processing, delegates to `vwarn`, then ends argument processing and returns.

## State And Persistence
Writes a diagnostic to `stderr`; no persistent state is modified.

## Dependencies And Integration Points
Part of the roken err/warn compatibility family and relies on `vwarn` plus `rk_warnerr`.

## Risks And Test Signals
Tests should verify formatting, errno inclusion, no exit, and compile-time consistency with `err.h` prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/warn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/warnerr.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/warnerr.c

## Purpose
Centralizes diagnostic formatting for roken's BSD err/warn compatibility functions.

## Important APIs, Types, And Functions
The exported function is `rk_warnerr(int doerrno, const char *fmt, va_list ap)`. It uses `getprogname`, `fprintf`, `vfprintf`, `strerror`, and a saved `errno`.

## Control Flow
The function snapshots `errno`, prints the program name if available, inserts separators when either a format or errno text will follow, formats the caller message if present, appends the saved errno text when requested, and ends with a newline.

## State And Persistence
It writes to `stderr` and reads program-name global state. It preserves the displayed errno by saving it before formatting.

## Dependencies And Integration Points
All `warn`, `warnx`, `err`, `errx`, `vwarn`, `verr`, and related wrappers funnel through this function.

## Risks And Test Signals
Formatting to `stderr` can itself change `errno`, but the message uses the saved value. Tests should cover all combinations of program name present/absent, format present/absent, errno enabled/disabled, and variadic formatting failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/warnerr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/warnx.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/warnx.c

## Purpose
Implements BSD-style variadic `warnx`, a non-terminating warning that omits `errno`.

## Important APIs, Types, And Functions
The exported function is `warnx(const char *fmt, ...)`. It wraps `vwarnx`.

## Control Flow
Starts a `va_list`, calls `vwarnx`, ends the `va_list`, and returns.

## State And Persistence
The function writes to `stderr` through shared warning helpers and does not alter persistent state.

## Dependencies And Integration Points
Part of roken's err/warn compatibility API and depends on `warnerr.c` for actual formatting.

## Risks And Test Signals
Tests should cover formatted output, no errno suffix, no process exit, and declaration compatibility in fallback builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/warnx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/win32_alloc.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/win32_alloc.c

## Purpose
Provides Windows allocator wrapper functions so binaries built with roken can share one allocation/free family across executable and DLL boundaries.

## Important APIs, Types, And Functions
Exports `rk_calloc`, `rk_free`, `rk_malloc`, `rk_strdup`, and `rk_wcsdup`. The file undefines allocator/string-dup macros before calling the real C runtime functions.

## Control Flow
Every wrapper directly delegates to the corresponding CRT allocator or duplicator and returns its result.

## State And Persistence
Heap allocations are created or freed in the CRT heap selected by the roken binary. No module globals exist.

## Dependencies And Integration Points
`roken.h.in` maps `calloc`, `malloc`, `free`, `realloc`, `strdup`, and `wcsdup` to roken wrappers on MSVC unless `ROKEN_NO_DEFINE_ALLOCATORS` is set. This file supplies most of those wrappers.

## Risks And Test Signals
The design relies on all participating code including the same roken header policy. Mixing native `free` with `rk_malloc` can still fail if callers bypass macros. Tests should cover allocation/free across DLL boundaries, `strdup` and `wcsdup`, null-free behavior, and builds with allocator remapping disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/win32_alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/write_pid.c -->
# sources/distributed-fs/openafs/src/external/heimdal/roken/write_pid.c

## Purpose
Implements helpers for writing and deleting daemon pid files, plus a fallback `pidfile` interface.

## Important APIs, Types, And Functions
Exports `pid_file_write(const char *progname)`, `pid_file_delete(char **filename)`, and, when native `pidfile` is absent, `pidfile(const char *bname)`. Private fallback state is `static char *pidfile_path`; `pidfile_cleanup` deletes it at process exit.

## Control Flow
`pid_file_write` formats `_PATH_VARRUN + progname + ".pid"`, opens it for writing, writes the process id, closes it, and returns the allocated path. `pid_file_delete` unlinks and frees a stored path. `pidfile` writes once, defaults the basename from `getprogname`, and registers cleanup with `atexit` or `on_exit`.

## State And Persistence
The pid file persists on disk until cleanup or explicit deletion. The fallback stores one process-global pidfile path pointer.

## Dependencies And Integration Points
Declared through `roken-common.h` and mapped by `roken.h.in`. Used by daemon-style code needing portable pidfile behavior.

## Risks And Test Signals
There is no locking or stale-pid validation, and `_PATH_VARRUN` may not be writable. Tests should cover write/delete, cleanup registration, `NULL` basename behavior, unwritable directories, and duplicate `pidfile` calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/heimdal/roken/write_pid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/import-external-git.pl -->
# sources/distributed-fs/openafs/src/external/import-external-git.pl

## Purpose
Automates importing selected files from an external git repository into `src/external/<module>` in the OpenAFS tree, recording the imported commit and creating an OpenAFS commit that describes upstream changes.

## Important APIs, Types, And Functions
This Perl script uses `Getopt::Long`, `File::Basename`, `File::Temp`, `File::Path`, `IO::File`, `IO::Pipe`, `Pod::Usage`, and `Cwd`. Inputs are `<module> <repository> [<commitish>]`, plus `--externalDir` and `--nofixwhitespace`. State files include `<module>-files`, `<module>-last`, and optional `<module>-author`.

## Control Flow
It reads source-to-destination mappings, reads the previous imported commit and author override, archives selected files from the external repo into a temporary tree, stashes local changes in the module directory, copies mapped files into place, adds new files, removes committed files no longer mapped, writes `<module>-last`, builds a commit message with upstream shortlog and file lists, commits, optionally rebases with whitespace fixing, and amends to trigger hooks. On failure it resets hard to `HEAD` and later pops any stash.

## State And Persistence
The script mutates the OpenAFS git working tree, index, commits, module directory contents, and `<module>-last`. It may stash and pop pre-existing local changes.

## Dependencies And Integration Points
It integrates external upstream source snapshots into OpenAFS vendored directories and depends heavily on command-line git, tar, cp, and module mapping files.

## Risks And Test Signals
The script uses shell string interpolation for paths and file lists, so spaces or metacharacters in names are risky. Error recovery uses destructive `git reset --hard HEAD` inside the module directory. Tests should use disposable repos to cover added/deleted files, mapping parse errors, missing files, author override, no-change imports, dirty-tree stash/pop, whitespace-fix failures, and commit-message content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/external/import-external-git.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/finale/Makefile.in -->
# sources/distributed-fs/openafs/src/finale/Makefile.in

## Purpose
Builds and installs the `translate_et` utility, which translates OpenAFS error codes into table names, offsets, and localized messages.

## Important APIs, Types, And Functions
Targets include `all`, `translate_et`, `test`, `install`, `dest`, and `clean`. Important variables are `INCLS`, `LIBS`, optional `LIBS_rxgk`, and `OBJS=$(top_builddir)/src/afs/unified_afs.o`.

## Control Flow
The default target builds `translate_et` from `translate_et.o`, unified AFS objects, many OpenAFS static libraries, roken, and extra platform libraries. The `test` target runs `translate_et` with a fixed set of error codes, compares output to `test.output`, and removes the temporary output. Install and dest copy the binary into configured bindirs.

## State And Persistence
Build artifacts include `translate_et`, object files, and generated `AFS_component_version_number.c`. The test writes `/tmp/translate_et.output`.

## Dependencies And Integration Points
The utility links against ubik, rx, auth, vldb, bos, com_err, volser, kauth, prot, opr, RFC3961, optional rxgk, and the unified AFS error table object.

## Risks And Test Signals
The broad link dependency set makes this target sensitive to error-table initialization changes and optional rxgk configuration. Test signals are successful build, exact `test.output` comparison, install path correctness, and clean target removal of generated artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/finale/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/finale/translate_et.c -->
# sources/distributed-fs/openafs/src/finale/translate_et.c

## Purpose
Implements the Unix/OpenAFS `translate_et` command-line utility for decoding numeric OpenAFS error codes.

## Important APIs, Types, And Functions
The only function is `main`. It calls multiple error-table initializers, including KA, RXK, KTC, ACFG, CMD, VL, PT, BZ, U, VOLS, unified AFS errors, and optional RXGK. It uses `afs_error_table_name` and `afs_error_message_localize`.

## Control Flow
On AIX, it adjusts SIGSEGV handling to allow full core dumps. It initializes all supported error tables, validates at least one argument, then loops over each numeric argument. For each code, it computes the low `ERRCODE_RANGE` offset, translates the table name and localized message, and prints one summary line.

## State And Persistence
The process-global com_err table registry is initialized. No files are written by the program itself.

## Dependencies And Integration Points
The utility depends on OpenAFS error table libraries and the unified AFS error table object. It is built by `src/finale/Makefile.in` and used by developers or diagnostics to interpret raw errors.

## Risks And Test Signals
Arguments are parsed with `atoi`, so invalid strings silently become zero and large values can overflow. Tests should verify known code translations, no-argument usage failure, optional RXGK builds, localization buffer handling, and AIX signal code compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/finale/translate_et.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/finale/translate_et_nt.c -->
# sources/distributed-fs/openafs/src/finale/translate_et_nt.c

## Purpose
Implements the Windows/admin-library variant of `translate_et`, translating AFS admin status codes into human-readable messages.

## Important APIs, Types, And Functions
The only function is `main`. It calls `afsclient_Init` and `util_AdminErrorCodeTranslate`, using `afs_status_t` and admin client headers.

## Control Flow
The program requires at least one numeric argument. It initializes AFS client/admin error tables, then loops over each argument, converts it with `atoi`, translates it through the admin utility layer, and prints `<code> = <message>`.

## State And Persistence
It initializes admin library process state but writes no persistent data.

## Dependencies And Integration Points
This file targets the Windows/admin API stack rather than the Unix com_err table set. It depends on `afs_Admin.h`, `afs_utilAdmin.h`, and `afs_clientAdmin.h`.

## Risks And Test Signals
Like the Unix variant, `atoi` gives weak input validation. Tests should cover initialization failure, known admin error translations, invalid input strings, and message pointer lifetime from `util_AdminErrorCodeTranslate`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/finale/translate_et_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/fsint/Makefile.in -->
# sources/distributed-fs/openafs/src/fsint/Makefile.in

## Purpose
Generates and builds the AFS file server and callback RPC interface code from rxgen `.xg` specifications.

## Important APIs, Types, And Functions
Targets include `depinstall`, `generated`, `liboafs_fsint.la`, `libfsint_pic.la`, `libafsint.a`, install/dest, and clean. Generated files include `Kcallback.*`, `Kvice.*`, `Kpagcb.*`, `afsint.*`, `afscbint.*`, and `pagcb.h`.

## Control Flow
The default target installs generated headers, regenerates all rxgen outputs, and builds shared/PIC/static libraries. Rxgen invocations select client stubs (`-C`), server stubs (`-S`), XDR (`-c`/`-y -c`), headers (`-h`), kernel variants (`-k`), and AFS options (`-A -x`). Install targets copy the static library and public headers into AFS lib/include destinations.

## State And Persistence
Build outputs are generated C/header files, libtool objects, static libraries, shared-library artifacts, and installed headers. Clean removes generated interface files and objects.

## Dependencies And Integration Points
This makefile is central to the OpenAFS RPC ABI. `fsprobe`, cache managers, file servers, kernel code, and callback listeners depend on the generated interfaces and libraries.

## Risks And Test Signals
Any rxgen rule or dependency drift can desynchronize headers and stubs. Test signals are clean-tree regeneration, successful library builds, no stale generated files after source `.xg` changes, install header consistency, and downstream compile coverage for users such as `fsprobe`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/fsint/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/fsprobe/Makefile.in -->
# sources/distributed-fs/openafs/src/fsprobe/Makefile.in

## Purpose
Builds the file-server probe library and test program, including callback server stubs needed for FileServer callback traffic.

## Important APIs, Types, And Functions
Targets include `liboafs_fsprobe.la`, `libfsprobe.a`, installed `fsprobe.h`, generated/copy targets for `afscbint.h` and `afscbint.ss.c`, `fsprobe_test`, install/dest, and clean. Objects are `fsprobe.lo`, `fsprobe_callback.lo`, `afscbint.ss.lo`, and `AFS_component_version_number.lo`.

## Control Flow
The default target builds the shared library, installs the public header into `TOP_INCDIR`, creates the static library, and links `fsprobe_test`. The makefile copies generated callback server files from `src/fsint` because `RXAFSCB_ExecuteRequest` is required by the probe's callback listener.

## State And Persistence
Build artifacts include libtool objects, `libfsprobe.a`, `liboafs_fsprobe.la`, copied generated callback files, `fsprobe_test`, and version files.

## Dependencies And Integration Points
Depends on rxkad, fsint, cmd, util, opr, volser, roken, pthread config, and libtool. Provides the library consumed by monitoring/probe tools.

## Risks And Test Signals
The library is sensitive to fsint generated-stub changes and rx/volser ABI changes. Tests should verify clean builds, copied callback stub freshness, static and shared link success, and `fsprobe_test` link against current dependency libraries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/fsprobe/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/fsprobe/fsprobe.c -->
# sources/distributed-fs/openafs/src/fsprobe/fsprobe.c

## Purpose
Implements the AFS FileServer probe facility. It initializes Rx connections to one or more file servers and volume servers, periodically collects statistics and partition information, and calls a user-supplied handler after each probe sweep.

## Important APIs, Types, And Functions
Public functions are `fsprobe_Init`, `fsprobe_Cleanup`, `fsprobe_ForceProbeNow`, and `fsprobe_Wait`. Important private pieces are `fsprobe_CleanupInit`, `fsprobe_LWP`, `XListPartitions`, globals `fsprobe_numServers`, `fsprobe_ConnInfo`, `fsprobe_Results`, `fsprobe_ProbeFreqInSecs`, `fsprobe_initflag`, `fsprobe_Handler`, `fsprobe_force_lock`, and `fsprobe_force_cv`.

## Control Flow
`fsprobe_Init` validates arguments, initializes locks and callback stubs, allocates connection/stat/result arrays, initializes Rx, creates null client/server security objects, opens file-server and volume-server connections for each socket, lists partitions, creates an AFS callback service using `RXAFSCB_ExecuteRequest`, starts the Rx server, and launches the probe thread. `fsprobe_LWP` loops forever: increments probe count, clears result arrays, calls `RXAFS_GetStatistics64` with fallback to `RXAFS_GetStatistics`, queries volume partition information via 64-bit or old APIs, calls the registered handler, then waits for the configured interval or a force-probe signal. `fsprobe_Cleanup` destroys Rx connections and optionally frees arrays.

## State And Persistence
State is process-global: server count, connection array, latest results, probe number, thread, locks, and cached partition lists. No disk state is written. The probe thread is not explicitly stopped by cleanup.

## Dependencies And Integration Points
Integrates with Rx, rxnull security, generated fsint callback stubs, volser partition APIs, hostutil name lookup, OPR mutex/condition primitives, and `fsprobe_callback.c`.

## Risks And Test Signals
Major risks include infinite probe thread lifetime, cleanup racing with the thread, global `newvolserver` protocol detection shared across all servers, unchecked allocation of `stats64.ViceStatistics64_val`, and limited copying into fixed host/name buffers. Tests should cover initialization failures, partial connection failures returning `-2`, forced probes, 64-bit and old statistics fallbacks, partition listing fallback, cleanup after failed init, and handler invocation counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/fsprobe/fsprobe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/fsprobe/fsprobe.h -->
# sources/distributed-fs/openafs/src/fsprobe/fsprobe.h

## Purpose
Declares the public interface and result structures for the AFS FileServer probe facility.

## Important APIs, Types, And Functions
Defines `struct ProbeViceStatistics`, `struct fsprobe_ConnectionInfo`, and `struct fsprobe_ProbeResults`. Declares global `fsprobe_numServers`, `fsprobe_ConnInfo`, `fsprobe_Results`, and functions `fsprobe_Init`, `fsprobe_ForceProbeNow`, `fsprobe_Cleanup`, and `fsprobe_Wait`.

## Control Flow
The header documents the expected lifecycle: call `fsprobe_Init` with server sockets, probe interval, handler, and debug flag; inspect exported results from the handler after each sweep; optionally call `fsprobe_ForceProbeNow`; wait with `fsprobe_Wait`; and clean up with `fsprobe_Cleanup`.

## State And Persistence
The public globals expose live connection metadata and the latest probe result arrays. These are process-memory structures, not persisted data.

## Dependencies And Integration Points
The header includes socket, Rx, `afsint`, volser, and volume-interface definitions. It is installed as `afs/fsprobe.h` and used by monitoring code and `fsprobe_test`.

## Risks And Test Signals
The API exposes mutable globals, making synchronization and ownership unclear. `ProbeViceStatistics` embeds fixed `VOLMAXPARTS` disk slots and legacy 32-bit counters even though the implementation may down-convert 64-bit stats. Tests should compile external consumers, verify structure layout expectations, and exercise handler access to globals during probe updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/fsprobe/fsprobe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/fsprobe/fsprobe_callback.c -->
# sources/distributed-fs/openafs/src/fsprobe/fsprobe_callback.c

## Purpose
Implements minimal AFS callback server procedures so FileServers can treat the probe process like a cache manager while statistics are collected.

## Important APIs, Types, And Functions
Defines callback globals `afs_cb_inited` and `afs_cb_interface`, private `init_afs_cb`, and many `SRXAFSCB_*` RPC handlers: `CallBack`, `InitCallBackState`, `Probe`, `GetCE64`, `GetCE`, `GetLock`, `XStatsVersion`, `GetXStats`, `InitCallBackState2`, `WhoAreYou`, `InitCallBackState3`, `ProbeUuid`, `GetServerPrefs`, `GetCellServDB`, `GetCellByNum`, `GetLocalCell`, `GetCacheConfig`, and `TellMeAboutYourself`.

## Control Flow
Most handlers are no-op stubs returning success because fsprobe does not maintain real cache-manager state. `InitCallBackState2` and several cache/cell query procedures return `RXGEN_OPCODE` to signal unsupported calls. `WhoAreYou` and `TellMeAboutYourself` lazily initialize interface addresses and UUIDs, then return them. `ProbeUuid` lazily initializes and compares the supplied UUID against the process callback UUID.

## State And Persistence
The only persistent state is the generated callback UUID and local interface address list in `afs_cb_interface`. It is process-local and initialized once.

## Dependencies And Integration Points
These functions satisfy symbols expected by generated `afscbint.ss.c` and are dispatched by `RXAFSCB_ExecuteRequest` from the callback service created in `fsprobe_Init`.

## Risks And Test Signals
Because most RPCs return success without filling outputs, callers must tolerate probe-only semantics. Verbose logging blocks reference stale macro names in disabled code paths, so enabling them may not compile. Tests should cover callback service startup, `WhoAreYou`, `TellMeAboutYourself`, `ProbeUuid` match/mismatch, unsupported opcode returns, and FileServer compatibility during fsprobe polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/fsprobe/fsprobe_callback.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/fsprobe/fsprobe_test.c -->
# sources/distributed-fs/openafs/src/fsprobe/fsprobe_test.c

## Purpose
Provides an interactive/manual test driver for the fsprobe library.

## Important APIs, Types, And Functions
Defines `FS_Handler`, which prints current `fsprobe_Results`, and `main`, which resolves three hard-coded server names, initializes fsprobe, sleeps, then cleans up.

## Control Flow
`main` builds three `sockaddr_in` entries for `servername1`, `servername2`, and `servername3` on port 7000, calls `fsprobe_Init` with a 30-second interval and debugging enabled, waits ten minutes using `fsprobe_Wait`, then calls `fsprobe_Cleanup` and `rx_Finalize`. The handler iterates over three result entries and prints probe status, many counters, and disk partition summaries.

## State And Persistence
The program relies on fsprobe globals for all result state. It writes only console output.

## Dependencies And Integration Points
Links against `libfsprobe`, Rx, fsint, volser, util, and roken. It uses `hostutil_GetHostByName` to resolve test servers.

## Risks And Test Signals
The test is not self-contained: server names are placeholders and the handler hard-codes three servers regardless of `fsprobe_numServers`. It also prints only 26 disk slots even though `VOLMAXPARTS` can differ. Useful signals are mainly manual: successful connection to real FileServers, periodic handler output, partition data, forced cleanup, and failure behavior when names cannot resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/fsprobe/fsprobe_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/Makefile.in -->
# sources/distributed-fs/openafs/src/gtx/Makefile.in

## Purpose
Builds the OpenAFS gtx display-independent window toolkit, installs its public headers, and links several test programs.

## Important APIs, Types, And Functions
The default target builds `liboafs_gtx.la`, `libgtx.a`, and installs headers for curses, dumb, X11, frame, input, keymap, light/text objects, object dictionary, text circular buffers, and window abstractions. Test targets include `object_test`, `screen_test`, `curses_test`, `cb_test`, and `gtxtest`.

## Control Flow
The makefile compiles toolkit modules into libtool objects, links shared/static libraries against rxkad, fsint, cmd, util, opr, and lwp compatibility libraries, then links test binaries with curses and platform libraries. Install/dest targets copy `libgtx.a` and headers into configured AFS lib/include directories.

## State And Persistence
Build outputs include libtool artifacts, static library, test binaries, installed headers, and generated version files. Clean removes objects, libraries, tests, core files, and version output.

## Dependencies And Integration Points
GTX is a UI abstraction used by older OpenAFS tools/tests. It integrates curses, a dumb backend, a mostly stub X11 backend, object/frame/keymap infrastructure, and text buffers.

## Risks And Test Signals
The toolkit is legacy C with K&R-style tests and backend-specific dependencies. Test signals are successful builds with and without curses/X11 headers, header installation, static/shared link success, and manual test execution in a terminal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/X11windows.c -->
# sources/distributed-fs/openafs/src/gtx/X11windows.c

## Purpose
Defines the gtx X11 window backend interface, but the implementation is effectively a stub.

## Important APIs, Types, And Functions
Exports `X11_gwinops`, `gator_X11_gwinbops`, `gator_X11gwin_init`, `gator_X11gwin_create`, `gator_X11gwin_cleanup`, and standard window operations for box, clear, destroy, display, draw line/rectangle/char/string, invert, getchar, getdimensions, and wait.

## Control Flow
Initialization only records the debug flag. Create always returns `NULL`. Most operations log when debugging is enabled and return success without drawing; input/dimension/wait functions return `-1`. Mapping macros for pixel-to-column/line are identity but unused for real drawing.

## State And Persistence
The only module state is global `X11_debug`. No X11 display, window, graphics context, or event state is created.

## Dependencies And Integration Points
The file satisfies the gtx backend operation table expected by the generic window layer and `gtxX11win.h`, allowing builds to link even without a functional X11 implementation.

## Risks And Test Signals
Any caller expecting a real X11 backend will fail at create time or get silent no-op drawing. Tests should assert that X11 create returns `NULL`, debug logs are sane, and higher-level code handles unavailable backends gracefully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/X11windows.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/cb_test.c -->
# sources/distributed-fs/openafs/src/gtx/cb_test.c

## Purpose
Manual test program for the gator text circular buffer package.

## Important APIs, Types, And Functions
The K&R-style `main` calls `gator_textcb_Init`, `gator_textcb_Create`, `gator_textcb_Write`, `gator_textcb_BlankLine`, and `gator_textcb_Delete`. It inspects `struct gator_textcb_hdr` and `struct gator_textcb_entry` fields directly.

## Control Flow
The program prompts for debug mode, creates a 100-entry buffer with 80 characters per entry, performs several writes including highlighted and bulk text, inserts blank lines, prints buffer metadata and entries, pauses for user input, writes many small entries to force wraparound, prints all entries again, then deletes the buffer and exits.

## State And Persistence
All state is heap memory owned by the circular buffer plus console input/output. No files are written.

## Dependencies And Integration Points
Linked by `gtx/Makefile.in` against the gtx library. It exercises the text circular buffer implementation used by text objects.

## Risks And Test Signals
It is interactive, uses `scanf` without robust input validation, and reaches into internal structures, so it is more diagnostic than automated. Useful signals are successful initialization, correct wraparound metadata, preserved highlight/inversion fields, clean deletion, and no crashes under repeated writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/cb_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/curses_test.c -->
# sources/distributed-fs/openafs/src/gtx/curses_test.c

## Purpose
Simple standalone curses smoke test used to verify basic curses availability and behavior.

## Important APIs, Types, And Functions
The K&R-style `main` calls `initscr`, `scrollok`, `clear`, `addstr`, `refresh`, `box`, `standout`, `standend`, and `endwin`.

## Control Flow
The program initializes curses, enables scrolling, clears the screen, writes a normal string, refreshes, draws a box on the standard screen, writes a standout string, refreshes again, ends standout mode, and restores the terminal with `endwin`.

## State And Persistence
It temporarily mutates terminal/curses state and writes to the terminal only.

## Dependencies And Integration Points
Built by `gtx/Makefile.in` when tests are requested and depends on configured curses headers/libraries. It is independent of the higher-level gtx window abstraction.

## Risks And Test Signals
The test is manual and should be run in a real terminal; failure to call `endwin` after a crash can leave terminal modes altered. Signals are successful link, visible text/box output, standout mode rendering, and terminal restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/curses_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/curseswindows.c -->
# sources/distributed-fs/openafs/src/gtx/curseswindows.c

## Purpose
Implements the functional curses backend for the gtx window abstraction, mapping generic gwin operations to curses windows and terminal input.

## Important APIs, Types, And Functions
Exports `curses_gwinops`, `gator_curses_gwinbops`, `gator_cursesgwin_init`, `gator_cursesgwin_create`, `gator_cursesgwin_cleanup`, and operations for box, clear, destroy, display, draw line/rectangle/char/string, invert, getchar, wait, and getdimensions. Private data is `struct gator_cursesgwin` from `gtxcurseswin.h`.

## Control Flow
Initialization calls `initscr`, allocates private data for the global base window, sets default character geometry and box characters, fills `gator_basegwin`, enables raw mode, creates a frame, and clears the screen. Window creation allocates a generic `gwin`, allocates curses-private data, creates a curses `WINDOW` with `newwin`, initializes frame/private fields, and returns the new window. Display clears the curses window, renders the gtx frame, and refreshes. Character/string drawing maps coordinates directly, optionally enters standout mode, writes content, and exits standout. Wait spins on `LWP_WaitForKeystroke`; getchar reads from stdin; dimensions use `getmaxyx`.

## State And Persistence
State includes global `curses_debug`, the global `gator_basegwin`, curses terminal state, allocated `gwin`/private structs, curses `WINDOW` objects, and frames. Cleanup restores non-raw mode and calls `endwin`, but destroy only deletes the curses window and does not free the surrounding structs.

## Dependencies And Integration Points
Depends on curses/ncurses headers, LWP keyboard waiting, `gtxobjects`, `gtxframe`, and the generic `gtxwindows` operation table. It is the main terminal backend for gtx tools.

## Risks And Test Signals
Coordinate units are treated as curses rows/columns despite generic fields being described as pixels. Several drawing operations are no-ops, allocation cleanup is incomplete on destroy, and blocking input depends on LWP behavior. Tests should cover init/cleanup terminal restoration, create failure cleanup, box/clear/display/draw string highlighting, dimension reads, wait/getchar behavior, and repeated create/destroy leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/gtx/curseswindows.c -->
