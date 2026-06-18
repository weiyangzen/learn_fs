# Research: subset-b-006583 tools LEDs, libapi, and libbpf support

This grouped report covers the requested source files under `sources/distributed-fs/ceph-client/tools`. Each file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/leds/led_hw_brightness_mon.c -->
# sources/distributed-fs/ceph-client/tools/leds/led_hw_brightness_mon.c

## Purpose
`led_hw_brightness_mon.c` is a small userspace diagnostic tool for LED class devices. It monitors the sysfs `brightness_hw_changed` attribute for one LED device and prints a monotonic timestamp plus the new brightness value whenever hardware or firmware changes the LED brightness outside normal kernel control.

## Important APIs, types, and functions
The only entry point is `main()`. It uses `LED_MAX_NAME_SIZE` from `<linux/uleds.h>` for path sizing, constructs `/sys/class/leds/<device>/brightness_hw_changed`, opens it read-only, primes the fd with an initial `read()`, waits with `poll(POLLPRI)`, timestamps with `clock_gettime(CLOCK_MONOTONIC)`, reads the ASCII brightness value into `buf`, rewinds with `lseek()`, and prints `atoi(buf)`.

## Control flow
The tool validates that exactly one device-name argument was provided, opens the sysfs notification file, then enters an infinite blocking poll loop. Each priority event is treated as a brightness-change notification. On poll, read, or seek failure, it breaks out, closes the fd, and returns the last error-ish integer.

## State and persistence behavior
There is no persistent state. Runtime state is the sysfs fd, the current poll descriptor, a short input buffer, and the last timestamp. The initial read is intentionally allowed to fail because it only suppresses stale/spurious notifications when a previous hardware event is already latched.

## Dependencies and integration points
This depends on the LED class sysfs ABI and on kernels/devices that expose `brightness_hw_changed`. It integrates with the `tools/leds` build as a standalone utility, not as a library.

## Risks and edge cases
`snprintf()` is called with `LED_MAX_NAME_SIZE` even though the destination has extra room for the fixed path prefix, so very long names can be truncated before the suffix is complete. The buffer read is not explicitly NUL-terminated before `atoi()`. Error reporting prints the negative return value from `poll()`/`lseek()` rather than `errno`, limiting diagnostics. The tool assumes sysfs poll semantics are edge-compatible with `POLLPRI`.

## Test signals
Run against an LED device with `brightness_hw_changed`, trigger firmware brightness changes, and verify one timestamp/value line per change. Negative tests should cover missing argument, missing sysfs attribute, long LED names, and CTRL+C cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/leds/led_hw_brightness_mon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/leds/uledmon.c -->
# sources/distributed-fs/ceph-client/tools/leds/uledmon.c

## Purpose
`uledmon.c` creates a userspace LED class device through `/dev/uleds` and monitors brightness changes requested by the LED subsystem. It is a simple exerciser for the uleds interface: userspace registers the LED, then blocks reading brightness updates.

## Important APIs, types, and functions
The `main()` function fills `struct uleds_user_dev` with a user-provided `name` and `max_brightness = 100`, opens `/dev/uleds` read-write, writes the registration structure, then repeatedly reads an `int brightness` and prints it with a `CLOCK_MONOTONIC` timestamp. It relies on `LED_MAX_NAME_SIZE` and the uleds character device ABI from `<linux/uleds.h>`.

## Control flow
After argument validation, the program registers the uleds device by writing the full `struct uleds_user_dev`. A successful write transitions into an endless blocking `read()` loop. A read failure prints `perror()`, closes the fd, and exits nonzero.

## State and persistence behavior
No state persists after process exit. The lifetime of the LED class device is tied to the open `/dev/uleds` file descriptor. Runtime state is the registration struct, fd, last brightness value, and timestamp.

## Dependencies and integration points
The tool requires a kernel with the uleds driver and permissions to open `/dev/uleds`. The created LED appears under the kernel LED class, so other LED sysfs tooling can drive brightness changes that this process observes.

## Risks and edge cases
`struct uleds_user_dev uleds_dev` is not zero-initialized before `strncpy()`, so names of length `LED_MAX_NAME_SIZE` may lack a terminator and padding bytes can contain stack data. The write only checks `ret == -1`; a short write would be treated as success. The printed brightness uses `%u` for an `int`. The infinite loop has no graceful cleanup beyond process termination.

## Test signals
Build and run with a unique device name, confirm a new `/sys/class/leds/<name>` appears, write different brightness values through sysfs, and verify matching timestamp/value output. Tests should also cover missing `/dev/uleds`, permissions, and maximum-length names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/leds/uledmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/Makefile -->
# sources/distributed-fs/ceph-client/tools/lib/api/Makefile

## Purpose
This Makefile builds and installs the small `tools/lib/api` static library, `libapi.a`, plus its public headers. The library provides reusable support code for kernel tools: filesystem mount discovery, debug printing hooks, CPU sysfs helpers, buffered I/O, and poll fd arrays.

## Important APIs, types, and functions
Key variables are `srctree`, `OUTPUT`, `LIBFILE`, `API_IN`, `CFLAGS`, `HDRS`, `FD_HDRS`, `FS_HDRS`, and install path variables derived from `prefix`, `DESTDIR`, and `LP64`. It includes `tools/build/Makefile.include` and `tools/scripts/Makefile.include`, builds the recursive `libapi` object through `$(MAKE) $(build)=libapi`, archives it with `$(AR) rcs`, and installs headers under `$(prefix)/include/api`.

## Control flow
The default `all` target depends on `fixdep` and `$(LIBFILE)`. `$(API_IN)` triggers the tools build system for the `libapi` directory. `$(LIBFILE)` removes any stale archive before archiving the combined object. `install` runs both `install_lib` and `install_headers`. `clean` removes the archive and object/dependency files under `OUTPUT` or the current tree.

## State and persistence behavior
Persistent outputs are `$(OUTPUT)libapi.a`, intermediate object files, and installed headers/libraries. No runtime state is involved. `DESTDIR` supports packaging installs into an alternate root.

## Dependencies and integration points
This file is tightly integrated with the Linux tools build framework, including `fixdep`, quiet command macros, architecture variables, and recursive `Build` files. Consumers include perf and other tools that link the local API support archive instead of duplicating helpers.

## Risks and edge cases
The `clean` rule uses `find ... | xargs $(RM)` without `-print0`, so unusual filenames are not robust. `CFLAGS` enables `-Werror` by default unless `WERROR=0`, which can break cross builds on newer compilers. Header installation mirrors only selected public headers; adding new public headers requires updating this Makefile.

## Test signals
Run `make -C tools/lib/api O=<out>` and `make install_headers DESTDIR=<tmp> prefix=/usr`, verify `libapi.a` is produced, installed headers land under `include/api`, and `make clean` removes generated archive/object state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/cpu.c -->
# sources/distributed-fs/ceph-client/tools/lib/api/cpu.c

## Purpose
`cpu.c` provides one libapi helper for discovering a CPU maximum frequency from sysfs. It is intended for tools that need a coarse CPU frequency value without open-coding sysfs mount discovery and parsing.

## Important APIs, types, and functions
`cpu__get_max_freq(unsigned long long *freq)` is the only exported function. It reads `devices/system/cpu/online` with `sysfs__read_int()` to obtain a CPU number, constructs `devices/system/cpu/cpu%d/cpufreq/cpuinfo_max_freq`, and reads the unsigned long long value with `sysfs__read_ull()`.

## Control flow
The function fails early if the online CPU sysfs read fails. Otherwise it formats the cpufreq entry for the parsed CPU and delegates the final read to the fs helper. It returns `0` on success or the negative/error return from the lower-level helper.

## State and persistence behavior
There is no local state. The function reads live sysfs state on each call. Any caching of the sysfs mountpoint happens in `fs.c`, not here.

## Dependencies and integration points
It depends on `cpu.h` for the prototype and `fs/fs.h` for `PATH_MAX`, `sysfs__read_int()`, and `sysfs__read_ull()`. It integrates with tools that link `libapi.a`.

## Risks and edge cases
`devices/system/cpu/online` can contain CPU ranges such as `0-7`, while `sysfs__read_int()` uses `atoi()`-style parsing and will return only the leading integer. This means the helper effectively samples CPU0 on common systems. Systems without cpufreq, with offline CPU0, or with policy-only cpufreq layouts will fail.

## Test signals
Unit or runtime tests should mock `SYSFS_PATH` and provide cpu online/cpufreq files. Real-system checks should compare the returned value with `/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq` and verify failure behavior when cpufreq is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/cpu.h -->
# sources/distributed-fs/ceph-client/tools/lib/api/cpu.h

## Purpose
`cpu.h` is the public libapi declaration for CPU helper functions. In this subset it exposes only maximum-frequency discovery.

## Important APIs, types, and functions
The header declares `int cpu__get_max_freq(unsigned long long *freq);`. It uses a simple include guard `__API_CPU__` and introduces no types or inline helpers.

## Control flow
There is no executable control flow. Callers include the header, pass a writable `unsigned long long *`, and interpret a zero return as a valid frequency read.

## State and persistence behavior
The header owns no state. The implementation reads sysfs at call time.

## Dependencies and integration points
It is installed by `tools/lib/api/Makefile` as a public `api/cpu.h` header and consumed by tools linked against `libapi.a`.

## Risks and edge cases
The interface does not document units in the prototype; the implementation returns the sysfs `cpuinfo_max_freq` value, normally kHz. Callers must check the return value before using `*freq`.

## Test signals
Compile tests should include this header from C and C++-adjacent tool builds. Runtime behavior is covered through `cpu.c` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/debug-internal.h -->
# sources/distributed-fs/ceph-client/tools/lib/api/debug-internal.h

## Purpose
`debug-internal.h` is the private libapi logging facade. It lets internal libapi code emit warn/info/debug messages through callback pointers configured by the public debug API.

## Important APIs, types, and functions
It includes `debug.h`, declares the global callback variables `__pr_warn`, `__pr_info`, and `__pr_debug`, and defines `pr_warn()`, `pr_info()`, and `pr_debug()` through the `__pr(func, fmt, ...)` macro. The macro prefixes messages with `libapi: ` and suppresses output when the callback pointer is `NULL`.

## Control flow
Each logging macro checks the selected function pointer before calling it. The callback is expected to behave like `printf`, accepting a format string and variadic arguments.

## State and persistence behavior
The header exposes mutable process-global function pointers defined in `debug.c`. Those settings persist for the lifetime of the process or until `libapi_set_print()` replaces them.

## Dependencies and integration points
This file is internal to `tools/lib/api`. Public consumers should use `debug.h` and `libapi_set_print()`, while libapi implementation files can include this header for prefixed logging.

## Risks and edge cases
The callback pointers are global and unsynchronized, so concurrent changes from multiple threads can race with logging. Format-string type safety depends entirely on compiler checks at call sites and callback compatibility.

## Test signals
Build with warnings enabled to catch format issues. Runtime tests can set callbacks to capture strings and verify prefixes, NULL suppression, and warn/info/debug routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/debug-internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/debug.c -->
# sources/distributed-fs/ceph-client/tools/lib/api/debug.c

## Purpose
`debug.c` implements libapi's configurable print callbacks. It provides default warning and info output to stderr and lets embedding tools redirect or silence messages.

## Important APIs, types, and functions
`__base_pr()` is a static variadic wrapper around `vfprintf(stderr, ...)`. The global callback variables `__pr_warn`, `__pr_info`, and `__pr_debug` back the internal macros from `debug-internal.h`; warn and info default to `__base_pr`, while debug defaults to `NULL`. `libapi_set_print()` assigns new callback pointers for all three channels.

## Control flow
Callers configure logging with `libapi_set_print(warn, info, debug)`. Later internal `pr_*` macros call the selected function if non-NULL. There is no validation or fallback when callbacks are NULL.

## State and persistence behavior
The three callback variables are process-global mutable state. Settings persist until overwritten and affect all libapi users in the same process.

## Dependencies and integration points
It depends on the public `debug.h` typedef and private `debug-internal.h` declarations. It is archived into `libapi.a` and used by filesystem helpers for warnings such as mount discovery issues.

## Risks and edge cases
Callback mutation is not thread-safe. A callback with incompatible variadic behavior can crash callers. Because debug defaults to NULL, debug messages disappear unless explicitly enabled.

## Test signals
Tests should verify default warn/info write to stderr, debug is silent by default, setting NULL suppresses a channel, and custom callbacks receive the `libapi:` prefix from internal macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/debug.h -->
# sources/distributed-fs/ceph-client/tools/lib/api/debug.h

## Purpose
`debug.h` is the public logging configuration API for libapi. It lets embedding tools customize how libapi warnings, informational messages, and debug messages are printed.

## Important APIs, types, and functions
`typedef int (*libapi_print_fn_t)(const char *, ...);` defines callback shape. `libapi_set_print(libapi_print_fn_t warn, libapi_print_fn_t info, libapi_print_fn_t debug)` installs callbacks for each logging channel.

## Control flow
The header has no executable logic. Consumers include it and call `libapi_set_print()` during initialization if default stderr logging is not desired.

## State and persistence behavior
State is owned by `debug.c` as global callback pointers. The header documents no ownership because callbacks are plain function pointers.

## Dependencies and integration points
It is installed as part of libapi headers and is included by `debug-internal.h`. Tools linking libapi can use it without including private headers.

## Risks and edge cases
The callback type is variadic; mismatched implementations are not strongly type-checked beyond the first argument. There is no thread-safety contract for changing callbacks after other threads start using libapi.

## Test signals
Compile a consumer against the installed header and link with `libapi.a`. Runtime tests are covered by `debug.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fd/array.c -->
# sources/distributed-fs/ceph-client/tools/lib/api/fd/array.c

## Purpose
`fd/array.c` implements a growable array of `struct pollfd` entries with synchronized per-entry private metadata. It is a convenience layer for tools that manage many fds and want filtering/destruction around `poll()`.

## Important APIs, types, and functions
Core functions are `fdarray__init()`, `fdarray__grow()`, `fdarray__new()`, `fdarray__exit()`, `fdarray__delete()`, `fdarray__add()`, `fdarray__dup_entry_from()`, `fdarray__filter()`, `fdarray__poll()`, and `fdarray__fprintf()`. The implementation maintains `entries` and `priv` arrays with identical allocation and indexing.

## Control flow
Users initialize or allocate an array, add fd/event pairs, call `fdarray__poll()`, then call `fdarray__filter()` to clear entries whose `revents` match a mask. Filtering optionally calls a destructor for matching entries and returns the count of remaining filterable entries. Cleanup frees both arrays and resets the structure.

## State and persistence behavior
All state is caller-owned in `struct fdarray`: current count, allocation count, autogrow amount, poll entries, and private metadata. It is runtime-only and freed by `fdarray__exit()`/`fdarray__delete()`.

## Dependencies and integration points
It depends on libc allocation, `<poll.h>`, and the public `array.h`. It integrates with perf/tool event loops that need to keep an fd and an index/pointer side by side.

## Risks and edge cases
`fdarray__grow()` reallocates `entries` first and then `priv`; if the second allocation fails, it frees the newly returned `entries` pointer. When `realloc()` moved storage, that can drop the original entries while `fda->entries` still points to freed memory. Autogrow of zero makes `fdarray__add()` fail once full. Filtering clears event fields but does not compact arrays or close fds unless a destructor does so.

## Test signals
Tests should add beyond initial allocation, verify private metadata stays aligned, poll/filter with a pipe or eventfd, exercise destructor calls, duplicate entries from one array to another, and force allocation-failure paths under fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fd/array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fd/array.h -->
# sources/distributed-fs/ceph-client/tools/lib/api/fd/array.h

## Purpose
`fd/array.h` declares the libapi poll fd array abstraction. It exposes the data structure so callers can inspect `struct pollfd` entries directly while relying on helper functions for allocation and filtering.

## Important APIs, types, and functions
`struct fdarray` contains `nr`, `nr_alloc`, `nr_autogrow`, `struct pollfd *entries`, and a parallel `priv` array whose entries can hold either `idx` or `ptr` plus flags. `enum fdarray_flags` defines `fdarray_flag__default`, `fdarray_flag__nonfilterable`, and `fdarray_flag__non_perf_event`. Public helpers cover initialization, allocation, deletion, adding, duplicating, polling, filtering, growing, printing, and `fdarray__available_entries()`.

## Control flow
Callers generally create or initialize an array, add entries, pass the array to `fdarray__poll()`, then inspect `entries[i].revents` or use `fdarray__filter()` to clear matching entries. Direct access to `priv[N].idx` or `priv[N].ptr` is allowed, but replacing the `priv` pointer is explicitly forbidden.

## State and persistence behavior
The structure owns heap allocations for `entries` and `priv` when grown. State persists only for the lifetime of the object and is not thread-safe by itself.

## Dependencies and integration points
The header forward-declares `struct pollfd` and includes `<stdio.h>` for `FILE`. It is installed by the libapi Makefile under `include/api/fd/array.h`.

## Risks and edge cases
Because the structure layout is public, external code can mutate invariants such as `nr`, `nr_alloc`, or `entries`. Users must not store pointers into `entries` or `priv` across growth. The `revents` parameter name in `fdarray__add()` actually fills `events`, which can confuse callers.

## Test signals
Compile users against the installed header, verify direct private metadata use survives `fdarray__grow()`, and run behavioral tests from `array.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fd/array.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/cgroup.c -->
# sources/distributed-fs/ceph-client/tools/lib/api/fs/cgroup.c

## Purpose
`fs/cgroup.c` locates the cgroup filesystem mountpoint that provides a requested controller subsystem. It supports cgroup v1 split hierarchies and cgroup v2 fallback.

## Important APIs, types, and functions
`struct cgroupfs_cache_entry` stores the last `subsys` and `mountpoint`. `cgroupfs_find_mountpoint(char *buf, size_t maxlen, const char *subsys)` is the public function. It scans `/proc/mounts`, parses device, mount path, filesystem type, and options, chooses a v1 cgroup mount containing the subsystem when possible, otherwise remembers a cgroup2 mount as fallback.

## Control flow
The function first checks the one-entry cache for the same subsystem. On miss, it opens `/proc/mounts`, reads lines with `getline()`, tokenizes by spaces, filters filesystem types starting with `cgroup`, and validates the subsystem option boundary with spaces or commas. After scanning, it updates the cache and copies the mountpoint into the caller buffer if it fits.

## State and persistence behavior
The only persistent runtime state is the static heap-allocated one-entry cache. It lasts until process exit and is not invalidated if mounts change.

## Dependencies and integration points
It depends on `/proc/mounts`, libc allocation/string functions, and `fs.h` for `PATH_MAX` and the prototype. Tools use it to find controller files without hard-coding `/sys/fs/cgroup` layouts.

## Risks and edge cases
Parsing `/proc/mounts` by raw spaces ignores escaped whitespace in mount paths. `strcpy(mountpoint, path)` assumes the parsed path fits `PATH_MAX`. The one-entry cache is unsynchronized and can race in multithreaded callers. A cgroup2 mount is returned even though individual v1 subsystem files do not exist there.

## Test signals
Test with mocked `/proc/mounts` content for v1 single hierarchy, v1 split hierarchy, v2-only systems, no matching subsystem, long mountpoints, and repeated calls verifying cache behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/fs.c -->
# sources/distributed-fs/ceph-client/tools/lib/api/fs/fs.c

## Purpose
`fs.c` is libapi's filesystem discovery and simple file-value I/O layer. It finds and optionally mounts common pseudo-filesystems used by tools (`sysfs`, `procfs`, `debugfs`, `tracefs`, `hugetlbfs`, and bpffs), then offers helpers for reading and writing numeric/string values under those mounts.

## Important APIs, types, and functions
`struct fs` records a filesystem name, known mountpoint list, cached path, mount mutex, and magic number. The `FS()` macro generates `name__mountpoint()`, `name__mount()`, and `name__configured()` for each supported filesystem. Helpers include `fs__read_mounts()`, `fs__valid_mount()`, `fs__check_mounts()`, `fs__env_override()`, `fs__mount()`, `filename__read_int()`, `filename__read_ull()`, `filename__read_xll()`, `filename__read_str()`, `filename__write_int()`, `procfs__read_str()`, `sysctl__read_int()`, `sysfs__read_*()`, and `sysfs__write_int()`.

## Control flow
On first `*_mountpoint()` call, `pthread_once()` runs initialization: environment override (`NAME_PATH`), known mountpoint statfs checks, then `/proc/mounts` scan. `*_mount()` returns the cached mountpoint or attempts `mount(NULL, mountpoint, fs->name, 0, NULL)` under a mutex. Read helpers resolve a mountpoint, format a path, open/read/parse, and close.

## State and persistence behavior
Each filesystem has a static `struct fs` and a cached heap `path` that persists for the process lifetime. Initialization is once-only; mount changes after first lookup are not observed. Read/write helpers do not cache values.

## Dependencies and integration points
It uses Linux magic constants, `statfs`, `/proc/mounts`, environment variables such as `SYSFS_PATH`, `mount(2)`, pthread once/mutex primitives, local buffered `io.h`, and `debug-internal.h`. It underpins `cpu.c`, tracing path helpers, and many tools that need sysfs/procfs/debugfs paths.

## Risks and edge cases
`mount_overload()` uses `snprintf(upper_name, name_len, ...)`, which cannot write the full `PERF_<name>_ENVIRONMENT` string and limits the environment override path. `filename__write_int()` writes the full 64-byte buffer instead of the formatted string length, which can send trailing NULs/spaces to sysfs-like files. Numeric reads use `atoi()`/`strtoull()` without rigorous error-end validation. Once-only caching can become stale after remounts.

## Test signals
Use temporary mount namespaces or environment overrides to test mount discovery order, magic validation, and mount fallback. Mock files should cover integer, hex, bool, long string, missing path, oversized path, and write behavior. Threaded tests should call mount helpers concurrently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/fs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/fs.h -->
# sources/distributed-fs/ceph-client/tools/lib/api/fs/fs.h

## Purpose
`fs.h` is the public libapi interface for pseudo-filesystem mount discovery and simple sysfs/procfs file I/O. It hides common path construction and parsing for tool code.

## Important APIs, types, and functions
The `FS(name)` macro declares `name__mountpoint()`, `name__mount()`, and `name__configured()` for `sysfs`, `procfs`, `debugfs`, `tracefs`, `hugetlbfs`, and `bpf_fs`. The header also declares `cgroupfs_find_mountpoint()`, filename-level read/write helpers, `procfs__read_str()`, `sysctl__read_int()`, and typed `sysfs__read_*()`/`sysfs__write_int()` helpers. It defines `PATH_MAX` as 4096 if libc did not.

## Control flow
The header itself has no execution. The declared mountpoint functions perform lazy discovery in `fs.c`; read helpers return zero on success or negative/error values depending on the path.

## State and persistence behavior
State is internal to the implementation, mostly cached mount paths. Callers own buffers returned by `filename__read_str()`, `procfs__read_str()`, and `sysfs__read_str()` and must free them.

## Dependencies and integration points
It includes `<stdbool.h>` and `<unistd.h>` and is installed as `include/api/fs/fs.h`. It is used by libapi CPU/tracing helpers and external tools.

## Risks and edge cases
Return conventions are not fully uniform: some helpers return `-errno`, others return `-1`. Callers must not assume all failures map directly to errno. The header does not annotate ownership for returned strings.

## Test signals
Compile installed-header users and exercise the implementation tests for `fs.c` and `cgroup.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/fs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/tracing_path.c -->
# sources/distributed-fs/ceph-client/tools/lib/api/fs/tracing_path.c

## Purpose
`tracing_path.c` centralizes discovery and path construction for Linux ftrace/tracepoint event files. It prefers tracefs and falls back to debugfs tracing, matching older and newer kernel layouts.

## Important APIs, types, and functions
State is held in static `char tracing_path[PATH_MAX]`, initially `/sys/kernel/tracing`. Public functions include `tracing_path_mount()`, `tracing_path_set()`, `get_tracing_file()`, `put_tracing_file()`, `get_events_file()`, `put_events_file()`, `tracing_events__opendir()`, `tracing_events__scandir_alphasort()`, and `tracing_path__strerror_open_tp()`. Private helpers mount tracefs/debugfs and set `tracing_path`.

## Control flow
`tracing_path_mount()` first calls `tracefs__mount()` and uses the mountpoint directly if available. If not, it calls `debugfs__mount()` and appends `tracing/`. Path constructors allocate strings with `asprintf()`. Directory helpers open or scan the `events` directory. The strerror helper formats actionable messages for missing tracepoints, missing tracing filesystems, permission failures, and generic errors.

## State and persistence behavior
The static `tracing_path` buffer is process-global and mutable. `tracing_path_set()` allows callers to override it. Allocated path strings are caller-owned and freed by the matching `put_*()` helpers.

## Dependencies and integration points
It depends on `fs.h` mount helpers, GNU `asprintf`, `<dirent.h>`, Linux `str_error_r()`, and tracefs/debugfs filesystem availability. It is used by perf-style tools that enumerate or open tracepoint event files.

## Risks and edge cases
`get_tracing_file()` concatenates `tracing_path_mount()` and `name` without inserting a slash; callers must pass names with the expected leading slash or rely on the stored path ending in slash for debugfs. Some helpers call `put_events_file()` on strings allocated by `get_tracing_file()`, which is equivalent today but semantically confusing. The global path is unsynchronized.

## Test signals
Test with tracefs mounted, only debugfs tracing available, neither available, and permission-denied event files. Verify generated paths for names with and without leading slashes, event directory scans, and formatted error messages for ENOENT/EACCES.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/tracing_path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/tracing_path.h -->
# sources/distributed-fs/ceph-client/tools/lib/api/fs/tracing_path.h

## Purpose
`tracing_path.h` declares libapi helpers for locating tracefs/debugfs tracing files and formatting tracepoint-open errors.

## Important APIs, types, and functions
It declares directory helpers `tracing_events__opendir()` and `tracing_events__scandir_alphasort()`, mount/path helpers `tracing_path_set()` and `tracing_path_mount()`, allocated string constructors `get_tracing_file()` and `get_events_file()` with matching free helpers, `zput_events_file(ptr)`, and `tracing_path__strerror_open_tp()`.

## Control flow
Callers obtain a mount path or allocated file path, operate on it, and free it. The error helper converts errno values and tracepoint names into user-facing diagnostic strings.

## State and persistence behavior
The implementation owns a global tracing path; callers own allocated strings returned by `get_*_file()`.

## Dependencies and integration points
It includes `<linux/types.h>` and `<dirent.h>`, and is installed under `include/api/fs`. It is intended for perf-like tools that interact with trace events.

## Risks and edge cases
`zput_events_file()` uses `free()` but this header does not include `<stdlib.h>` directly, so include order can matter. Ownership is conventional rather than type-enforced.

## Test signals
Compile consumers using only the installed header plus standard includes, and run implementation tests from `tracing_path.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/fs/tracing_path.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/io.h -->
# sources/distributed-fs/ceph-client/tools/lib/api/io.h

## Purpose
`io.h` is a header-only lightweight buffered read library for tools. It wraps a file descriptor with a caller-supplied buffer and provides character, numeric, delimiter, and line reads without using stdio.

## Important APIs, types, and functions
`struct io` stores fd, buffer pointers, timeout, and EOF/error state. Inline helpers are `io__init()`, `io__fill_buffer()`, `io__get_char()`, `io__get_hex()`, `io__get_dec()`, `io__getdelim()`, and `io__getline()`. Numeric functions parse positive hex/decimal values into `__u64`. Delimiter reads dynamically allocate or reallocate the output line.

## Control flow
Callers initialize `struct io` with an fd and buffer. `io__get_char()` refills the buffer when consumed. If `timeout_ms` is nonzero, refill first waits with `poll(POLLIN)`. Numeric readers consume until a nonmatching character and return that terminator. `io__getdelim()` consumes through a delimiter or EOF and returns the allocated length.

## State and persistence behavior
State is entirely in caller-owned `struct io` plus the caller-supplied buffer. `eof` is sticky after EOF, timeout, or read error. Lines allocated by `io__getdelim()` are caller-owned through `*line_out`.

## Dependencies and integration points
It depends on `poll(2)`, `read(2)`, libc allocation, errno, and Linux integer types. `fs.c` uses it for full-file string reads and bool parsing.

## Risks and edge cases
`io__get_char()` returns the negative refill return directly, so EOF and errors are both `-1` with errno only sometimes meaningful. `io__getdelim()` frees any existing `*line_out` and does not preserve caller capacity despite accepting `line_len_out`; callers cannot reuse buffers. Numeric overflow intentionally drops high bits. Timeout poll does not handle `POLLERR`/`POLLHUP` as readable.

## Test signals
Use pipes or temp files to test buffered reads across buffer boundaries, decimal/hex terminators, EOF behavior, timeouts, delimiter allocation growth, and interaction with `filename__read_str()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/io_dir.h -->
# sources/distributed-fs/ceph-client/tools/lib/api/io_dir.h

## Purpose
`io_dir.h` is a header-only low-level directory reader built on the `getdents64` syscall. It avoids stdio `DIR *` overhead for tools that need compact directory iteration.

## Important APIs, types, and functions
It defines `perf_getdents64()`, `struct io_dirent64`, and `struct io_dir`. Inline helpers are `io_dir__init()`, `io_dir__rewinddir()`, `io_dir__readdir()`, and `io_dir__is_dir()`. Architecture-specific `SYS_getdents64` fallback numbers are provided when libc headers do not define the syscall number.

## Control flow
Callers open a directory fd, initialize `struct io_dir`, and repeatedly call `io_dir__readdir()`. When the internal fixed buffer is exhausted, the helper calls `getdents64` again. `io_dir__is_dir()` trusts `d_type` unless it is `DT_UNKNOWN`, in which case it calls `fstatat()`.

## State and persistence behavior
Runtime state is the directory fd, available bytes, next pointer, and a four-entry buffer embedded in `struct io_dir`. There is no persistent state. Rewind uses `lseek(fd, 0, SEEK_SET)` and clears buffered bytes.

## Dependencies and integration points
It depends on raw Linux directory entry layout, syscall numbers, `fstatat`, `lseek`, and `<linux/limits.h>`. It is used by performance-sensitive tools code that can tolerate Linux-specific APIs.

## Risks and edge cases
The embedded buffer can hold only a few dirents and assumes returned records fit in it. Fallback syscall numbers are architecture-sensitive and can age. `io_dir__readdir()` does not validate `d_reclen`, so malformed syscall output would corrupt iteration. It is Linux-only.

## Test signals
Iterate real directories with many entries, names near `NAME_MAX`, unknown `d_type` filesystems, rewind behavior, and memory-sanitizer builds that exercise the explicit zeroing path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/api/io_dir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/argv_split.c -->
# sources/distributed-fs/ceph-client/tools/lib/argv_split.c

## Purpose
`argv_split.c` provides a small helper to split a whitespace-separated string into a NULL-terminated `argv` array. It mirrors a common kernel helper but is built for userspace tools.

## Important APIs, types, and functions
Private helpers are `skip_arg()` and `count_argc()`. Public functions are `argv_split(const char *str, int *argcp)` and `argv_free(char **argv)`. It uses Linux-style `skip_spaces()`, `isspace()`, and `strndup()`.

## Control flow
`argv_split()` first counts arguments by skipping leading whitespace and scanning to the next whitespace. It allocates `argc + 1` pointers, optionally stores `argc`, duplicates each token with `strndup()`, and terminates the array with NULL. On allocation failure it frees any partially built vector through `argv_free()`.

## State and persistence behavior
All returned state is heap-owned by the caller and freed with `argv_free()`. There is no global state and no quote/escape parsing state.

## Dependencies and integration points
It depends on `tools/include/linux` compatibility headers for kernel-like string and ctype helpers. Tool parsers can use it when their syntax is simple whitespace tokenization.

## Risks and edge cases
Quotes, backslashes, and shell-like escaping are deliberately not honored. If `calloc()` fails, `argcp` is left unchanged because it is assigned only after allocation success. `argv_free()` assumes a non-NULL, NULL-terminated vector; passing NULL would dereference it.

## Test signals
Test empty strings, leading/trailing whitespace, repeated whitespace, tabs/newlines, quoted text showing non-shell behavior, allocation-failure cleanup, and `argv_free()` nulling element pointers before freeing the vector.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/argv_split.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bitmap.c -->
# sources/distributed-fs/ceph-client/tools/lib/bitmap.c

## Purpose
`bitmap.c` supplies userspace implementations of common Linux bitmap primitives for tools. It operates on arrays of `unsigned long` and mirrors kernel bitmap semantics for weights, set algebra, formatting, and bit range modification.

## Important APIs, types, and functions
Implemented functions include `__bitmap_weight()`, `__bitmap_or()`, `bitmap_scnprintf()`, `__bitmap_and()`, `__bitmap_equal()`, `__bitmap_intersects()`, `__bitmap_set()`, `__bitmap_clear()`, `__bitmap_andnot()`, `__bitmap_subset()`, and `__bitmap_xor()`. It relies on macros and helpers from `<linux/bitmap.h>` such as `BITS_PER_LONG`, `BITS_TO_LONGS`, `BITMAP_LAST_WORD_MASK`, `find_first_bit()`, `find_next_bit()`, `hweight_long()`, and `scnprintf()`.

## Control flow
Most operations loop over whole words and handle a final partial word with a mask. `bitmap_scnprintf()` walks set bits, coalesces contiguous ranges, and writes comma-separated `n` or `n-m` spans. Range set/clear calculates first/last word masks and updates full middle words with all-bits masks.

## State and persistence behavior
There is no global state. All state is in caller-provided bitmaps and output buffers. Mutating operations write directly to `dst` or `map`.

## Dependencies and integration points
This file is part of tools/lib compatibility code used by perf and other tools that include Linux bitmap APIs in userspace.

## Risks and edge cases
Callers must provide buffers sized for `BITS_TO_LONGS(bits)`. Formatting uses `size - ret` without clamping when output is truncated, so underflow risks depend on `scnprintf()` semantics. Range helpers do not validate `start + len` against the actual map allocation. Negative `len` values are not guarded.

## Test signals
Compare operations against kernel bitmap expectations for zero bits, exact word sizes, partial final words, overlapping source/destination, formatted sparse and contiguous ranges, and set/clear ranges crossing word boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/Makefile -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/Makefile

## Purpose
This Makefile builds, checks, installs, and cleans libbpf from the kernel tools tree. It produces static and shared libraries, generated helper definitions, a pkg-config file, and installable public headers.

## Important APIs, types, and functions
Key outputs are `libbpf.a`, `libbpf.so.$(LIBBPF_VERSION)`, `libbpf.so` symlinks, `libbpf.pc`, and `bpf_helper_defs.h`. It derives `LIBBPF_VERSION` from `libbpf.map`, sets `LIBBPF_MAJOR_VERSION`/`MINOR_VERSION`, builds separate shared/static object directories, invokes `scripts/bpf_doc.py` for helper definitions, and verifies ABI/version consistency with `check_abi` and `check_version`.

## Control flow
`all` depends on `fixdep` and runs `all_cmd`. Shared and static combined objects are built through the tools build system with different `OUTPUT` directories and `SHLIB_FLAGS` for shared builds. The shared library links against `-lelf -lz` with a version script and creates soname symlinks. Install targets copy libraries, pkg-config metadata, source headers, and generated headers into `prefix`/`DESTDIR`.

## State and persistence behavior
Persistent build outputs live under `OUTPUT`: libraries, symlinks, generated header, pkg-config file, temporary ABI symbol lists, and object directories. Installation persists files under `$(prefix)/lib*`, `include/bpf`, and pkg-config directories.

## Dependencies and integration points
It depends on the Linux tools build system, architecture make fragments, `readelf`, `awk`, `grep`, `sort -V`, `scripts/bpf_doc.py`, libelf, zlib, and `libbpf.map`. It is shared by kernel selftests, perf, and external libbpf builds from the tools tree.

## Risks and edge cases
`-Werror` is unconditional in appended CFLAGS, so compiler drift can break builds. ABI checks depend on `readelf` output formats. Generated helper definitions depend on a synchronized `tools/include/uapi/linux/bpf.h`. Out-of-tree `srctree` detection is make-environment-sensitive.

## Test signals
Run `make -C tools/lib/bpf` for static/shared outputs, `make check` for ABI/version validation, install into a temporary `DESTDIR`, verify `pkg-config --cflags --libs` output, and build BPF selftests against the produced headers/library.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/bpf.c

## Purpose
`bpf.c` is libbpf's low-level wrapper around the Linux `bpf(2)` syscall. It converts stable C APIs and option structs into correctly sized `union bpf_attr` payloads, handles fd sanitization, maps errno into libbpf return conventions, and provides compatibility retries for selected kernel-version differences.

## Important APIs, types, and functions
Foundational helpers are `ptr_to_u64()`, `sys_bpf()`, `sys_bpf_fd()`, and `sys_bpf_prog_load()`. Public APIs include map creation and operations, program load/query/test-run/attach/detach, BPF link create/update/detach, object pin/get, ID iteration and fd-by-id lookup, info-by-fd wrappers, raw tracepoint open, BTF load, task fd query, stats enable, program-map binding, BPF token creation, stream read, and struct_ops association. `probe_memcg_account()`, `libbpf_set_memlock_rlim()`, and `bump_rlimit_memlock()` manage old memlock accounting behavior.

## Control flow
Each wrapper validates option struct size with `OPTS_VALID()`, zeroes only the supported attr prefix with `offsetofend()`, fills command-specific fields, calls `sys_bpf()`, and returns either fd or negative errno through libbpf helpers. Program and BTF load optionally retry with verifier logs. `bpf_prog_load()` also retries after kernel-reported func/line info record-size differences by allocating zero-tailed compatibility records. `bpf_link_create()` falls back to `BPF_RAW_TRACEPOINT_OPEN` for old kernels and eligible tracing attach types.

## State and persistence behavior
Global state is limited to memlock auto-bump controls: `memlock_bumped` and `memlock_rlim`. Kernel-created maps, programs, links, BTF objects, tokens, and pinned objects persist by fd or bpffs lifetime according to kernel rules, not by this file.

## Dependencies and integration points
It depends on Linux UAPI `linux/bpf.h`, syscall numbers per architecture, libbpf internal option and error helpers, feature probing, fd hygiene, and kernel support for each BPF command. Higher-level libbpf object loading code uses these wrappers as its syscall boundary.

## Risks and edge cases
Attr sizing must track UAPI evolution exactly; too-small sizes omit features, too-large sizes can fail on older kernels. Global memlock bumping is process-wide and not thread-isolated. Many APIs require mutually exclusive option fields; validation mistakes can send ambiguous attrs. Compatibility retry code must preserve errno and caller log buffers carefully.

## Test signals
Run libbpf selftests across old/new kernels and privilege modes. Specific coverage should include map CRUD and batch ops, program load with and without logs, BTF load retry, link-create fallback, fd-by-id/info queries, memcg versus memlock accounting, token fd fields, and invalid option sizes/field combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/bpf.h

## Purpose
`bpf.h` is libbpf's public low-level BPF syscall API header. It exposes C declarations and option structs for creating/manipulating BPF maps, programs, links, BTF objects, pinned objects, tokens, and related metadata without using the higher-level ELF/object loader.

## Important APIs, types, and functions
Important option structs include `bpf_map_create_opts`, `bpf_prog_load_opts`, `bpf_btf_load_opts`, `bpf_map_batch_opts`, `bpf_obj_pin_opts`, `bpf_obj_get_opts`, `bpf_prog_attach_opts`, `bpf_prog_detach_opts`, `bpf_link_create_opts`, `bpf_link_update_opts`, `bpf_prog_query_opts`, `bpf_raw_tp_opts`, `bpf_get_fd_by_id_opts`, `bpf_test_run_opts`, `bpf_token_create_opts`, `bpf_prog_stream_read_opts`, and `bpf_prog_assoc_struct_ops_opts`. Each struct carries a `sz` field and a `__last_field` macro for forward/backward compatibility. APIs are marked `LIBBPF_API`.

## Control flow
The header defines the contract used by `bpf.c`: callers zero/initialize option structs, set `sz`, pass fds/pointers/counts, and receive fds, counts, logs, durations, revisions, or negative errors. Batch functions treat `count` as both input and output.

## State and persistence behavior
The header owns no state. It describes kernel object lifetimes mediated by fds and bpffs pins. `libbpf_set_memlock_rlim()` affects process-global behavior implemented in `bpf.c`.

## Dependencies and integration points
It includes Linux BPF UAPI types plus `libbpf_common.h` and `libbpf_legacy.h`. It is installed as a public `include/bpf/bpf.h` header and is consumed by both libbpf internals and external applications.

## Risks and edge cases
Option struct compatibility depends on callers setting `sz` correctly, usually through libbpf option macros. Some unions provide legacy aliases such as `replace_prog_fd`/`replace_fd`, so field misuse can be subtle. Documentation comments warn that batch `count` is unreliable on `EFAULT`.

## Test signals
Compile external low-level API users against the installed header, run ABI symbol checks against `libbpf.map`, and execute syscall wrapper tests from `bpf.c` for all option structs and legacy aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_core_read.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_core_read.h

## Purpose
`bpf_core_read.h` provides BPF CO-RE read, type, field, enum, and bitfield macros. It lets BPF programs read kernel data structures in a way that emits BTF relocations so libbpf can adapt offsets, sizes, signedness, and type IDs to the target kernel.

## Important APIs, types, and functions
The header defines relocation info enums (`bpf_field_info_kind`, `bpf_type_id_kind`, `bpf_type_info_kind`, `bpf_enum_value_kind`), field/type/enum helpers (`bpf_core_field_exists`, `bpf_core_type_exists`, `bpf_core_enum_value`, etc.), direct/probed bitfield macros, `bpf_core_read*()` wrappers, `bpf_core_cast()`, pointer-chasing internals, and high-level macros such as `BPF_CORE_READ()`, `BPF_CORE_READ_INTO()`, `BPF_CORE_READ_STR_INTO()`, plus user-space and non-CO-RE probe-read variants.

## Control flow
The macros expand at BPF program compile time. Clang/GCC builtins preserve access indices or type info, creating relocations in BTF sections. Runtime reads happen through helpers such as `bpf_probe_read_kernel()`, direct loads for eligible program types, or user-memory read helpers. Variadic macro machinery supports up to nine field accessors for pointer chasing.

## State and persistence behavior
There is no runtime persistent state in the header. It influences compiled BPF bytecode and relocation metadata persisted inside the BPF object file.

## Dependencies and integration points
It depends on `bpf_helpers.h`, compiler BTF builtins, kernel BTF, and libbpf CO-RE relocation processing. It integrates with BPF programs built from `vmlinux.h` or equivalent BTF-derived types.

## Risks and edge cases
CO-RE user reads still require kernel/UAPI types known to target BTF; arbitrary userspace structs are not relocatable. Big-endian bitfield reads need adjusted destination offsets. Compiler differences require separate clang/GCC type-reference paths. Deep pointer chains beyond macro limits are unsupported.

## Test signals
BPF selftests should cover field existence/offset/size, type matches, enum relocations, bitfields on little and big endian, pointer chasing, string reads, user reads, GCC and Clang builds, and fallback non-CO-RE macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_core_read.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_endian.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_endian.h

## Purpose
`bpf_endian.h` provides byte-order conversion macros usable from both BPF programs and userspace code. It avoids relying on libc byte-order headers and accounts for LLVM BPF target endianness behavior.

## Important APIs, types, and functions
Internal macros `___bpf_mvb()`, `___bpf_swab16()`, `___bpf_swab32()`, and `___bpf_swab64()` implement constant byte swaps. Public macros are `bpf_htons()`, `bpf_ntohs()`, `bpf_htonl()`, `bpf_ntohl()`, `bpf_cpu_to_be64()`, and `bpf_be64_to_cpu()`. They choose constant swabs or `__builtin_bswap*()` with `__builtin_constant_p()`.

## Control flow
Preprocessor branches inspect compiler `__BYTE_ORDER__`. Little-endian builds define conversions as swaps; big-endian builds define them as identity. Unsupported byte order triggers a compile-time error.

## State and persistence behavior
There is no state. The macros compile into constants, bswap operations, or identity expressions.

## Dependencies and integration points
It assumes Linux integer typedefs such as `__u16`, `__u32`, and `__u64` are already available, typically via `vmlinux.h`, `<linux/types.h>`, or related BPF headers. It is installed as a public libbpf BPF-program helper header.

## Risks and edge cases
Using compiler `__BYTE_ORDER__` is intentional for BPF cross-targets, but builds with misconfigured target endianness will silently produce wrong conversions. Macro arguments may be evaluated within builtin/constant expressions; callers should avoid side effects.

## Test signals
Compile BPF and userspace tests for little-endian and big-endian targets, compare constant and variable conversions, inspect generated BPF instructions for expected endian operations, and build with missing byte-order macros to confirm the compile error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_endian.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_gen_internal.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_gen_internal.h

## Purpose
`bpf_gen_internal.h` declares libbpf's internal generated-loader state and operations. This machinery builds BPF instruction/data blobs that can recreate object loading steps in a generated loader program.

## Important APIs, types, and functions
`struct ksym_relo_desc` records extern/kernel-symbol relocations by name, kind, instruction index, weakness, typeless status, and LD64 status. `struct ksym_desc` stores resolved/generated ksym metadata. `struct bpf_gen` owns loader options, data and instruction buffers, endian state, cleanup label, program/map counts, log level, error, ksym and CO-RE relocation arrays, attach target, fd array bookkeeping, and hash instruction offsets. Declared functions initialize, finish, free, load BTF, create maps, load programs, update/freeze maps, record attach targets, record externs, record CO-RE relocations, and populate outer maps.

## Control flow
Higher-level libbpf code initializes `bpf_gen`, records object-load operations as it parses maps/programs/relocations, then finishes the generated loader. The functions declared here append data and instructions while tracking errors in the `bpf_gen` state.

## State and persistence behavior
State is entirely in `struct bpf_gen` and its heap arrays/buffers. It persists across one object-generation session and is freed by `bpf_gen__free()`. Generated blobs can persist as skeleton or loader artifacts outside this header.

## Dependencies and integration points
It includes `bpf.h` and `libbpf_internal.h`, uses SHA256 sizing and `struct bpf_core_relo`, and is consumed by libbpf generator implementation files, not external applications.

## Risks and edge cases
This is an internal ABI between libbpf source files; field layout changes must be synchronized. Endianness, cleanup labels, fd-array indexing, and relocation counts are easy to corrupt because they coordinate generated instructions and runtime object indexes.

## Test signals
Build generated-loader/selftest paths, load objects with maps, inner maps, extern ksyms, weak symbols, CO-RE relocations, BTF, attach targets, and endian-swapped targets. Memory-leak tests should exercise early-error cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_gen_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_helpers.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_helpers.h

## Purpose
`bpf_helpers.h` is the primary convenience header for BPF C programs. It imports generated helper prototypes and defines macros for map definitions, ELF sections, attributes, common utilities, debug printing, open-coded iterators, and verifier-friendly loop constructs.

## Important APIs, types, and functions
It includes `bpf_helper_defs.h`, defines map declaration helpers (`__uint`, `__type`, `__array`, `__ulong`), `SEC()`, function attributes (`__always_inline`, `__noinline`, `__weak`, `__hidden`), BTF tags (`__kconfig`, `__ksym`, `__kptr*`, `__uptr`, `__arg_*`), `offsetof`, `container_of`, `barrier`, `barrier_var`, `__bpf_unreachable`, `bpf_tail_call_static()`, pin/tristate enums, `bpf_ksym_exists()`, formatting wrappers (`BPF_SEQ_PRINTF`, `BPF_SNPRINTF`, `bpf_printk`, `bpf_stream_printk`), and iterator macros `bpf_for_each`, `bpf_for`, and `bpf_repeat`.

## Control flow
Most behavior is compile-time macro expansion. Section and BTF tag macros shape the ELF/BTF that libbpf parses. Print wrappers build temporary `u64` argument arrays for helpers. Iterator macros use BPF open-coded iterator kfuncs plus cleanup attributes to create verifier-friendly loops.

## State and persistence behavior
The header itself has no persistent state, but its section macros define object-file state such as maps, program sections, `.kconfig`, and `.ksyms`. Print format strings may become static global data unless `BPF_NO_GLOBAL_DATA` is set.

## Dependencies and integration points
It depends on generated helper prototypes, compiler support for GNU attributes/pragmas, BPF target compilation, and kernel kfunc/helper availability. It is included by most libbpf-style BPF programs and by `bpf_core_read.h`/`bpf_tracing.h`.

## Risks and edge cases
Programs must include `vmlinux.h` or Linux types before this header so generated helper prototypes see `__u64` and peers. GCC and clang differ in attribute diagnostics and weak-symbol checks. `bpf_tail_call_static()` requires a constant slot. Iterator macros depend on cleanup attribute support and kfunc availability.

## Test signals
Compile BPF samples/selftests with clang and GCC, with and without global data, use map definition macros, print wrappers with more than three args, static tail calls, weak ksym existence checks, and open-coded iterator loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_prog_linfo.c -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_prog_linfo.c

## Purpose
`bpf_prog_linfo.c` builds a searchable representation of BPF program line information returned by `BPF_OBJ_GET_INFO_BY_FD`. It maps translated instruction offsets and JITed instruction addresses back to `struct bpf_line_info` records.

## Important APIs, types, and functions
`struct bpf_prog_linfo` stores raw xlated line info, optional raw JITed line info, per-JIT-function line counts, per-function start indexes, total line count, JIT function count, and record sizes. Public functions are `bpf_prog_linfo__new()`, `bpf_prog_linfo__free()`, `bpf_prog_linfo__lfind()`, and `bpf_prog_linfo__lfind_addr_func()`. `dissect_jited_func()` validates and partitions JITed line-info addresses by kernel symbol function ranges.

## Control flow
Construction validates that line info exists and has a minimum record size, copies raw xlated line info from addresses embedded in `struct bpf_prog_info`, then optionally copies JITed line info and builds per-function indexes if all required JIT metadata is present. Lookup by instruction offset or JIT address starts at an optional skip index and returns the last line record not greater than the query.

## State and persistence behavior
All state is heap-owned by `struct bpf_prog_linfo` and freed by `bpf_prog_linfo__free()`. It snapshots kernel-provided info at construction time; it does not refresh if the program changes or is unloaded.

## Dependencies and integration points
It depends on `linux/bpf.h`, `struct bpf_prog_info`, `struct bpf_line_info`, errno conventions, and libbpf allocation/error style. Higher-level libbpf consumers use it for symbolization and diagnostics.

## Risks and edge cases
The code treats numeric addresses from `bpf_prog_info` as user pointers via casts; callers must have populated the info buffers correctly. Pointer arithmetic on `void *` relies on GNU C. JIT validation assumes monotonically increasing addresses within each function. Constructor failures collapse several allocation/validation errors to `EINVAL`.

## Test signals
Load BPF programs with BTF line info, query info, construct linfo, and test lookups at exact offsets, between offsets, before first entry, with skip values, with and without JITed metadata, and with intentionally inconsistent JIT function ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_prog_linfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_tracing.h -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_tracing.h

## Purpose
`bpf_tracing.h` provides architecture-aware tracing convenience macros for BPF programs. It maps `struct pt_regs` register layouts to portable argument accessors and supplies wrappers for fentry/fexit, kprobe, kretprobe, syscall kprobe, uprobe, and uretprobe program signatures.

## Important APIs, types, and functions
The header detects target architecture through `__TARGET_ARCH_*` or compiler macros, defines per-architecture register names for normal calls, syscalls, return value, frame pointer, stack pointer, and instruction pointer, then exposes `PT_REGS_PARMn()`, `PT_REGS_PARMn_CORE()`, `PT_REGS_PARMn_SYSCALL()`, `PT_REGS_SYSCALL_REGS()`, `BPF_KPROBE_READ_RET_IP()`, and `BPF_KRETPROBE_READ_RET_IP()`. Program wrappers include `BPF_PROG`, `BPF_PROG2`, `BPF_KPROBE`, `BPF_KRETPROBE`, `BPF_KSYSCALL`, `BPF_KPROBE_SYSCALL`, `BPF_UPROBE`, and `BPF_URETPROBE`.

## Control flow
At compile time, the preprocessor selects one target mapping or emits pragma errors through placeholder accessors when no target is known. Wrapper macros generate a public BPF program function with raw context and a static inline implementation with typed arguments. `BPF_KSYSCALL` uses a `__kconfig` extern `LINUX_HAS_SYSCALL_WRAPPER` at runtime to decide how to interpret syscall pt_regs.

## State and persistence behavior
There is no mutable state in the header. It affects compiled BPF program prototypes, BTF, CO-RE relocations, and generated code. `LINUX_HAS_SYSCALL_WRAPPER` is resolved by libbpf as virtual kconfig data.

## Dependencies and integration points
It includes `bpf_helpers.h` and uses `BPF_CORE_READ()` from `bpf_core_read.h` paths via included helpers. It depends on architecture pt_regs definitions from `vmlinux.h` or UAPI/user-reg structs and is central to libbpf-style tracing programs.

## Risks and edge cases
Wrong or missing `__TARGET_ARCH_*` produces invalid register access or compile-time pragma errors. Some syscall ABI quirks are explicitly not hidden, including old mmap, clone backwards variants, socketcall, and compat syscalls. Frame-pointer based return-IP reading depends on architecture and kernel config.

## Test signals
BPF tracing selftests should compile for every supported architecture mapping, verify kprobe/uprobe/fentry wrappers pass typed arguments correctly, exercise `BPF_PROG2` struct arguments, validate syscall wrapper and non-wrapper kernels, and inspect CO-RE pt_regs reads for architectures using user-reg casts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/bpf_tracing.h -->
