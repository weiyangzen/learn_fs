# Group Research: subset-b-009230

This grouped report covers the fio Windows POSIX compatibility layer, oslib portability helpers, parser/profile helpers, and several runtime synchronization/submission helpers. Sections are source-tree aligned and marker delimited for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix.c -->
# sources/test-tools/fio/os/windows/posix.c

Purpose: implements the subset of POSIX/Linux APIs that fio needs when built with MinGW or Microsoft Windows tooling. It is intentionally narrow: error conversion, time, dynamic loading, memory mapping, shared memory, directory iteration, polling, syslog, resource usage, and process/socket handoff behavior are emulated only far enough for fio's Windows port.

Important APIs/functions: `win_to_posix_error()` maps many Win32 `ERROR_*` values to `errno`; `sysconf()`, `gettimeofday()`, `ctime_r()`, `sigaction()`, `lstat()`, `fsync()`, `pread()`, `pwrite()`, `poll()`, `opendir()`/`readdir()`/`closedir()`, `mmap()`/`munmap()`/`msync()`/`mlock()`/`munlock()`, System V-style `shmget()`/`shmat()`/`shmdt()`/`shmctl()`, `getrusage()`, `nice()`, `basename()`, and `dlopen()`/`dlsym()`/`dlclose()` are the main compatibility surface. `windows_create_job()` and `windows_handle_connection()` implement fio server child-process handling with job objects, named pipes, and `WSADuplicateSocket()`.

Control flow: most wrappers translate a POSIX call into a direct Win32 API call and set `errno` through `win_to_posix_error()` on failure. `mmap()` branches between anonymous `VirtualAlloc()` and file-backed `CreateFileMapping()`/`MapViewOfFile()`. The directory API stores a search handle in `DIR` and lazily starts `FindFirstFileA()` on first `readdir()`. `poll()` builds `fd_set`s and delegates to `select()`. The process handoff path creates a child with `--server-internal=<pipe>`, duplicates the socket to that child, writes `WSAPROTOCOL_INFO` through a named pipe, and monitors for a "connected" message or process exit.

State and persistence: global state includes `dl_error`, `log_file`, `nFileMappings`, and a fixed `fileMappings[1024]` array. `syslog()` persists messages to `syslog.txt` in the current working directory. Shared memory handles are retained in the fixed mapping table until `IPC_RMID`, but `shmctl()` only invalidates the table entry and does not close the Windows handle. Several functions return static buffers (`basename()`, `readdir()`).

Dependencies and integration: depends on Windows headers, Winsock, CRT file descriptors (`_get_osfhandle`, `_lseeki64`, `_write`, `_telli64`), fio logging/debug symbols, `mtime_since_now()`, `fio_gettime()`, `os-windows.h`, and `lib/hweight.h`. The shim headers in `os/windows/posix/include` declare much of this surface for Windows builds.

Risks: this is not a full POSIX implementation. `fork()`, `setsid()`, `waitpid()`, `readv()`, `setuid()`, `setgid()`, `geteuid()`, and `posix_madvise()` are stubs. `fcntl()` currently returns success without changing nonblocking state. Some time/resource conversions collapse subsecond precision. `mmap()` splits 64-bit sizes/offsets incorrectly by 16-bit shifts rather than conventional high/low DWORD arithmetic, so large mappings deserve extra scrutiny. `syslog()` uses `va_list` after `_vscprintf()` without copying or restarting it, which is risky on ABIs where `va_list` is consumed. The fixed shared-memory table has no bounds check or synchronization.

Test signals: Windows fio builds should exercise server mode, network/client mode, directory traversal, mmap-backed allocations, shared memory paths, fsync/pread/pwrite correctness, and poll/readiness behavior. Negative tests should verify errno mapping and unsupported-call handling rather than assuming full POSIX behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix.h -->
# sources/test-tools/fio/os/windows/posix.h

Purpose: minimal umbrella header for Windows POSIX compatibility declarations that are not provided by the local include shims.

Important APIs/types: defines `clockid_t` as `int` and declares `inet_aton()` plus `win_to_posix_error(DWORD)`. The declarations support Windows code that expects Unix-ish networking and errno conversion helpers.

Control flow and state: no executable logic or state lives here; it only makes compatibility symbols visible to other compilation units.

Dependencies and integration: assumes Windows `DWORD` is already visible through included Windows headers. It is paired with `posix.c` and the `os/windows/posix/include` shim headers.

Risks: because it does not include the Windows header that defines `DWORD` or the networking header that defines `struct in_addr`, including this header in isolation may fail. It is meant for the existing fio include order.

Test signals: successful Windows compilation is the main signal; include-order tests would catch missing transitive definitions.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/arpa/inet.h -->
# sources/test-tools/fio/os/windows/posix/include/arpa/inet.h

Purpose: Windows replacement for the POSIX `<arpa/inet.h>` subset used by fio.

Important APIs/types: includes `<ws2tcpip.h>` and `<inttypes.h>`, typedefs `socklen_t` and `in_addr_t` to `int`, maps `EAI_SYSTEM` to `EAI_FAIL`, and declares `inet_network()`.

Control flow and state: header-only declarations and macros; runtime behavior is in Winsock and `posix.c`.

Dependencies and integration: lets fio code include `<arpa/inet.h>` on Windows while still receiving Winsock definitions such as `inet_pton()` and address structures. `inet_network()` is implemented in `posix.c`; `inet_aton()` may come from `oslib/inet_aton.c` or `posix.h`.

Risks: `in_addr_t` is normally an unsigned IPv4 address type, but this shim uses `int`; callers that rely on exact signedness or width may behave differently. The `EAI_SYSTEM` mapping discards the Unix convention of consulting `errno`.

Test signals: compile Windows network paths and run server/client address parsing with IPv4 literals and failing `getaddrinfo()` cases.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/arpa/inet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/asm/types.h -->
# sources/test-tools/fio/os/windows/posix/include/asm/types.h

Purpose: tiny Linux compatibility header for code that expects `<asm/types.h>` integer aliases.

Important APIs/types: defines `__u16`, `__u32`, and `__u64` as unsigned 16/32/64-bit-like C integer aliases.

Control flow and state: no logic or state; compile-time type compatibility only.

Dependencies and integration: supports fio code and imported Linux-style headers that use `__u*` names on Windows.

Risks: it does not define signed aliases or the full Linux UAPI type set. Exact widths rely on Windows compiler assumptions for `unsigned short`, `unsigned int`, and `unsigned long long`.

Test signals: Windows compilation of any Linux-UAPI-like structures using these aliases.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/asm/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/dirent.h -->
# sources/test-tools/fio/os/windows/posix/include/dirent.h

Purpose: declares a minimal POSIX `dirent` API for Windows builds.

Important APIs/types: `struct dirent` carries `d_ino` and `d_name[MAX_PATH]`; `struct dirent_ctx` stores a Win32 `HANDLE find_handle` and directory name; `DIR` aliases that context. It declares `opendir()`, `readdir()`, and `closedir()`.

Control flow and state: implemented by `posix.c` using `CreateFileA()`, `FindFirstFileA()`, `FindNextFile()`, and `FindClose()`. `readdir()` returns a static `struct dirent`, so results are overwritten by the next call.

Dependencies and integration: includes `<winsock2.h>` to get Windows types and `MAX_PATH`. It enables fio code that scans directories to compile on Windows.

Risks: not thread-safe because of static `readdir()` storage; paths longer than `MAX_PATH` are truncated or unsupported; `d_ino` is always zero. It is sufficient for listing names, not metadata-rich directory traversal.

Test signals: Windows directory scans with existing, missing, inaccessible, and long-path directories.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/dirent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/dlfcn.h -->
# sources/test-tools/fio/os/windows/posix/include/dlfcn.h

Purpose: provides a small `<dlfcn.h>` facade for dynamic loading on Windows.

Important APIs/types: defines `RTLD_LAZY` and declares `dlopen()`, `dlclose()`, `dlsym()`, and `dlerror()`.

Control flow and state: `posix.c` maps these to `LoadLibrary()`, `FreeLibrary()`, `GetProcAddress()`, and a global string pointer for the last error.

Dependencies and integration: supports fio code that loads engines or optional modules through Unix-style dynamic-loader calls.

Risks: `mode` is ignored; `dlerror()` returns coarse static strings, not detailed Win32 errors; the global error pointer is not thread-local. `LoadLibrary()` path semantics differ from POSIX `dlopen()`.

Test signals: load a known DLL, resolve an exported symbol, fail a missing symbol, and ensure caller paths handle the simplified error reporting.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/dlfcn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/libgen.h -->
# sources/test-tools/fio/os/windows/posix/include/libgen.h

Purpose: declares the `basename()` compatibility function for Windows.

Important APIs/types: single API `char *basename(char *path)`.

Control flow and state: implemented in `posix.c` by searching for the last slash or backslash and copying into a static `MAX_PATH` buffer.

Dependencies and integration: lets Unix code include `<libgen.h>` and compile on Windows.

Risks: implementation returns static storage, is not thread-safe, and truncates to `MAX_PATH - 1`. Unlike some POSIX implementations, it does not modify the input path.

Test signals: path cases with `/`, `\`, trailing separators, empty strings, and long names.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/libgen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/netdb.h -->
# sources/test-tools/fio/os/windows/posix/include/netdb.h

Purpose: placeholder `<netdb.h>` for Windows fio builds.

Important APIs/types: none; it only satisfies include presence.

Control flow and state: no logic or state.

Dependencies and integration: used where source files include `<netdb.h>` unconditionally while actual needed networking declarations come from Winsock headers elsewhere.

Risks: any future code expecting `struct addrinfo`, `getaddrinfo()`, or `gai_strerror()` from this header will fail unless another header provides them first.

Test signals: compilation of current Windows networking code; add include-coverage tests if new netdb APIs are introduced.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/netdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/netinet/in.h -->
# sources/test-tools/fio/os/windows/posix/include/netinet/in.h

Purpose: placeholder `<netinet/in.h>` shim for Windows.

Important APIs/types: includes `<inttypes.h>` and `<sys/un.h>`, but declares no IPv4/IPv6 structs itself.

Control flow and state: header-only compatibility; no runtime behavior.

Dependencies and integration: relies on other Windows networking headers, especially `<arpa/inet.h>` and Winsock, to provide real socket address definitions.

Risks: unusually minimal for `<netinet/in.h>`; code that includes only this header and expects `struct sockaddr_in`, `IPPROTO_TCP`, or byte-order helpers may fail.

Test signals: Windows compile paths that include network headers in different orders.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/netinet/in.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/netinet/tcp.h -->
# sources/test-tools/fio/os/windows/posix/include/netinet/tcp.h

Purpose: empty `<netinet/tcp.h>` shim for Windows fio builds.

Important APIs/types: none.

Control flow and state: no logic or state.

Dependencies and integration: satisfies include directives when TCP constants are obtained through Winsock or not used in Windows code paths.

Risks: missing constants such as `TCP_NODELAY` if future code expects this header to provide them.

Test signals: Windows build coverage of network code that includes `<netinet/tcp.h>`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/netinet/tcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/poll.h -->
# sources/test-tools/fio/os/windows/posix/include/poll.h

Purpose: declares a minimal `poll()` interface for Windows.

Important APIs/types: includes `<winsock2.h>`, typedefs `nfds_t` as `int`, and declares `poll(struct pollfd[], nfds_t, int)`.

Control flow and state: `posix.c` implements `poll()` by translating event masks into `select()` read/write/exception sets and writing `revents`.

Dependencies and integration: depends on Winsock's `struct pollfd` and socket constants. Used by fio client/server or network paths.

Risks: `select()` receives `nfds` even though Windows ignores that value; only `POLLIN`, `POLLOUT`, and exception-as-`POLLHUP` are modeled. File-descriptor polling is not supported, only sockets.

Test signals: network readiness tests on readable, writable, closed, invalid, and timeout sockets.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/poll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/semaphore.h -->
# sources/test-tools/fio/os/windows/posix/include/semaphore.h

Purpose: placeholder POSIX semaphore header for Windows.

Important APIs/types: none.

Control flow and state: no logic; it exists to satisfy includes.

Dependencies and integration: fio likely uses its own semaphore abstraction (`fio_sem`) on Windows rather than POSIX `sem_t` APIs from this header.

Risks: any code that expects `sem_t`, `sem_init()`, or related APIs from this header will not compile.

Test signals: Windows build coverage after any new semaphore usage.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/semaphore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/sys/ioctl.h -->
# sources/test-tools/fio/os/windows/posix/include/sys/ioctl.h

Purpose: empty Windows `<sys/ioctl.h>` compatibility shim.

Important APIs/types: none; the source comment says the file only needs to exist on Windows and is otherwise unused.

Control flow and state: no runtime behavior.

Dependencies and integration: prevents build failures from unconditional includes in portable source.

Risks: not a real ioctl interface. Future Windows code expecting ioctl request macros or function declarations must add them or gate the include.

Test signals: compile-only coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/sys/ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/sys/ipc.h -->
# sources/test-tools/fio/os/windows/posix/include/sys/ipc.h

Purpose: placeholder System V IPC header for Windows.

Important APIs/types: none in this file; related IPC constants and typedefs are in `sys/shm.h`.

Control flow and state: no logic or state.

Dependencies and integration: satisfies includes for code paths that also include `sys/shm.h`.

Risks: not a complete IPC header; callers expecting `IPC_CREAT`, `key_t`, or permission structures from this header alone will fail.

Test signals: Windows build and include-order checks for shared-memory users.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/sys/ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/sys/mman.h -->
# sources/test-tools/fio/os/windows/posix/include/sys/mman.h

Purpose: declares the memory-mapping subset used by fio on Windows.

Important APIs/types: defines `PROT_*`, `MAP_*`, `MAP_FAILED`, `MS_*`, and declares `mmap()`, `munmap()`, `msync()`, `mlock()`, `munlock()`, and `posix_madvise()`.

Control flow and state: implementations in `posix.c` translate anonymous mappings to `VirtualAlloc()` and file mappings to `CreateFileMapping()`/`MapViewOfFile()`, with cleanup through `UnmapViewOfFile()` or `VirtualFree()`.

Dependencies and integration: included by fio memory allocation and synchronization code that wants Unix APIs. `rwlock.c` uses `mmap()`/`munmap()` through the OS abstraction.

Risks: constants are local shim values and not ABI-compatible with Unix. `MAP_FAILED` is `NULL`, unlike POSIX `(void *)-1`, so callers must be compatible with this behavior. `MAP_FIXED` and several flags are declared but not fully implemented.

Test signals: Windows tests for anonymous mapping, file mapping, sync, lock/unlock, and failure paths.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/sys/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/sys/resource.h -->
# sources/test-tools/fio/os/windows/posix/include/sys/resource.h

Purpose: exposes the small `getrusage()` surface fio needs on Windows.

Important APIs/types: defines `RUSAGE_SELF` and `RUSAGE_THREAD`; declares `struct rusage` with user/system time and a few counters; declares `getrusage()`.

Control flow and state: `posix.c` fills `ru_utime` and `ru_stime` using `GetProcessTimes()` or `GetThreadTimes()` and zeroes the structure first.

Dependencies and integration: supports fio CPU accounting paths that use `getrusage()` cross-platform.

Risks: only CPU time is meaningfully filled; context-switch and fault counters remain zero. Time conversion truncates to whole seconds.

Test signals: compare monotonic nondecreasing user/system times for process and thread usage on Windows.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/sys/resource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/sys/shm.h -->
# sources/test-tools/fio/os/windows/posix/include/sys/shm.h

Purpose: declares a limited System V shared-memory facade for Windows.

Important APIs/types: defines `IPC_RMID`, `IPC_CREAT`, `IPC_PRIVATE`; typedefs `uid_t`, `gid_t`, `shmatt_t`, and `key_t`; declares `ipc_perm`, `shmid_ds`, and `shmget()`/`shmat()`/`shmdt()`/`shmctl()`.

Control flow and state: `posix.c` backs `shmget()` with pagefile-backed `CreateFileMapping()`, stores handles in a fixed global array, maps them with `MapViewOfFile()`, commits pages with `VirtualAlloc()`, and unmaps with `UnmapViewOfFile()`.

Dependencies and integration: used by fio code expecting process-shared memory on Unix-like systems while building on Windows.

Risks: permissions, keys, attach counts, ownership, and most `shmctl()` commands are not implemented. The fixed handle table has no bounds checks, no synchronization, and no true key reuse semantics.

Test signals: Windows shared-memory allocation/attach/detach lifecycle tests and stress tests around many segments.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/sys/shm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/sys/socket.h -->
# sources/test-tools/fio/os/windows/posix/include/sys/socket.h

Purpose: empty `<sys/socket.h>` shim for Windows.

Important APIs/types: none; socket definitions are expected from Winsock headers.

Control flow and state: no runtime behavior.

Dependencies and integration: satisfies Unix include paths in fio networking code.

Risks: not sufficient for code that includes only `<sys/socket.h>` and expects POSIX socket APIs or constants.

Test signals: Windows network build coverage with current include ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/sys/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/sys/uio.h -->
# sources/test-tools/fio/os/windows/posix/include/sys/uio.h

Purpose: declares vector I/O types for Windows fio builds.

Important APIs/types: `struct iovec` contains `iov_base` and `iov_len`; declares `readv()` and `writev()`.

Control flow and state: `posix.c` stubs `readv()` with `ENOSYS`; `writev()` loops over vectors and sends each segment on a Winsock socket.

Dependencies and integration: used by network code that writes scatter/gather buffers. Includes `<unistd.h>` for `ssize_t`.

Risks: `writev()` is socket-only and does not preserve atomic vector-write semantics. `readv()` is unavailable on Windows. Callers must avoid general file descriptor vector I/O.

Test signals: socket writev behavior with multiple vectors and error injection; verify read paths do not require `readv()`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/sys/uio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/sys/un.h -->
# sources/test-tools/fio/os/windows/posix/include/sys/un.h

Purpose: minimal Unix-domain socket type shim for Windows.

Important APIs/types: typedefs `sa_family_t` and `in_port_t` to `int`; defines `struct sockaddr_un` with `sun_family` and `sun_path[260]`.

Control flow and state: no implementation; type compatibility only.

Dependencies and integration: included indirectly by `netinet/in.h` and supports code that references Unix-domain socket structures.

Risks: does not implement Unix-domain socket behavior. `sun_path` length is Windows `MAX_PATH`-like and may not match Unix expectations.

Test signals: compile-only unless Windows code starts using Unix socket emulation.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/sys/un.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/sys/wait.h -->
# sources/test-tools/fio/os/windows/posix/include/sys/wait.h

Purpose: minimal wait-status compatibility header for Windows.

Important APIs/types: defines `WIFSIGNALED`, `WIFEXITED`, `WTERMSIG`, and `WEXITSTATUS` as zero-valued macros, `WNOHANG` as `1`, and declares `waitpid()`.

Control flow and state: `posix.c` implements `waitpid()` as an `ENOSYS` stub.

Dependencies and integration: lets Unix-oriented process code compile on Windows while fio uses alternate child-process handling where needed.

Risks: wait status macros never report success, signals, or exit status. Any logic relying on real wait semantics will misbehave.

Test signals: Windows process code should avoid depending on `waitpid()`; compile paths are the primary signal.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/sys/wait.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/syslog.h -->
# sources/test-tools/fio/os/windows/posix/include/syslog.h

Purpose: declares a tiny syslog facade for Windows.

Important APIs/types: declares `syslog()`, `openlog()`, and `closelog()` and defines a small set of `LOG_*` priority/option/facility constants.

Control flow and state: `posix.c` lazily opens `syslog.txt` and writes formatted messages with `WriteFile()`.

Dependencies and integration: supports code that logs through syslog APIs without requiring Windows Event Log integration.

Risks: the header declares `syslog()` as returning `int`, while the implementation returns `void`; this is a type mismatch. Priorities, facilities, options, identity strings, and PID behavior are ignored. The file handle is global and unsynchronized.

Test signals: Windows compile warnings should be checked for prototype mismatch; runtime should confirm messages reach `syslog.txt` and failures do not crash.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/os/windows/posix/include/syslog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/asprintf.c -->
# sources/test-tools/fio/oslib/asprintf.c

Purpose: fallback implementations of GNU `vasprintf()` and `asprintf()` for platforms lacking them.

Important APIs/functions: under `!CONFIG_HAVE_VASPRINTF`, `vasprintf()` computes required length using a copied `va_list`, allocates the buffer, stores it in `*strp`, and formats into it. Under `!CONFIG_HAVE_ASPRINTF`, `asprintf()` wraps `vasprintf()` with `va_start()`/`va_end()`.

Control flow and state: no persistent state. Allocation failure returns `-1`; `vsnprintf()` errors propagate.

Dependencies and integration: includes `oslib/asprintf.h`; used by other fio portability code such as Linux zoned-device sysfs path construction.

Risks: `*strp` is assigned even on allocation failure as `NULL`. The fallback assumes `vsnprintf(NULL, 0, ...)` is supported by the C library. Callers own the returned allocation.

Test signals: build on systems without native `asprintf`, format strings with zero-length, long, and invalid conversions, and verify allocation ownership.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/asprintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/asprintf.h -->
# sources/test-tools/fio/oslib/asprintf.h

Purpose: conditional declarations for fio's `asprintf()`/`vasprintf()` fallbacks.

Important APIs/types: includes `<stdarg.h>` and declares `vasprintf()` when `CONFIG_HAVE_VASPRINTF` is absent and `asprintf()` when `CONFIG_HAVE_ASPRINTF` is absent.

Control flow and state: no logic or state.

Dependencies and integration: paired with `oslib/asprintf.c`; consumers include this header to get portable declarations without conflicting with libc-provided functions.

Risks: configuration macros must match the platform headers and build objects, or duplicate/missing declarations can occur.

Test signals: configure/build matrix on platforms with and without GNU `asprintf()`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/asprintf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/blkzoned.h -->
# sources/test-tools/fio/oslib/blkzoned.h

Purpose: declares fio's zoned block device OS abstraction and supplies stubs when native zoned-device support is unavailable.

Important APIs/functions: public functions cover zoned model discovery, zone reporting, write-pointer reset/move/finish, and max open/active zone limits. Under `CONFIG_HAS_BLKZONED`, implementations are external, normally `linux-blkzoned.c`. Without support, inline stubs return `-EIO` or `-ENODEV`, except block devices report `ZBD_NONE` to allow emulation.

Control flow and state: no persistent state in the header; behavior is compile-time selected.

Dependencies and integration: includes `zbd_types.h` and uses `struct thread_data`, `struct fio_file`, `struct zbd_zone`, and `enum zbd_zoned_model`. It integrates fio's generic ZBD logic with OS-specific Linux ioctls.

Risks: unsupported-platform stubs intentionally make most operations fail. The `blkzoned_get_max_active_zones()` stub parameter name is `max_open_zones`, a harmless but confusing mismatch.

Test signals: build both with and without `CONFIG_HAS_BLKZONED`; verify non-Linux behavior reports no native zones while Linux ZBD tests use real implementations.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/blkzoned.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/getopt.h -->
# sources/test-tools/fio/oslib/getopt.h

Purpose: portable `getopt_long_only()` declaration and `struct option` fallback.

Important APIs/types: when `CONFIG_GETOPT_LONG_ONLY` is set it delegates to system `<getopt.h>`. Otherwise it defines `struct option`, `no_argument`, `required_argument`, `optional_argument`, and declares `getopt_long_only()`.

Control flow and state: header-only compile-time selection.

Dependencies and integration: paired with `getopt_long.c`; used by fio command-line parsing on platforms without GNU getopt extensions.

Risks: fallback intentionally implements only a common subset, so code must not depend on unsupported GNU features.

Test signals: CLI option parsing tests on systems with and without native `getopt_long_only()`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/getopt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/getopt_long.c -->
# sources/test-tools/fio/oslib/getopt_long.c

Purpose: klibc-derived fallback implementation of a common subset of `getopt_long_only()`.

Important APIs/functions: defines globals `optarg`, `optind`, `opterr`, and `optopt`; internal `option_matches()` checks exact or unique prefix long-option matches; `getopt_long_only()` parses long `--name[=arg]` options and short `-x` clusters with required/optional arguments.

Control flow and state: private static `pvt` remembers the current character pointer, previous `optstring`, and previous `argv` to reset parsing when a different parse begins. Long option parsing increments `optind`, finds exact or unique short matches, handles `flag` vs `val`, and populates `longindex`. Short option parsing advances within a cluster and handles missing arguments with `:` or `?`.

Dependencies and integration: includes the fallback `getopt.h`; consumed by fio CLI setup on platforms lacking native support.

Risks: documented limitations include no option reordering, no `-W foo`, and no special first `optstring` character `-`. Globals are process-wide and not thread-safe. Ambiguous long prefixes return `?`.

Test signals: parse exact long options, unique/ambiguous abbreviations, `--`, missing required arguments, optional arguments, short clusters, and repeated parses with different `argv`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/getopt_long.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/inet_aton.c -->
# sources/test-tools/fio/oslib/inet_aton.c

Purpose: fallback `inet_aton()` implementation.

Important APIs/functions: `inet_aton(const char *cp, struct in_addr *inp)` delegates to `inet_pton(AF_INET, cp, inp)`.

Control flow and state: no state; direct conversion wrapper returning the `inet_pton()` result.

Dependencies and integration: includes `inet_aton.h`, which pulls in `<arpa/inet.h>`. Supports platforms where `inet_aton()` is missing but `inet_pton()` exists.

Risks: historical `inet_aton()` accepted some shorthand IPv4 forms that `inet_pton()` rejects. The return value is compatible for success/failure, but accepted syntax may differ.

Test signals: IPv4 literal parsing, invalid address rejection, and compatibility expectations for shorthand addresses.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/inet_aton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/inet_aton.h -->
# sources/test-tools/fio/oslib/inet_aton.h

Purpose: declaration for fio's `inet_aton()` fallback.

Important APIs/types: includes `<arpa/inet.h>` and declares `inet_aton(const char *, struct in_addr *)`.

Control flow and state: no logic or state.

Dependencies and integration: paired with `inet_aton.c`; also overlaps with Windows `posix.h` declaration.

Risks: duplicate declarations must agree with platform headers and configuration. This header should only be used when the fallback is needed or harmless.

Test signals: compile matrix with native and fallback `inet_aton()`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/inet_aton.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/libmtd.c -->
# sources/test-tools/fio/oslib/libmtd.c

Purpose: imported mtd-utils library code used by fio for Linux Memory Technology Device discovery and operations.

Important APIs/functions: public APIs include `libmtd_open()`, `libmtd_close()`, `mtd_dev_present()`, `mtd_get_info()`, `mtd_get_dev_info()`/`mtd_get_dev_info1()`, `mtd_lock()`, `mtd_unlock()`, `mtd_erase()`, `mtd_regioninfo()`, `mtd_is_locked()`, `mtd_torture()`, `mtd_is_bad()`, `mtd_mark_bad()`, `mtd_read()`, `mtd_write()`, `mtd_read_oob()`, `mtd_write_oob()`, `mtd_write_img()`, and `mtd_probe_node()`. Internal helpers read sysfs attributes, parse major/minor files, convert device type strings, validate eraseblock offsets, and probe 64-bit ioctl availability.

Control flow: `libmtd_open()` constructs `/sys/class/mtd/...` path patterns and checks sysfs support; if unsupported, it falls back to legacy `/proc/mtd` behavior. Discovery scans sysfs `mtdX` directories, reads attributes such as `name`, `type`, `erasesize`, `writesize`, `subpagesize`, `oobsize`, and flags, and populates `mtd_dev_info`. Operation functions validate eraseblock numbers and offsets before issuing Linux MTD ioctls such as `MEMLOCK`, `MEMUNLOCK`, `MEMERASE64`/`MEMERASE`, `MEMGETREGIONINFO`, `MEMISLOCKED`, `MEMGETBADBLOCK`, `MEMSETBADBLOCK`, `MEMWRITE`, and OOB read/write variants. 64-bit ioctl support is discovered lazily by trying the 64-bit ioctl and falling back on `ENOTTY`.

State and persistence: `struct libmtd` stores allocated path patterns and a cached `offs64_ioctls` state. Operations persistently modify hardware state: eraseblocks may be erased, locked/unlocked, marked bad, written, or tortured with patterns.

Dependencies and integration: depends on Linux MTD UAPI (`<mtd/mtd-user.h>`), sysfs, `/proc/mtd` legacy support, `libmtd_int.h`, `libmtd_common.h`, and xalloc wrappers. fio uses it for MTD-aware test targets.

Risks: many functions are destructive by design. `mtd_torture()` appears to return `-1` even after a successful torture pass, which is suspicious despite logging success. `mtd_read()` loops while `rd < len` but calls `read(fd, buf, len)` each time rather than advancing `buf` and shrinking the remaining count, risking overwritten buffers or infinite loops on short reads. Sysfs parsing assumes small bounded files and exact kernel formats. Hardware operations require correct privileges and real devices.

Test signals: unit tests can mock sysfs/proc parsing, but integration needs MTD devices or loopback/simulated MTD. Critical tests should cover 64-bit ioctl fallback, bad-block operations, OOB bounds validation, alignment checks, and the `mtd_torture()` return contract.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/libmtd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/libmtd.h -->
# sources/test-tools/fio/oslib/libmtd.h

Purpose: public API and data model for fio's imported MTD library.

Important APIs/types: defines `MTD_NAME_MAX`, `MTD_TYPE_MAX`, opaque `libmtd_t`, `struct mtd_info`, and `struct mtd_dev_info`. Declares discovery APIs, eraseblock lock/unlock/erase/region/lock-status APIs, bad-block APIs, raw and OOB read/write APIs, image-write helper, and node probing.

Control flow and state: no implementation; it defines the contract implemented by `libmtd.c` and `libmtd_legacy.c`. The API passes an opaque library descriptor plus caller-owned `mtd_dev_info` structs and open file descriptors.

Dependencies and integration: C++ compatible extern block; includes `<stdint.h>` and forward-declares `struct region_info_user`. Consumers are expected to include Linux MTD headers where concrete ioctl structs are needed.

Risks: many APIs are destructive and require a valid MTD fd plus accurate eraseblock geometry. The public comments are important because misuse can erase or mark bad blocks. `mtd_lock()`/`mtd_unlock()` comments mention a descriptor parameter that is not actually in the signature.

Test signals: compile consumers against the header and run integration tests for each operation on controlled MTD devices.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/libmtd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/libmtd_common.h -->
# sources/test-tools/fio/oslib/libmtd_common.h

Purpose: shared support macros and helpers for imported MTD utility code.

Important APIs/types: requires `PROGRAM_NAME`; defines `MIN`, `MAX`, `ALIGN`, typed min/max GNU statement expressions, `O_CLOEXEC` fallback, `PRIxoff_t`/`PRIdoff_t`, logging macros (`normsg`, `errmsg`, `sys_errmsg`, `warnmsg`), `is_power_of_2()`, `simple_strtoX()` conversion wrappers, and `common_print_version()`. It includes `libmtd_xalloc.h`.

Control flow and state: mostly macros; error macros print to `stderr` and return `-1`, while `*_die` variants exit. `simple_strtoX` inline helpers set an error flag if conversion leaves trailing text.

Dependencies and integration: used by `libmtd.c` and `libmtd_legacy.c`; assumes GNU C extensions (`__typeof__`, statement expressions) and libc feature macros.

Risks: macros evaluate arguments carefully in some places but still expose global names like `min`. Error handling prints directly rather than integrating with fio's normal logging. The required `PROGRAM_NAME` macro must be set before inclusion.

Test signals: build with compilers supporting GNU extensions; exercise parse and logging paths in MTD tests.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/libmtd_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/libmtd_int.h -->
# sources/test-tools/fio/oslib/libmtd_int.h

Purpose: private MTD library internals shared between sysfs and legacy implementations.

Important APIs/types: defines `PROGRAM_NAME`, sysfs path fragment constants, 64-bit ioctl support states, private `struct libmtd`, and legacy fallback prototypes.

Control flow and state: `struct libmtd` holds allocated sysfs path patterns, a `sysfs_supported` bit, and a cached two-bit `offs64_ioctls` state initialized as unknown then updated by runtime ioctl probing.

Dependencies and integration: included by `libmtd.c` and `libmtd_legacy.c`; imports the public types from `libmtd.h` in implementation files.

Risks: private layout is cast from opaque `libmtd_t`, so all implementations must agree. Cached ioctl support is per-library descriptor and not synchronized.

Test signals: sysfs-supported and legacy paths both need coverage, including transition from unknown to supported/not-supported 64-bit ioctl states.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/libmtd_int.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/libmtd_legacy.c -->
# sources/test-tools/fio/oslib/libmtd_legacy.c

Purpose: pre-sysfs MTD support for older Linux kernels using `/proc/mtd` and MTD ioctls.

Important APIs/functions: `legacy_libmtd_open()`, `legacy_dev_present()`, `legacy_mtd_get_info()`, `legacy_get_dev_info()`, and `legacy_get_dev_info1()`. Internal `proc_parse_start()` reads `/proc/mtd`; `proc_parse_next()` parses device number, size, erase size, and quoted name.

Control flow: the parser reads the whole `/proc/mtd` buffer, validates the header, and advances line by line. Device info validates a node is a character device with major `90`, opens it, reads `MEMGETINFO`, probes `MEMGETBADBLOCK`, validates geometry, maps MTD type constants to strings, derives `mtd_num` from the minor, and then re-parses `/proc/mtd` for the device name.

State and persistence: no persistent library state beyond caller structs; it opens and closes device/proc files. It probes but does not modify device state except through ioctls that should be informational.

Dependencies and integration: Linux MTD UAPI, `/proc/mtd`, `/dev/mtd%d`, and common MTD helpers. Called by `libmtd.c` when sysfs support is unavailable.

Risks: legacy kernel assumptions are old and hard to test. `legacy_dev_present()` returns early without freeing the parser buffer when it finds a match, leaking memory. Error paths depend on exact `/proc/mtd` formatting. Device node requirements may fail on systems without static `/dev/mtd*` nodes.

Test signals: mocked `/proc/mtd` parser cases and integration on an old or simulated MTD setup.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/libmtd_legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/libmtd_xalloc.h -->
# sources/test-tools/fio/oslib/libmtd_xalloc.h

Purpose: allocation wrappers imported with MTD utility code.

Important APIs/functions: static inline `xmalloc()`, `xcalloc()`, `xzalloc()`, `xrealloc()`, `xstrdup()`, and `_GNU_SOURCE`-guarded `xasprintf()`. Functions abort through `sys_errmsg_die()` on nonzero-size allocation failure.

Control flow and state: no persistent state; wrappers delegate to libc allocation routines and centralize failure handling.

Dependencies and integration: assumes `sys_errmsg_die()` is available from `libmtd_common.h`, so this header is normally included after common helpers.

Risks: allocation failure exits the process rather than returning an error, which may be unexpected inside fio. Functions are marked unused to silence warnings in translation units that include but do not use them.

Test signals: compile with and without `_GNU_SOURCE`; fault-injection allocation tests would need to accept process exit semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/libmtd_xalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/linux-blkzoned.c -->
# sources/test-tools/fio/oslib/linux-blkzoned.c

Purpose: Linux implementation of fio's zoned block device abstraction.

Important APIs/functions: implements `blkzoned_get_zoned_model()`, `blkzoned_get_max_open_zones()`, `blkzoned_get_max_active_zones()`, `blkzoned_report_zones()`, `blkzoned_reset_wp()`, `blkzoned_finish_zone()`, and `blkzoned_move_zone_wp()`. Internal helpers read sysfs attributes and compute zone capacity.

Control flow: sysfs helpers resolve `/sys/dev/block/<major>:<minor>`, follow symlinks, strip partition components when needed, and read queue attributes. Zone reporting opens the block device, allocates a `blk_zone_report`, issues `BLKREPORTZONE`, and converts Linux sector units and zone types/conditions into fio `zbd_zone` fields. Reset/finish build `blk_zone_range` and issue `BLKRESETZONE` or `BLKFINISHZONE`, opening the file temporarily if fio has not already opened it. Write-pointer movement uses `fallocate(FALLOC_FL_ZERO_RANGE)` when no buffer is provided, otherwise `pwrite()`.

State and persistence: no module-global state. Operations can persistently change device write pointers or zone conditions. The code uses caller-owned `fio_file` state and closes only fds it opened itself.

Dependencies and integration: Linux block zoned UAPI, sysfs, fio `zbd_types`, `fio_file`, logging, `smalloc`/verification contexts, and `asprintf()`. It provides the `CONFIG_HAS_BLKZONED` backend declared in `blkzoned.h`.

Risks: requires block devices; non-block files return errors or no zoned model. Older UAPI headers are handled with local struct definitions, but kernel behavior still varies. `readlink()` path handling assumes sysfs canonical layout. `BLKFINISHZONE` treats `ENOTTY` as success for older kernels, which may hide unsupported behavior.

Test signals: ZBD integration tests on host-aware/host-managed devices, partition devices, old kernels lacking capacity or finish-zone support, and sysfs attribute absence.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/linux-blkzoned.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/linux-dev-lookup.c -->
# sources/test-tools/fio/oslib/linux-dev-lookup.c

Purpose: recursively resolves a block device path from major/minor numbers for blktrace replay.

Important APIs/functions: `blktrace_lookup_device(const char *redirect, char *path, unsigned int maj, unsigned int min)`.

Control flow: if `redirect` is provided, it copies it to `path` and succeeds. Otherwise it opens the directory named by `path`, iterates entries, recursively descends into directories, and compares `major(st.st_rdev)`/`minor(st.st_rdev)` for block devices. On match, it copies the found full path back to `path`.

State and persistence: no persistent state; mutates the caller's `path` buffer during recursive search.

Dependencies and integration: Linux `stat`, `sysmacros`, directory APIs, and blktrace replay code that records device major/minor.

Risks: `full_path[257]` and `strcpy()`/`sprintf()` make path length assumptions and can overflow/truncate in deep trees. Recursion follows directories without cycle protection beyond normal filesystem constraints. `redirect` copy also assumes caller buffer is large enough.

Test signals: lookup existing and missing block devices under `/dev`, redirect override, deep directory paths, and path-buffer sizing.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/linux-dev-lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/linux-dev-lookup.h -->
# sources/test-tools/fio/oslib/linux-dev-lookup.h

Purpose: declaration for Linux block-device lookup used by blktrace replay.

Important APIs/types: declares `blktrace_lookup_device()`.

Control flow and state: no implementation or state.

Dependencies and integration: paired with `linux-dev-lookup.c`; consumers pass a mutable search path buffer and target major/minor.

Risks: the API contract does not expose the required size of `path`, which is important because the implementation copies paths into it.

Test signals: compile consumers and run replay lookup scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/linux-dev-lookup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/statx.c -->
# sources/test-tools/fio/oslib/statx.c

Purpose: fallback `statx()` wrapper for systems where libc lacks `statx()`.

Important APIs/functions: under `!CONFIG_HAVE_STATX`, defines `statx()`. If `CONFIG_HAVE_STATX_SYSCALL` is available, it calls `syscall(__NR_statx, ...)`; otherwise it sets `errno = EINVAL` and returns `-1`.

Control flow and state: compile-time selected; no persistent state.

Dependencies and integration: paired with `statx.h`; allows fio code to use a uniform `statx()` symbol where direct syscall support exists.

Risks: on systems without syscall support the fallback fails with `EINVAL`, so callers must handle absence. It does not emulate `statx()` with `stat()`.

Test signals: build on libc-with-statx, syscall-only, and no-statx systems; verify callers degrade gracefully.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/statx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/statx.h -->
# sources/test-tools/fio/oslib/statx.h

Purpose: conditional declarations and stub types for `statx()`.

Important APIs/types: when libc lacks `statx()` but syscall headers exist, includes `<linux/stat.h>` and `<sys/stat.h>`. Without syscall support, defines `STATX_ALL` as `0`, undefines `statx`, and declares an empty `struct statx`. Declares fallback `statx()`.

Control flow and state: no runtime logic.

Dependencies and integration: used with `statx.c` to keep source portable across Linux/libc versions.

Risks: empty `struct statx` is only safe when callers do not inspect fields after a guaranteed failure. Configuration must prevent field use on unsupported platforms.

Test signals: compile matrix and behavior tests for code paths that use file birthtime or extended stat metadata.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/statx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/strcasestr.c -->
# sources/test-tools/fio/oslib/strcasestr.c

Purpose: fallback case-insensitive substring search.

Important APIs/functions: defines `strcasestr(const char *s1, const char *s2)` when `CONFIG_STRCASESTR` is absent.

Control flow and state: walks the haystack and needle, comparing exact or `tolower()` values; resets to the next haystack position on mismatch and returns the first match or `NULL`.

Dependencies and integration: paired with `strcasestr.h`; supports option and string parsing on platforms missing GNU `strcasestr()`.

Risks: passes plain `char` values to `tolower()` without casting to `unsigned char`, which is undefined for negative signed-char non-ASCII bytes. Locale behavior follows C library `tolower()`.

Test signals: empty needle, no match, case variants, overlapping patterns, and high-bit byte inputs.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/strcasestr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/strcasestr.h -->
# sources/test-tools/fio/oslib/strcasestr.h

Purpose: declaration for fallback `strcasestr()`.

Important APIs/types: declares `char *strcasestr(const char *haystack, const char *needle)` when `CONFIG_STRCASESTR` is absent.

Control flow and state: no implementation or state.

Dependencies and integration: paired with `strcasestr.c`; avoids declaring the function when libc already provides it.

Risks: configuration must match platform headers to avoid duplicate declarations.

Test signals: compile on platforms with and without native `strcasestr()`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/strcasestr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/strlcat.c -->
# sources/test-tools/fio/oslib/strlcat.c

Purpose: fallback implementation of BSD `strlcat()`.

Important APIs/functions: `strlcat(char *dst, const char *src, size_t dsize)` appends at most `dsize - strlen(dst) - 1` bytes, NUL terminates when possible, and returns the length it tried to create.

Control flow and state: scans to the end of `dst` within `dsize`, copies from `src` while space remains, then returns `dlen + strlen(src)`.

Dependencies and integration: included only when `CONFIG_STRLCAT` is absent; paired with `strlcat.h`.

Risks: caller must pass a valid NUL-terminated `dst` within `dsize` or accept truncation semantics. This is standard `strlcat()` behavior, but misuse can still read beyond intended memory if `dst` is not terminated within `dsize`.

Test signals: exact fit, truncation, zero-size buffer, unterminated destination within size, and return-value truncation detection.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/strlcat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/strlcat.h -->
# sources/test-tools/fio/oslib/strlcat.h

Purpose: declaration for fallback `strlcat()`.

Important APIs/types: includes `<stddef.h>` and declares `size_t strlcat(char *, const char *, size_t)` when `CONFIG_STRLCAT` is absent.

Control flow and state: no runtime logic.

Dependencies and integration: paired with `strlcat.c`.

Risks: configuration mismatch can conflict with system declarations.

Test signals: compile on platforms with and without native `strlcat()`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/strlcat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/strndup.c -->
# sources/test-tools/fio/oslib/strndup.c

Purpose: fallback `strndup()` implementation.

Important APIs/functions: allocates `n + 1` bytes, copies up to `n` bytes with `strncpy()`, and forces a trailing NUL.

Control flow and state: no persistent state; returns allocated string or `NULL`.

Dependencies and integration: paired with `strndup.h`; used where bounded string duplication is needed on platforms lacking libc support.

Risks: always allocates `n + 1`, even when source is shorter; very large `n` can overflow `n + 1`. Callers own the returned allocation.

Test signals: shorter source, exactly `n`, longer source, `n = 0`, allocation failure.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/strndup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/strndup.h -->
# sources/test-tools/fio/oslib/strndup.h

Purpose: declaration for fallback `strndup()`.

Important APIs/types: includes `<stddef.h>` and declares `char *strndup(const char *, size_t)` when `CONFIG_HAVE_STRNDUP` is absent.

Control flow and state: no logic or state.

Dependencies and integration: paired with `strndup.c`.

Risks: duplicate declaration risk if configure incorrectly detects libc support.

Test signals: compile matrix with native and fallback `strndup()`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/strndup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/strsep.c -->
# sources/test-tools/fio/oslib/strsep.c

Purpose: fallback implementation of BSD/GNU `strsep()`.

Important APIs/functions: `strsep(char **stringp, const char *delim)` returns the next token, overwrites the delimiter with NUL, and advances `*stringp`.

Control flow and state: scans characters in the current string and compares each against all delimiter characters. When a delimiter or NUL is found, it updates `*stringp` to the next position or `NULL`.

Dependencies and integration: paired with `strsep.h`; used by fio parsing code, including zoned-device sysfs line trimming and profile option splitting.

Risks: modifies the input string. Empty tokens are returned, matching standard `strsep()` but differing from `strtok()` expectations.

Test signals: consecutive delimiters, empty input, no delimiter, delimiter at end, and `NULL` string pointer contents.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/strsep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/oslib/strsep.h -->
# sources/test-tools/fio/oslib/strsep.h

Purpose: declaration for fallback `strsep()`.

Important APIs/types: declares `char *strsep(char **, const char *)` when `CONFIG_STRSEP` is absent.

Control flow and state: no runtime logic.

Dependencies and integration: paired with `strsep.c`.

Risks: configuration mismatch can collide with libc declarations.

Test signals: compile on platforms with and without native `strsep()`.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/oslib/strsep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/parse.c -->
# sources/test-tools/fio/parse.c

Purpose: core parser for fio job-file and command-line options.

Important APIs/functions: exported functions include `str_to_float()`, `str_to_decimal()`, `check_str_bytes()`, `check_str_time()`, `strip_blank_front()`, `strip_blank_end()`, `find_option()`/`find_option_c()`, `sort_options()`, `parse_cmd_option()`, `parse_option()`, `string_distance()`, `string_distance_ok()`, `show_cmd_help()`, `fill_default_options()`, `options_init()`, `options_mem_dupe()`, and `options_free()`. Internal helpers handle unit suffixes, value-pair sorting, range display, option help, default validation, and value storage.

Control flow: parsing starts by locating an option through exact/alias matching, splitting `name=value`, and passing the option/value into `handle_option()`. `handle_option()` handles repeated values separated by comma, colon, or dash depending on option type, then calls `__handle_option()` for each segment. The switch in `__handle_option()` validates and stores values by type: strings and enumerations use `posval`, numeric values use byte/time suffix parsing and min/max/power-of-two checks, ranges fill paired offsets, float lists track precision, booleans handle negation, and deprecated/unsupported options report diagnostics. Defaults and profile-specific options reuse the same parser.

State and persistence: global static `__fio_options` is temporarily used during `sort_options()` for priority comparison. Parsed string options allocate and own duplicated strings unless `no_free` is set. Dump-list entries allocate `print_option` nodes for later reporting.

Dependencies and integration: depends on fio option metadata (`struct fio_option`), option categories/groups, logging/debug, arithmetic parser when `CONFIG_ARITHMETIC` is enabled, and helpers from `minmax`, `pow2`, and IEEE float wrappers. It is central to job setup and profile expansion.

Risks: parser behavior is highly metadata-driven; bad offsets, callbacks, or option types can corrupt target option structs. Unit suffix logic is subtle, including percent encoding as negative unsigned values and zone suffix values. `strip_blank_end()` treats `;` and `#` as comments unconditionally. Some conversions rely on `strtoll()`/`sscanf()` edge behavior.

Test signals: option parser tests should cover every `fio_opt_type`, byte/time units including IEC/SI behavior, arithmetic expressions, percentages, zone suffixes, ranges, multi-value replication, validation callbacks, defaults, deprecation, closest-help suggestions, and memory cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/parse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/parse.h -->
# sources/test-tools/fio/parse.h

Purpose: public option parser model and API declarations.

Important APIs/types: defines `enum fio_opt_type`, `struct value_pair`, `PARSE_MAX_VP`, `struct fio_option`, parser/exported helper declarations, callback typedefs, `td_var()`, percentage/zone encoding helpers, `ZONE_BASE_VAL`, and `struct print_option`.

Control flow and state: no parser implementation, but `td_var()` is the key storage helper: it chooses profile option storage when `o->prof_opts` is set, otherwise the thread option object, then applies the option offset.

Dependencies and integration: includes `<inttypes.h>` and `flist.h`; used by global options, profiles, and command-line/job-file parsing.

Risks: `struct fio_option` offsets are raw byte offsets into caller structs, so metadata mistakes are memory-safety bugs. Percent/zone encodings use unsigned wraparound, requiring callers to use helper predicates rather than direct comparisons.

Test signals: compile all option table definitions with `options_init()` diagnostics enabled and parser tests that validate offsets and encoded special values.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/parse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/pcbuf.h -->
# sources/test-tools/fio/pcbuf.h

Purpose: header-only two-phase circular buffer for producer/consumer separation with explicit commit.

Important APIs/types: `struct pc_buf` tracks `commit_head`, `staging_head`, `read_tail`, `capacity`, and a flexible `uint64_t buffer[]`. Inline APIs include `pcb_alloc()`, `pcb_is_empty()`, `pcb_is_full()`, `pcb_push_staged()`, `pcb_commit()`, `pcb_pop()`, `pcb_print_committed()`, `pcb_print_staged()`, `pcb_committed_size()`, `pcb_staged_size()`, and `pcb_space_available()`.

Control flow: producers stage items by writing at `staging_head`; consumers only see data up to `commit_head`. `pcb_commit()` publishes all staged entries by moving `commit_head` to `staging_head`. One slot is reserved so full and empty states are distinguishable.

State and persistence: all state is in the allocated buffer object; no synchronization primitives are included. `pcb_alloc()` uses `malloc()` and leaves freeing to the caller.

Dependencies and integration: generic utility header using standard C headers; useful where fio needs staged visibility of batches without a separate implementation file.

Risks: not thread-safe without external synchronization or memory barriers. `capacity` must be greater than one; zero capacity causes modulo-by-zero and one capacity leaves no usable slots. Allocation size can overflow for huge capacities.

Test signals: staged vs committed visibility, wraparound, full/empty detection, capacity edge cases, and concurrent usage only with explicit locking tests.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/pcbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/printing.c -->
# sources/test-tools/fio/printing.c

Purpose: GTK/gfio print-operation support for results.

Important APIs/functions: `gfio_print_results()` is the exported entry point. Static callbacks `begin_print()`, `results_draw_page()`, `results_print_done()`, and `printing_error_dialog()` integrate with `GtkPrintOperation`.

Control flow: `gfio_print_results()` creates a print operation, restores previous settings/page setup if available, connects GTK signals, enables async printing, and runs the print dialog. `begin_print()` captures page dimensions and DPI and sets one page. `results_draw_page()` currently draws simple diagonal/crosshair test graphics and coordinate labels with Cairo. Error paths show a GTK message dialog and preserve settings on apply.

State and persistence: static `print_params` caches page setup, print settings, and page dimensions across calls. GTK reference counts are managed for settings, but page setup is stored as a pointer from the context.

Dependencies and integration: GTK, Cairo, gfio UI structures, and `draw_right_justified_text()`.

Risks: drawing looks like placeholder/test output rather than full fio results. Error-handling comment documents a hang when printing over an unwritable existing file. Cached `page_setup` lifetime should be reviewed because it is not explicitly referenced like settings.

Test signals: gfio print dialog, print-to-file success/failure, repeated print settings persistence, and visual output inspection.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/printing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/printing.h -->
# sources/test-tools/fio/printing.h

Purpose: declaration for gfio result printing.

Important APIs/types: declares `gfio_print_results(struct gui_entry *ge)`.

Control flow and state: no implementation; caller passes a gfio GUI entry used by `printing.c`.

Dependencies and integration: depends on a visible `struct gui_entry` declaration from gfio headers before use.

Risks: minimal API surface but tightly coupled to GTK/gfio types.

Test signals: gfio build and print action integration.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/printing.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/profile.c -->
# sources/test-tools/fio/profile.c

Purpose: profile registration, lookup, option injection, and per-thread profile hooks for fio benchmark profiles.

Important APIs/functions: `find_profile()`, `load_profile()`, `register_profile()`, `unregister_profile()`, `profile_add_hooks()`, `profile_td_init()`, and `profile_td_exit()`.

Control flow: profiles are stored in a global intrusive list. `register_profile()` annotates profile-specific options with `prof_name` and `prof_opts`, registers them with the global option system, links the profile, and adds the profile name as a valid value for the `profile` option. `load_profile()` finds a profile, calls `prep_cmd()`, then adds the generated command-line options. `profile_add_hooks()` copies optional `prof_io_ops` into a `thread_data` when a profile is active.

State and persistence: static `profile_list` holds registered profiles. Profile option metadata is mutated during registration and invalidated during unregister. `thread_data` receives copied hook operations and a flag.

Dependencies and integration: `fio.h`, option system (`add_option`, `add_job_opts`, `add_opt_posval`, invalidation helpers), debug/logging, and `flist`.

Risks: registration mutates shared static option tables; unregister must cleanly remove option values. `load_profile()` assumes `prep_cmd()` produced a NULL-terminated command line. Hook copying means later changes to the profile ops are not reflected in already initialized threads.

Test signals: registering/unregistering profiles, profile-specific option parsing, missing profile errors, prep failures, and td init/exit hook execution.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/profile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/profile.h -->
# sources/test-tools/fio/profile.h

Purpose: public profile plugin interface for fio.

Important APIs/types: `struct prof_io_ops` exposes optional `td_init`, `td_exit`, and `io_u_lat` hooks. `struct profile_ops` describes a profile with list linkage, name, description, options, option storage, `prep_cmd()`, generated command line, and optional IO hooks. Declares registration, lookup, loading, hook installation, and td lifecycle helpers.

Control flow and state: no implementation, but defines the contract consumed by `profile.c` and profile modules under `profiles/`.

Dependencies and integration: includes `flist.h` and uses `struct fio_option` and `struct thread_data` from broader fio headers.

Risks: fixed-size `name[32]` and `desc[64]` require profile authors to keep identifiers short. `cmdline` must be stable and NULL-terminated.

Test signals: compile profile modules and run profile load paths with custom options and hooks.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/profile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/profiles/act.c -->
# sources/test-tools/fio/profiles/act.c

Purpose: implements the ACT "Aerospike-like" fio profile with generated workloads and latency pass/fail criteria.

Important APIs/functions: static profile registration via `fio_init act_register()` and `fio_exit act_unregister()`. Profile callbacks include `act_prep_cmdline()`, `act_td_init()`, `act_td_exit()`, and `act_io_u_lat()`. Helpers build option strings (`act_add_opt()`, `act_add_rw()`, `act_add_dev_prep()`, `act_add_dev()`), aggregate latency slices, and print final stats.

Control flow: profile options collect device names, load, duration, queue/thread parameters, read block count, write size, and prep mode. `act_prep_cmdline()` splits comma-separated devices and generates fio jobs. Normal mode creates runtime/time-based read and write jobs per device with derived rates; prep mode writes zeroes and random salt. During IO, `act_io_u_lat()` buckets latency by criteria per one-hour sample and returns failure when thresholds are exceeded. Thread init allocates per-thread slices and increments a shared pending count; thread exit merges slices under a fio semaphore and prints aggregate pass/fail when the last thread exits.

State and persistence: global `act_opts` grows with dynamically allocated option strings; global `act_run_data` holds the semaphore, pending thread count, and aggregate slices. Per-thread state lives in `td->prof_data`.

Dependencies and integration: profile framework, parser option types, fio semaphores, timing (`fio_gettime`, `time_since_now`), logging, and thread lifecycle hooks.

Risks: `act_options.device_names` is destructively modified by `strsep()`, so reload/reuse semantics are fragile. Option cleanup loop in `act_unregister()` increments before freeing and may skip or overrun depending on `org_idx`/`opt_idx`. Default `test_duration` is parsed as a time value but later formatted as seconds with `%llus`; unit expectations need confirmation. This profile drives real destructive writes to named devices.

Test signals: profile option parsing, generated command-line contents for prep and normal mode, multiple devices, latency bucket aggregation, failure thresholds, and unregister memory cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/profiles/act.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/profiles/tiobench.c -->
# sources/test-tools/fio/profiles/tiobench.c

Purpose: implements a fio profile approximating tiotest/tiobench workloads.

Important APIs/functions: `tb_prep_cmdline()` fills dynamic option strings; static init/exit functions register/unregister `tiobench_profile`. Profile options include size, block size, number of runs, directory, and thread count.

Control flow: base `tb_opts` describes four jobs: sequential write, random write, sequential read, and random read, with stonewalls between phases, sync engine, direct IO, group reporting, threads, overwrite, and fixed filenames. `tb_prep_cmdline()` converts size from MiB to bytes or defaults to `4*1024*$mb_memory`, writes block size, loops, directory, and numjobs into static buffers, and returns the option list to the profile loader.

State and persistence: static option storage and static string buffers persist across runs. `dir` is marked `no_free`, so parser cleanup does not free it.

Dependencies and integration: profile framework, parser, option categories/groups, and fio job option ingestion.

Risks: static buffers assume formatted option values fit 80 bytes; directory paths longer than the buffer can overflow via `sprintf()`. Fixed filenames limit scaling beyond four files unless fio interprets them per job/thread as intended.

Test signals: generated command line for explicit/default size, long directories, different thread counts, and full profile execution in a scratch directory.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/profiles/tiobench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/pshared.c -->
# sources/test-tools/fio/pshared.c

Purpose: initializes pthread mutexes and condition variables with optional process-shared and monotonic-clock attributes.

Important APIs/functions: `cond_init_pshared()`, `mutex_init_pshared_with_type()`, `mutex_init_pshared()`, and `mutex_cond_init_pshared()`.

Control flow: each initializer creates the relevant pthread attribute object, conditionally sets `PTHREAD_PROCESS_SHARED` under `CONFIG_PSHARED`, conditionally sets condition-variable clock to `CLOCK_MONOTONIC`, initializes the synchronization object, logs errors, and returns pthread error codes. Mutex attributes are destroyed after successful mutex initialization.

State and persistence: no global state; initializes caller-owned pthread objects.

Dependencies and integration: pthreads, fio logging, and platform configure macros. Used where synchronization objects may live in shared memory or need monotonic timeouts.

Risks: error paths in `cond_init_pshared()` do not destroy initialized condition attributes before returning. If mutex initialization succeeds but condition initialization fails in `mutex_cond_init_pshared()`, the mutex remains initialized and caller must clean up.

Test signals: platforms with and without `CONFIG_PSHARED`, monotonic condattr support, each mutex type, and failure injection for attr/init calls.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/pshared.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/pshared.h -->
# sources/test-tools/fio/pshared.h

Purpose: declarations for process-shared pthread initialization helpers.

Important APIs/types: includes `<pthread.h>` and declares mutex, condition, and combined initialization helpers.

Control flow and state: no implementation or state.

Dependencies and integration: paired with `pshared.c`; consumers pass caller-owned pthread objects.

Risks: API returns raw pthread error codes, not `errno`, so callers must handle that convention.

Test signals: compile and runtime initialization tests under relevant configure matrices.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/pshared.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/rate-submit.c -->
# sources/test-tools/fio/rate-submit.c

Purpose: offloaded IO submission workqueue helpers for fio's rated submission mode.

Important APIs/functions: exported `rate_submit_init()` and `rate_submit_exit()` manage the workqueue when `io_submit_mode == IO_MODE_OFFLOAD`. Workqueue callbacks include `io_workqueue_fn()`, pre-sleep flush/quiesce callbacks, worker allocation/free/init/exit, and accounting update functions. `check_overlap()` serializes overlapping IO when `serialize_overlap` is enabled.

Control flow: initialization creates a workqueue with one worker per requested iodepth. Each worker owns a copied `thread_data` configured from the parent, duplicates files/options, loads and initializes the IO engine, and then submits `io_u` work items. `io_workqueue_fn()` optionally waits until no in-flight overlap exists, marks the IO, queues it, handles busy/completion paths, updates queue events, and signals the parent if errors occur. Exit aggregates worker stats into the parent and frees worker resources. Accounting periodically sums per-direction byte/block counters under locks unless atomic fetch-add is available.

State and persistence: worker-private `thread_data` copies hold IO engine/file state. Parent `td->io_wq` owns worker lifecycle and stat locks. Global `overlap_check` mutex is used by overlap serialization.

Dependencies and integration: fio core thread data, IO engines, workqueue framework, file duplication, option duplication/free, runstate management, rusage, and stats aggregation.

Risks: this path is concurrency-heavy. Deadlock avoidance depends on consistent lock ordering in `pthread_double_lock()`. Worker copies must stay synchronized with parent fields that are safe to duplicate. Overlap checking unlock/relock loops can be expensive under heavy overlapping workloads. Per-priority stats are disabled during exit because aggregation cannot fully preserve them.

Test signals: offload mode with multiple iodepths, serialize-overlap workloads, busy IO engines, error propagation, stat aggregation, workqueue shutdown, and ThreadSanitizer-style race testing where possible.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/rate-submit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/rate-submit.h -->
# sources/test-tools/fio/rate-submit.h

Purpose: declarations for rated/offloaded IO submission lifecycle.

Important APIs/types: declares `rate_submit_init(struct thread_data *, struct sk_out *)` and `rate_submit_exit(struct thread_data *)`.

Control flow and state: no implementation; functions operate on fio thread data and socket output context.

Dependencies and integration: paired with `rate-submit.c`; requires broader fio declarations for `struct thread_data` and `struct sk_out`.

Risks: callers must only expect workqueue setup when offload mode is active; init returns zero for other modes.

Test signals: compile and offload/non-offload initialization behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/rate-submit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/rwlock.c -->
# sources/test-tools/fio/rwlock.c

Purpose: fio wrapper around a process-shared pthread read/write lock allocated in shared memory.

Important APIs/functions: `fio_rwlock_init()`, `fio_rwlock_read()`, `fio_rwlock_write()`, `fio_rwlock_unlock()`, and `fio_rwlock_remove()`.

Control flow: initialization mmaps anonymous shared memory, stores a magic value, initializes rwlock attributes, optionally sets `PTHREAD_PROCESS_SHARED`, initializes the pthread rwlock, destroys attributes, and returns the mapped object. Lock/unlock functions assert the magic value before calling pthread rwlock operations. Remove destroys the rwlock and unmaps the object.

State and persistence: lock state lives in an mmaped `struct fio_rwlock`; the magic constant guards accidental misuse.

Dependencies and integration: pthreads, `sys/mman.h`, fio OS mapping macro `OS_MAP_ANON`, and logging. Used where fio needs shared read/write synchronization across processes or threads.

Risks: `fio_rwlock_init()` error path calls `fio_rwlock_remove()` even if `pthread_rwlock_init()` was not reached, which can destroy an uninitialized rwlock. The assert checks disappear under `NDEBUG`. Process-shared behavior depends on platform support.

Test signals: read/write lock behavior, process-shared operation under `CONFIG_PSHARED`, mmap failure handling, attr/init failure injection, and removal after initialization.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/rwlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/fio/rwlock.h -->
# sources/test-tools/fio/rwlock.h

Purpose: public type and API for fio read/write locks.

Important APIs/types: defines `FIO_RWLOCK_MAGIC`, `struct fio_rwlock` containing `pthread_rwlock_t lock` and `int magic`, and declares init/read/write/unlock/remove helpers.

Control flow and state: no implementation, but documents that callers manipulate an opaque-ish object allocated by `fio_rwlock_init()`.

Dependencies and integration: includes pthread headers and pairs with `rwlock.c`.

Risks: structure layout is public, so external code could allocate it incorrectly; the implementation expects mmap allocation and magic initialization.

Test signals: compile users and lifecycle tests around the declared API.
<!-- END_FILE_RESEARCH: sources/test-tools/fio/rwlock.h -->
