# Group Research: group_1175_nbdkit_sources_virtualization_nbdkit_plugins_curl_curl_c_sources_vi_db35a3c4a7c3

Scope: `Docs/research_subset_a.md` includes `sources/virtualization/nbdkit`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/curl/curl.c -->
# File Research: sources/virtualization/nbdkit/plugins/curl/curl.c

Main nbdkit callback implementation for the curl plugin. It wires the plugin lifecycle to libcurl global initialization/cleanup and to local helper modules: `config.c`, `worker.c`, `scripts.c`, and `times.c`.

Key behavior:
- Uses one nbdkit per-connection `struct handle` containing only the readonly flag.
- Allocates a fresh configured libcurl easy handle for each NBD request instead of reusing handles.
- Runs all easy handles through the single background worker/multi-handle implementation in `worker.c`.
- Uses `NBDKIT_THREAD_MODEL_PARALLEL`.
- Allows `multi-conn` only for readonly connections because writable HTTP has no reliable flush semantics.
- Implements `.get_size` with a HEAD request that collects content length and `Accept-Ranges`.
- Falls back from failed HEAD to GET only for HTTP 403, matching S3-like behavior where HEAD can be forbidden while GET works.
- Requires `Accept-Ranges: bytes` for HTTP/HTTPS URLs.
- Implements `.pread` as an HTTP GET with `CURLOPT_RANGE`.
- Implements `.pwrite` as an upload with `CURLOPT_RANGE`.

Important callbacks:
- `header_cb` detects `Accept-Ranges: bytes`.
- `write_cb` copies downloaded data into the NBD read buffer.
- `read_cb` copies NBD write data into libcurl’s upload buffer.
- `error_cb` intentionally aborts body transfer during fallback GET after headers are obtained.

Notable details:
- Range strings are formatted as `offset-offset+count`, which delegates protocol interpretation to libcurl/server behavior.
- Read/write callbacks cap copied bytes to the requested NBD count even if libcurl supplies/requests more.
- `update_times` is called after curl completion for timing diagnostics.
- `display_curl_error` combines libcurl’s status string with the per-handle error buffer.
- `plugin.config_help` is assigned from a constructor to avoid a non-constant C initializer.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/curl/curl.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/curl/curldefs.h -->
# File Research: sources/virtualization/nbdkit/plugins/curl/curldefs.h

Shared internal header for the curl plugin.

Key contents:
- Feature probes based on `CURL_AT_LEAST_VERSION`, covering newer libcurl options and info fields such as proxy CA options, `_T` timing values, `curl_multi_poll`, connection/xfer IDs, and content length as `curl_off_t`.
- Fallback `_Atomic` definition for old platforms without `<stdatomic.h>`.
- Global configuration declarations for URL, connection limits, header/cookie scripts, renew intervals, and debug flags.
- `struct handle`, the per-connection plugin handle.
- `struct curl_handle`, wrapping a `CURL *`, error buffer, read/write transfer pointers, `accept_range`, per-request copied headers, and associated worker command.
- `enum command_type` and `struct command` for worker-thread command submission and completion signaling.
- Declarations for config, worker, scripts, and timing helper modules.

Notable details:
- `struct command` contains a caller-owned mutex and condition variable. Worker completion is signaled back to the nbdkit request thread through these fields.
- `display_curl_error` standardizes nbdkit error reporting for libcurl failures.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/curl/curldefs.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/curl/scripts.c -->
# File Research: sources/virtualization/nbdkit/plugins/curl/scripts.c

Implements dynamic `header-script` and `cookie-script` support for the curl plugin.

Key behavior:
- Maintains cached output from the configured scripts.
- Re-runs scripts on first use and when the configured renew interval expires.
- Protects cached script state with a process-wide mutex.
- Exposes `url` and `iteration` shell variables to generated shell script wrappers.
- Redirects script stderr to a temporary file and reports the first error line through `nbdkit_error`.
- Applies generated headers and cookies to each curl easy handle before a request.

Header handling:
- Header script output is read line by line.
- Empty lines are ignored after trimming trailing whitespace.
- Stored headers are duplicated into each `struct curl_handle` because libcurl does not copy `CURLOPT_HTTPHEADER` lists.

Cookie handling:
- Cookie script output uses only the first non-empty trimmed line.
- Cookies are applied with `CURLOPT_COOKIE`, which libcurl copies internally.

Platform behavior:
- Non-Windows uses `mkstemp`, `open_memstream`, `popen`, `getline`, shell quoting, and curl slists.
- Windows stubs script support and reports `NOT_IMPLEMENTED_ON_WINDOWS` if scripts are configured.

Notable details:
- `scripts_unload` frees cached global header lists and cookie strings.
- The comment says curl handle exclusivity is guaranteed by handle allocation, so per-handle mutation is safe after the global script lock is released.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/curl/scripts.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/curl/times.c -->
# File Research: sources/virtualization/nbdkit/plugins/curl/times.c

Optional timing accumulator for curl requests.

Key behavior:
- Enabled by `-D curl.times=1`.
- Uses libcurl `_T` timing fields when available.
- Tracks cumulative name lookup, connection, SSL negotiation, pretransfer, first byte, total transfer, and redirect timing.
- `update_times` runs after each curl perform completion.
- `display_times` prints cumulative timing buckets when the plugin unloads.

Notable details:
- Counters are `_Atomic curl_off_t`.
- Most libcurl timing values are cumulative from request start, so `display_times` subtracts the previous cumulative value to report stage duration.
- Redirect time is treated as non-cumulative.
- `-D curl.verbose=1` causes per-request timing values to be logged as they are collected.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/curl/times.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/curl/worker.c -->
# File Research: sources/virtualization/nbdkit/plugins/curl/worker.c

Background worker implementation for the curl plugin. It owns one libcurl multi handle and runs all easy handles submitted by nbdkit request threads.

Key behavior:
- `worker_get_ready` initializes the multi handle and configures max total connections when supported.
- `worker_after_fork` creates a self-pipe and starts the worker pthread.
- Request threads send pointers to stack-allocated `struct command` objects through the pipe, then wait on the command’s condition variable.
- The worker alternates `curl_multi_perform`, completion checks, and `curl_multi_poll`/`curl_multi_wait` on curl fds plus the self-pipe.
- Completed easy handles are removed from the multi handle and their associated command is retired with the libcurl status.
- `worker_unload` sends a `STOP` command, joins the thread, closes pipe fds, removes remaining handles, frees tracked handles, and cleans up the multi handle.

Compatibility details:
- Uses `curl_multi_poll` when available, falling back to `curl_multi_wait`.
- Maintains its own vector of active handles unless libcurl provides `curl_multi_get_handles`.
- Older `curl_multi_wait` behavior includes a workaround sleep after repeated zero-fd waits.

Concurrency model:
- One worker thread owns the multi handle.
- NBD request threads own command creation and wait for command completion.
- Debug flag `-D curl.worker=1` logs command dispatch and retirement.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/curl/worker.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/data/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/data/Makefile.am

Automake build definition for `nbdkit-data-plugin`.

Key contents:
- Builds `nbdkit-data-plugin.la`.
- Source set is `data.c`, `data.h`, `format.c`, `format.h`, and the public nbdkit plugin header.
- Distributes `disk2data.pl` and `nbdkit-data-plugin.pod`.
- Includes nbdkit headers and common allocator, replacement, and utility include directories.
- Links against common allocators, utils, compatibility library, optional Windows import library, and GnuTLS.
- Adds linker version script when `USE_LINKER_SCRIPT` is enabled.
- Generates the man page and HTML documentation from POD when `HAVE_POD` is enabled.

Build significance:
- GnuTLS linkage supports base64 decoding in the data plugin when configured.
- The plugin depends on shared allocator abstractions for sparse/in-memory backing behavior.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/data/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/data/data.c -->
# File Research: sources/virtualization/nbdkit/plugins/data/data.c

Top-level nbdkit data plugin implementation. It creates a writable allocator-backed virtual disk initialized from command-line data.

Configuration:
- Requires exactly one of `raw=`, `base64=`, or `data=`.
- Accepts optional `size=`.
- Accepts optional `allocator=`, defaulting to `sparse`.
- Extra parameters are accepted only with `data=...`; they are later available to the data-format parser as `$VAR`.
- Rejects extra parameters with `raw=` or `base64=`.

Initialization:
- `data_get_ready` creates the configured allocator.
- `raw=` writes the literal command-line string.
- `base64=` decodes via GnuTLS when available.
- `data=` delegates to `read_data_format`.
- If `size=` is omitted, the export size is the initialized data size.
- Calls allocator `set_size_hint` with the final export size.

NBD behavior:
- Uses `NBDKIT_THREAD_MODEL_PARALLEL`.
- Does not need per-connection handles.
- Serves the same allocator-backed disk to all clients and advertises `multi-conn`.
- Supports read, write, zero, trim, flush, extents, native FUA, native cache no-op, fast zero, and block size reporting.
- `trim` is implemented as allocator zero.
- `flush` is a no-op because data is memory-backed.

Dump/plugin details:
- Reports base64, mlock, and zstd build support.
- Sets `.errno_is_preserved = 1`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/data/data.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/data/data.h -->
# File Research: sources/virtualization/nbdkit/plugins/data/data.h

Small shared header for the data plugin.

Key contents:
- Includes GnuTLS and defines `NBDKIT_DATA_HAVE_BASE64_SUPPORT` when both `HAVE_GNUTLS` and `HAVE_GNUTLS_BASE64_DECODE2` are available.
- Declares `get_extra_param`, which lets `format.c` resolve `$VAR` references from extra plugin command-line parameters.

Role:
- Separates optional base64 build feature detection from parser and top-level plugin logic.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/data/data.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/data/disk2data.pl -->
# File Research: sources/virtualization/nbdkit/plugins/data/disk2data.pl

Perl utility that converts a disk image into an `nbdkit data data="..." size=N` command line.

Key behavior:
- Requires exactly one disk image argument.
- Opens the input in raw mode.
- Scans byte by byte through the image.
- Skips long zero runs by emitting absolute offset directives like `@0xOFFSET`.
- Emits short zero gaps directly when that is shorter than an offset directive.
- Detects repeated short-period data patterns up to period 8.
- Emits single-byte repeats as `BYTE*N`.
- Emits multi-byte repeated patterns as `(pattern)*N`.
- Emits ordinary non-zero data as decimal byte values.
- Always prints `size=<actual file size>`.

Output formatting:
- Starts output with `nbdkit data data="`.
- Tracks a simple column count to wrap lines.
- Prefers starting offset directives on a new line when the line is already moderately long.

Use case:
- Compactly describes small or sparse disk images using the data plugin’s mini-language.
- The embedded POD warns that fully populated large images are unsuitable because command-line limits are much smaller than useful disk image sizes.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/data/disk2data.pl -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/data/format.c -->
# File Research: sources/virtualization/nbdkit/plugins/data/format.c

Parser, optimizer, and evaluator for the data plugin’s `data="..."` mini-language.

Supported expression types:
- Null and list expressions.
- Decimal/hex/octal byte values in range `0..255`.
- Absolute, relative, and aligned offsets: `@N`, `@+N`, `@-N`, `@^ALIGN`.
- File inclusion: `<FILE`.
- Script output inclusion: `<(SCRIPT)` on non-Windows.
- C-like strings with common escapes and `\xNN`.
- Repetition/fill: `expr*N`.
- Named expressions and assignment: `expr -> \name`, then `\name`.
- Slices: `expr[N:M]`, `expr[:M]`, `expr[N:]`, `expr[:]`.
- Endian words: `le16:`, `le32:`, `le64:`, `be16:`, `be32:`, `be64:`.
- Inline `base64:...` when base64 support is compiled in.
- `$VAR` expansion from plugin extra parameters first, then environment variables.
- `#` comments.

Architecture:
- Parses into a global AST table indexed by `node_id` rather than storing direct pointers.
- Node 0 is a shared null expression.
- `read_data_format` parses, optimizes, optionally prints AST debug output, evaluates into the allocator, then frees the AST table.
- GCC-only macro machinery type-checks internal `expr(...)` construction calls.

Parser details:
- Parentheses create scoped nested lists.
- Names may contain alphanumeric characters, `_`, and `-`.
- Variables require shell-like `$[A-Za-z_][A-Za-z0-9_]*`.
- Decimal offsets accept human-size suffixes via `human_size_parse_substr`; `0...` forms use numeric scanning.
- `@^ALIGN` requires a power of two.
- String numeric/unicode escapes other than `\xNN` are explicitly not implemented.

Optimization pass:
- Removes null list entries.
- Flattens lists only when scoped semantics will not change.
- Combines adjacent constants into strings or fills.
- Collapses `expr*0`, `expr*1`, nested repeats, fill repeats, small string repeats, and single-byte repeats.
- Slices constant strings, fills, bytes, and nulls when valid.
- Avoids unsafe inlining for scoped expressions such as offsets, names, and assignments.

Evaluator:
- Writes bytes, strings, fills, file/script output, repeated data, slices, and nested lists into an allocator.
- Tracks current offset and maximum observed size.
- Assignment stores an expression in a local dictionary scope.
- Name expansion evaluates the assigned expression in the environment captured when it was assigned.
- Nested lists, repeats, and generic slices are evaluated into temporary sparse allocators and blitted into the destination.
- Optimizes `<FILE[N:M]` by seeking and reading only the requested file range.
- Optimizes `<(SCRIPT)[:LEN]` by truncating script output rather than reading unbounded output.

Platform behavior:
- Non-Windows uses `popen` for scripts.
- `store_script_len` restores `SIGPIPE` to default and historically does not fail on script exit status when truncating output.
- Windows reports script inclusion as unsupported.

Notable risks/edges:
- Several offset overflow checks are marked as TODO comments.
- Some parse error paths leak transient AST/list allocations but the code treats them as fatal plugin configuration errors.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/data/format.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/data/format.h -->
# File Research: sources/virtualization/nbdkit/plugins/data/format.h

Public internal header for the data-format parser.

Key contents:
- Includes `allocator.h`.
- Declares `read_data_format(const char *value, struct allocator *a, uint64_t *size)`.

Role:
- Gives `data.c` a small interface for parsing the `data=` mini-language into an allocator while receiving the implicit data size.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/data/format.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/eval/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/eval/Makefile.am

Automake build definition for `nbdkit-eval-plugin`.

Key contents:
- Distributes `nbdkit-eval-plugin.pod`.
- Disabled on Windows because it depends on shell scripting.
- Builds `nbdkit-eval-plugin.la` when not Windows.
- Shares implementation files with `plugins/sh` by creating symlinks for `call.c`, `methods.c`, and `tmpdir.c`.
- Includes `eval.c`, the generated shared sources, sh plugin headers, and the public nbdkit plugin header.
- Includes nbdkit, sh plugin, common include, and common utils directories.
- Links against common utils and optional import library.
- Uses plugin linker flags and optional version script.
- Generates man/html documentation from POD when enabled.

Build significance:
- The eval plugin is structurally a variant of the shell plugin where callback scripts are supplied directly on the command line rather than as a separate script file.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/eval/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/eval/eval.c -->
# File Research: sources/virtualization/nbdkit/plugins/eval/eval.c

Implements the `eval` plugin, which turns command-line callback bodies into temporary executable scripts and delegates behavior to the shared shell-plugin method machinery.

Key structures:
- `known_methods` lists callback names accepted as inline methods.
- `method_scripts` stores method-to-script mappings in sorted order.
- `missing` is a generated script that exits with code 2, matching the shell plugin’s missing-callback convention.
- `subplugin sub` supplies `get_script`, `call`, `call_read`, and `call_write` to shared sh plugin code.

Lifecycle:
- `eval_load` initializes the temporary directory and creates the default `missing` script.
- `eval_unload` invokes the `unload` method if present, then tears down the tempdir, method scripts, and missing script.

Configuration:
- If a key matches a known method, `add_method` writes its value as an executable script in the tempdir.
- Duplicate method definitions are rejected.
- Method names are additionally checked for `.` and `/`.
- Unknown keys are passed to the configured `config` method.
- If no `config` method exists, unknown config keys are reported like core nbdkit would report unknown callbacks.

Completion:
- Requires `get_size` to be defined.
- Synthesizes `can_write`, `can_flush`, `can_trim`, `can_zero`, `can_extents`, and `can_cache` wrappers when the corresponding operation exists but the `can_*` method is missing.
- Calls `config_complete` when present.

Plugin registration:
- Uses the sh plugin’s implementations for thread model, lifecycle hooks, export handling, capability callbacks, data operations, extents, and cache.
- Uses `NBDKIT_THREAD_MODEL_PARALLEL`.
- Preserves errno along error paths.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/eval/eval.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/example1/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/example1/Makefile.am

Automake build definition for `nbdkit-example1-plugin`.

Key contents:
- Distributes `nbdkit-example1-plugin.pod`.
- Builds `nbdkit-example1-plugin.la` from `example1.c` and the public nbdkit plugin header.
- Includes nbdkit source and build include directories.
- Uses warning CFLAGS, plugin module linker flags, optional Windows import library, and optional linker version script.
- Generates man/html documentation from POD when enabled.

Role:
- Minimal build wrapper for the simplest C example plugin.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/example1/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/example1/example1.c -->
# File Research: sources/virtualization/nbdkit/plugins/example1/example1.c

Minimal read-only C example plugin.

Key behavior:
- Defines a static 512-byte boot sector that looks like a 100 MB disk with one empty partition.
- Defines a 100 MB static memory array.
- `.load` copies the boot sector into the start of the array.
- `.open` ignores readonly and returns `NBDKIT_HANDLE_NOT_NEEDED`.
- `.get_size` returns the static array size.
- `.pread` copies directly from the static array into the client buffer.

Threading:
- Uses `NBDKIT_THREAD_MODEL_SERIALIZE_ALL_REQUESTS` as a conservative educational default even though parallel reads would be safe.

Purpose:
- Demonstrates the minimum shape of a read-only memory-backed nbdkit C plugin: load, open, get size, read, and register.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/example1/example1.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/example2/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/example2/Makefile.am

Automake build definition for `nbdkit-example2-plugin`.

Key contents:
- Distributes `nbdkit-example2-plugin.pod`.
- Builds `nbdkit-example2-plugin.la`.
- Uses `example2.c` on non-Windows and `winexample2.c` on Windows.
- Includes nbdkit source and build include directories.
- Uses warning CFLAGS, plugin module linker flags, optional Windows import library, and optional linker version script.
- Generates man/html documentation from POD when enabled.

Role:
- Demonstrates platform-specific source selection for a simple read-only file-serving plugin.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/example2/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/example2/example2.c -->
# File Research: sources/virtualization/nbdkit/plugins/example2/example2.c

Unix implementation of a simple read-only file-server example plugin.

Configuration:
- Accepts required `file=<filename>`.
- Resolves the configured path with `nbdkit_realpath`.
- Rejects unknown parameters.
- Frees the filename on unload.
- `dump_plugin` prints a sample `example2_extra=hello` line.
- Exposes a developer debug flag `-D example2.extra=1`.

Connection handling:
- Per-connection handle contains an open file descriptor.
- `.open` opens the file `O_RDONLY|O_CLOEXEC`.
- `.close` closes the fd and frees the handle.

NBD behavior:
- `.get_size` uses `fstat`.
- Rejects block devices because the example does not implement block-device sizing.
- `.pread` loops with `pread` until the requested byte count is satisfied.
- Unexpected EOF is treated as an error.
- Uses conservative `NBDKIT_THREAD_MODEL_SERIALIZE_ALL_REQUESTS`.
- Sets `.errno_is_preserved = 1`.

Purpose:
- Educational step beyond `example1`, showing configuration, per-connection state, file descriptor management, and error handling.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/example2/example2.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/example2/winexample2.c -->
# File Research: sources/virtualization/nbdkit/plugins/example2/winexample2.c

Windows implementation of the example2 read-only file-server plugin.

Platform guard:
- Fails compilation when not building on Windows.

Configuration and lifecycle:
- Same user-facing `file=<filename>` parameter as Unix `example2.c`.
- Resolves paths with `nbdkit_realpath`.
- Frees filename on unload.
- Prints `example2_extra=hello` from `dump_plugin`.
- Provides the same developer debug flag.

Connection handling:
- Per-connection handle stores a Windows `HANDLE`.
- `.open` uses `CreateFile` with `GENERIC_READ` and shared read/write access.
- `.close` uses `CloseHandle`.

NBD behavior:
- `.get_size` uses `GetFileSizeEx`.
- `.pread` uses `ReadFile` with an `OVERLAPPED` offset.
- Uses conservative `NBDKIT_THREAD_MODEL_SERIALIZE_ALL_REQUESTS`.

Notable details:
- Unlike the Unix version, it does not loop to verify that the full requested byte count was read.
- Error reporting uses `GetLastError` numeric codes.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/example2/winexample2.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/example3/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/example3/Makefile.am

Automake build definition for `nbdkit-example3-plugin`.

Key contents:
- Distributes `nbdkit-example3-plugin.pod`.
- Disabled on Windows; the comment says a Windows port would reduce the educational value and should be a separate example.
- Builds `nbdkit-example3-plugin.la` from `example3.c` and the public nbdkit plugin header when not Windows.
- Includes nbdkit source and build include directories.
- Uses warning CFLAGS, plugin module linker flags, optional Windows import library, and optional linker version script.
- Generates man/html documentation from POD when enabled.

Role:
- Build wrapper for a read-write temporary-file example plugin.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/example3/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/example3/example3.c -->
# File Research: sources/virtualization/nbdkit/plugins/example3/example3.c

Simple read-write example plugin that stores each client’s disk in a temporary file.

Configuration:
- Optional `size=<SIZE>`, defaulting to 100 MB.
- Uses `nbdkit_parse_size`.
- Rejects unknown parameters.
- `dump_plugin` prints `example3_extra=hello`.

Connection behavior:
- Per-connection handle contains an fd for an anonymous temporary file.
- `.open` creates a temp file under `LARGE_TMPDIR`, unlinks it immediately, and `ftruncate`s it to the configured size.
- Ignores readonly, so `-r` does not change behavior.
- `.close` closes the fd and frees the handle.
- Each connection sees its own independent temporary disk.

NBD behavior:
- `.get_size` returns configured size.
- `.pread` loops with `pread`.
- `.pwrite` loops with `pwrite`.
- `.flush` uses `fdatasync`, or `fsync` when `fdatasync` is unavailable.
- Uses conservative `NBDKIT_THREAD_MODEL_SERIALIZE_ALL_REQUESTS`.
- Sets `.errno_is_preserved = 1`.

Purpose:
- Demonstrates writable plugin callbacks and per-connection transient backing storage.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/example3/example3.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/example4/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/example4/Makefile.am

Automake build definition for the Perl `nbdkit-example4-plugin`.

Key contents:
- Source script is `example4.pl`.
- Distributes the Perl source.
- Installs a generated script `nbdkit-example4-plugin` when Perl support is available.
- Rewrites `@sbindir@` in the shebang to the configured `sbindir`.
- Marks the generated plugin executable with mode `0555`.
- Generates man/html documentation from the Perl POD when `HAVE_POD` is enabled.
- Cleans generated plugin and man page artifacts.

Role:
- Shows how scripted nbdkit plugins are installed/generated rather than compiled as `.la` modules.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/example4/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/example4/example4.pl -->
# File Research: sources/virtualization/nbdkit/plugins/example4/example4.pl

Perl example plugin for nbdkit.

Configuration:
- Requires `size=<N>` in bytes.
- Rejects unknown parameters.
- `config_complete` ensures size was set.
- Does not parse human-readable sizes; it simply converts the value with Perl `int`.

Runtime behavior:
- `get_ready` allocates a scalar containing `size` zero bytes.
- `open` returns a hash handle containing the readonly flag.
- `close` is a no-op.
- `get_size` returns `length($disk)`.
- `pread` returns `substr($disk, offset, count)`.
- `pwrite` updates the shared `$disk` scalar using `substr`.
- `dump_plugin` prints `example4_extra=hello` and flushes stdout.

Semantics:
- All clients share one in-memory disk.
- The disk is discarded when nbdkit exits.
- The embedded POD documents it as a testing and Perl plugin example.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/example4/example4.pl -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/file/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/file/Makefile.am

Automake build definition for `nbdkit-file-plugin`.

Key contents:
- Distributes `nbdkit-file-plugin.pod`.
- Builds `nbdkit-file-plugin.la`.
- Uses `file.c` on non-Windows and `winfile.c` on Windows.
- Includes nbdkit headers, common include, common replacements, and common utils.
- Links common utils, common replacement compatibility library, and optional Windows import library.
- Uses plugin module linker flags and optional linker version script.
- Generates man/html documentation from POD when enabled, inserting the shared magic-parameter documentation.

Role:
- Builds the production local file/block-device plugin with platform-specific implementations.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/file/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/file/file.c -->
# File Research: sources/virtualization/nbdkit/plugins/file/file.c

Unix implementation of the production `file` plugin. It serves regular files, block devices, files inside directories, or inherited file descriptors.

Configuration modes:
- `file=<FILENAME>` or magic filename.
- `dir=<DIRNAME>` / `directory=<DIRNAME>`.
- `fd=<FD>`.
- `dirfd=<FD>`.
- Exactly one mode is allowed.
- `fadvise=normal|random|sequential`.
- `reduce-memory-pressure=true|false`.
- Legacy `cache=default|none` maps to memory-pressure behavior.
- Old `rdelay`/`wdelay` parameters are rejected with guidance to use `--filter=delay`.

Validation:
- `file=` and `fd=` must refer to regular files or block devices.
- `dir=` and `dirfd=` must refer to directories.
- File descriptors must be greater than stderr.
- Directory export names may not contain `/`.

Exports:
- File/fd modes expose the default export.
- Directory/dirfd modes list regular files and block devices in the directory and use export names to choose the file.

Open/handle state:
- Per-connection handle stores fd, name, stat data, file type, sector size, rotational flag, block-size hints, writeability, and zero/discard capability flags.
- Writable opens fall back to read-only if `O_RDWR` fails.
- `fd=` mode duplicates the incoming fd and derives writeability from `fcntl(F_GETFL)`.
- Applies `posix_fadvise` hints when available.

Capabilities:
- Parallel thread model.
- Supports multi-conn.
- Reports rotational status for block devices when available.
- Reports block size hints from Linux block ioctls when sane.
- Advertises native FUA because flush is implemented.
- Cache uses `posix_fadvise(POSIX_FADV_WILLNEED)` when available, otherwise nbdkit emulation.
- Extents are available when `SEEK_HOLE` exists and works for the opened file.

I/O behavior:
- `.get_size` uses `device_size` under an `lseek_lock`.
- `.pread` and `.pwrite` loop until the full requested count is transferred.
- `.flush` calls `fdatasync`.
- FUA writes call flush after writing.
- Optional memory-pressure mode evicts read pages with `POSIX_FADV_DONTNEED`.

Linux write eviction:
- When enabled, completed writes are queued in a fixed window list.
- Old write windows are forced out with `sync_file_range` and then advised `DONTNEED`.
- Locks protect the write-window list and prevent fd close while eviction uses an fd.

Zero/trim behavior:
- Attempts zero/trim methods in priority order.
- Uses `FALLOC_FL_PUNCH_HOLE` when trimming is allowed.
- For aligned block devices, may combine `FALLOC_FL_ZERO_RANGE` and `BLKDISCARD`.
- Uses `FALLOC_FL_ZERO_RANGE` where supported.
- Can punch then fallocate to zero without trimming.
- Can use `BLKZEROOUT` for aligned block devices.
- Disables failing capability paths after `ENOTSUP`/`EOPNOTSUPP`-style errors.
- Returns `EOPNOTSUPP` to let nbdkit fall back to writing zeroes when no zero method works.
- Trim is advisory and succeeds even when no trim method works.

Extents:
- Uses `lseek(SEEK_DATA)` and `lseek(SEEK_HOLE)` under a lock.
- Marks holes as `NBDKIT_EXTENT_HOLE | NBDKIT_EXTENT_ZERO`.
- Honors `NBDKIT_FLAG_REQ_ONE`.

Notable details:
- `.errno_is_preserved = 1`.
- `file_can_cache` returns `NBDKIT_FUA_NATIVE`/`NBDKIT_FUA_EMULATE`, which appears semantically intended as native/emulated cache support despite using FUA constants.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/file/file.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/file/winfile.c -->
# File Research: sources/virtualization/nbdkit/plugins/file/winfile.c

Windows implementation of the production `file` plugin.

Configuration:
- Supports only `[file=]<FILENAME>`.
- Resolves the path with `nbdkit_realpath`.
- Requires the file parameter in `config_complete`.
- `dump_plugin` reports `file_extents=yes` and `winfile=yes`.

Error handling:
- `windows_error` converts `GetLastError` values into strings with `FormatMessageA`.
- Errors generally include filename, Windows error code, and message.

Open/handle state:
- Opens with `CreateFile`, requesting read and optionally write access.
- If write access fails, falls back to read-only.
- Detects volume/block-device-style paths beginning with `\\.\`.
- For volumes, gets size via `IOCTL_DISK_GET_LENGTH_INFO` and block size via `IOCTL_DISK_GET_DRIVE_GEOMETRY`.
- For regular files, gets size via `GetFileSizeEx`.
- Detects sparse files with `GetFileInformationByHandle`.
- Per-connection handle stores `HANDLE`, size, readonly flag, volume flag, sparse flag, and block size.

Capabilities:
- `can_write` depends on readonly fallback.
- `can_flush` is false for readonly handles because Windows denies flushing read-only files.
- `can_trim` and `can_extents` are true only for sparse files.
- `can_zero` always true.
- Parallel thread model.
- Block size is zeroed for normal files and populated for volumes.

I/O behavior:
- `.pread` uses `ReadFile` with `OVERLAPPED` offsets.
- On invalid-parameter errors for 4K raw devices, it suggests using `--filter=blocksize` for possible unaligned reads.
- `.pwrite` uses `WriteFile` with `OVERLAPPED` offsets and flushes on FUA.
- `.flush` uses `FlushFileBuffers`.

Zero/trim/extents:
- `trim` uses `FSCTL_SET_ZERO_DATA` and requires sparse files.
- `zero` also uses `FSCTL_SET_ZERO_DATA`.
- For sparse files without `MAY_TRIM`, `zero` returns `ENOTSUP` so nbdkit can fall back to writing zeroes.
- `ERROR_NOT_SUPPORTED` from zero is translated to `ENOTSUP`.
- `extents` uses `FSCTL_QUERY_ALLOCATED_RANGES`, inserts zero-hole extents between allocated ranges, and honors `REQ_ONE`.

Notable details:
- The read/write comments note odd behavior if count exceeds 32 bits, though nbdkit passes `uint32_t`.
- `.errno_is_preserved = 1` is marked with an uncertainty comment.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/file/winfile.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/floppy/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/floppy/Makefile.am

Automake build definition for `nbdkit-floppy-plugin`.

Key contents:
- Distributes `nbdkit-floppy-plugin.pod`.
- Builds the plugin only when `HAVE_ICONV` is enabled.
- Builds `nbdkit-floppy-plugin.la` from `directory-lfn.c`, `floppy.c`, `virtual-floppy.c`, `virtual-floppy.h`, and the public nbdkit plugin header.
- Includes nbdkit headers, common include, common regions, common replacements, common utils, and the local directory.
- Links common regions, common utils, and optional Windows import library.
- Uses plugin module linker flags and optional linker version script.
- Generates man/html documentation from POD when enabled, inserting shared magic-parameter documentation.

Build significance:
- The iconv dependency gates the plugin because floppy directory/name handling depends on character set conversion support.
- The source set suggests the plugin exposes a virtual floppy image backed by directory contents and long-filename handling.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/floppy/Makefile.am -->