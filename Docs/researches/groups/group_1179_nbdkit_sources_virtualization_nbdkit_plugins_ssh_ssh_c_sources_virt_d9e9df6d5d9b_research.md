# Group Research: group_1179_nbdkit_sources_virtualization_nbdkit_plugins_ssh_ssh_c_sources_virt_d9e9df6d5d9b

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/ssh/ssh.c -->
# File Research: sources/virtualization/nbdkit/plugins/ssh/ssh.c

Implements the `ssh` nbdkit plugin, exposing a remote regular file or block device over SSH/SFTP through libssh.

Key behavior:
- Parses connection and file parameters: `host`, `path`, `port`, `user`, `password`, SSH `config`, `known-hosts`, repeated `identity`, host-key verification, timeout, compression, and remote file creation options.
- Requires `host` and `path`; if `create=true`, also requires `create-size`.
- Uses libssh options for host/user/port/known hosts/identities/timeout/compression, then parses SSH config after setting host.
- Verifies known hosts unless `verify-remote-host=false`.
- Authenticates first with `none`, then public key, then password if provided.
- Opens an SFTP session and then opens or creates the remote file. Creation is protected by `create_lock` so parallel opens do not repeatedly truncate the target.
- Supports remote block devices by detecting `SSH_S_IFBLK`; regular files use `sftp_fstat` size, block devices use a binary-search read probe.
- Implements read/write as `sftp_seek64` followed by `sftp_read`/`sftp_write`, requiring serialized requests per handle.
- Advertises flush and multi-conn only when `fsync@openssh.com` extension version `1` is present.

Integration points:
- Registers `.magic_config_key = "path"`.
- Uses `NBDKIT_THREAD_MODEL_SERIALIZE_REQUESTS` because SFTP pread/pwrite are emulated with seek plus read/write on a shared file handle.
- Exposes debug logging through exported `ssh_debug_log` and libssh log callback.
- Depends on nbdkit helpers for password reading, bool/size parsing, vectors, cleanup, min/max.

Risks and edge cases:
- `ssh_pread` and `ssh_pwrite` assume progress from libssh. If `sftp_read` or `sftp_write` returns `0` while `count > 0`, the loop would not advance.
- Host-key verification failure modes are intentionally strict and require users to pre-populate known hosts.
- `create` is global mutable plugin state; access around create/truncate is locked, but the state is shared across connections by design.
- Block-device sizing by probing can be slow and depends on remote read behavior at out-of-range offsets.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/ssh/ssh.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/tcl/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/tcl/Makefile.am

Builds the Tcl plugin when `HAVE_TCL` is enabled.

Key behavior:
- Distributes the manpage source `nbdkit-tcl-plugin.pod` and `example.tcl`.
- Builds `nbdkit-tcl-plugin.la` from `tcl.c` and the public plugin header.
- Adds include paths for source/build `include`.
- Uses `$(TCL_CFLAGS)` and links with `$(TCL_LIBS)`.
- Adds Windows import-library support and optional linker version script.
- Generates `nbdkit-tcl-plugin.3` from POD when `HAVE_POD` is enabled.

Integration points:
- Conditional on Tcl availability.
- Follows standard nbdkit plugin libtool module flags: `-module -avoid-version -shared`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/tcl/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/tcl/tcl.c -->
# File Research: sources/virtualization/nbdkit/plugins/tcl/tcl.c

Implements the `tcl` nbdkit plugin, which loads a Tcl script and maps Tcl procedures onto nbdkit plugin callbacks.

Key behavior:
- Creates one global `Tcl_Interp` in `.load`, initializes Tcl, deletes it and calls `Tcl_Finalize` in `.unload`.
- Requires the first config parameter to be `script=/path/to/script.tcl`.
- Evaluates the script with `Tcl_EvalFile`, then verifies required procs: `plugin_open`, `get_size`, and `pread`.
- Optional Tcl callbacks include `dump_plugin`, `config`, `config_complete`, `plugin_close`, `pwrite`, `can_write`, `can_flush`, `can_trim`, `zero`, `is_rotational`, `plugin_flush`, and `trim`.
- Treats the Tcl object returned by `plugin_open` as the nbdkit handle and manages Tcl refcounts around it.
- Converts nbdkit read/write requests to Tcl calls:
  - `pread handle count offset` returns a byte array.
  - `pwrite handle bytearray offset` receives data as a Tcl byte array.
- Fallback capability behavior mirrors C plugins in several cases, such as `can_write` returning true if `pwrite` exists.

Integration points:
- Registers `.magic_config_key = "script"`.
- Uses `NBDKIT_THREAD_MODEL_SERIALIZE_ALL_REQUESTS`, matching the single global interpreter design.
- Provides Tcl version and patch-level details through `.dump_plugin`.

Risks and edge cases:
- Some boolean conversions call `Tcl_GetBooleanFromObj` without checking its return code; invalid Tcl boolean results may be silently misinterpreted.
- A Tcl `pread` result shorter than requested is rejected, but extra bytes are ignored.
- Single interpreter means plugin state is global and serialized, not per connection.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/tcl/tcl.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/tmpdisk/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/tmpdisk/Makefile.am

Builds the tmpdisk plugin on non-Windows systems.

Key behavior:
- Distributes `default-command.sh.in` and `nbdkit-tmpdisk-plugin.pod`.
- Generates `default-command.c` by stripping comments from `default-command.sh.in`, escaping quotes, converting each line to a C string, and substituting `__TRUNCATE__` with `$(TRUNCATE)`.
- Builds `nbdkit-tmpdisk-plugin.la` from `default-command.c`, `tmpdisk.c`, and public plugin header.
- Includes common utility headers and links `common/utils/libutils.la`.
- Generates `nbdkit-tmpdisk-plugin.1` from POD when `HAVE_POD` is enabled, inserting the magic-parameter text.

Integration points:
- Disabled on Windows because the plugin runs shell commands.
- Uses standard plugin module flags and optional linker script.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/tmpdisk/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/tmpdisk/default-command.sh.in -->
# File Research: sources/virtualization/nbdkit/plugins/tmpdisk/default-command.sh.in

Shell template embedded into tmpdisk as the default disk-creation command.

Key behavior:
- Defaults `type` to `ext4`.
- Chooses mkfs extra flags by filesystem family:
  - `ext?`: `-F`
  - `*fat` or `msdos`: `-I`
  - `ntfs`: `-Q -F` and label option `-n`
  - `xfs`: `-f`
- Creates the disk with substituted truncate command: `__TRUNCATE__ -s $size "$disk"`.
- Runs `mkfs -t "$type"` with optional label support.

Integration points:
- Consumed by `Makefile.am` to generate `default-command.c`.
- Relies on tmpdisk’s C code to set shell variables `disk`, `size`, and optional user-supplied variables such as `label` and `type`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/tmpdisk/default-command.sh.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/tmpdisk/tmpdisk.c -->
# File Research: sources/virtualization/nbdkit/plugins/tmpdisk/tmpdisk.c

Implements the `tmpdisk` plugin, creating one temporary formatted disk per connection and serving it through a local file descriptor.

Key behavior:
- Uses `TMPDIR` if set, otherwise `LARGE_TMPDIR`.
- Requires `size=<SIZE>`.
- Accepts `command=<COMMAND>` to replace the generated default mkfs command.
- Rejects user-supplied `disk` because it is reserved for the backing disk path.
- Treats other shell-variable-safe parameters as environment-style shell variables for the command.
- Creates a private `tmpdiskXXXXXX` directory under the tmpdir, runs the command to create `disk`, opens it read-only or read-write, determines true size with `device_size`, then unlinks the disk and removes the directory while keeping the fd.
- Implements `pread`, `pwrite`, no-op `flush`, and advisory `trim` via `fallocate(FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE)` when available.
- Advertises native FUA but intentionally ignores flush/FUA because data is temporary.
- Explicitly disables multi-conn.

Integration points:
- Uses nbdkit API v2 signatures with flags.
- `.magic_config_key = "size"`.
- Uses `NBDKIT_THREAD_MODEL_PARALLEL`.
- Uses common helpers for shell quoting, shell-variable validation, cleanup, and device sizing.

Risks and edge cases:
- User-provided `command` is executed by the shell after variable setup; this is intentional plugin behavior but security-sensitive.
- Trim errors other than `EPERM` and `EIO` are mostly ignored because trim is advisory.
- `can_trim` is compile-time based, while per-handle `can_punch_hole` can later disable punching after unsupported errors.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/tmpdisk/tmpdisk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/torrent/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/torrent/Makefile.am

Builds the BitTorrent-backed plugin when C++ and libtorrent are available.

Key behavior:
- Distributes `nbdkit-torrent-plugin.pod`.
- Builds `nbdkit-torrent-plugin.la` from `torrent.cpp` and public plugin header.
- Includes nbdkit common headers and local plugin directory.
- Compiles with warnings, pthread flags, and libtorrent flags.
- Links with common utils, Windows import support, pthreads, and libtorrent.
- Generates `nbdkit-torrent-plugin.1` from POD with magic-parameter insertion when POD support is enabled.

Integration points:
- Nested conditionals: `HAVE_CXX` and `HAVE_TORRENT`.
- Uses standard nbdkit plugin module flags and optional linker version script.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/torrent/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/torrent/torrent.cpp -->
# File Research: sources/virtualization/nbdkit/plugins/torrent/torrent.cpp

Implements the `torrent` nbdkit plugin, serving a selected file from a torrent or magnet URI as a read-only NBD export while downloading pieces on demand.

Key behavior:
- Accepts one `torrent=` value, as a local `.torrent`, `file:` URI, or `magnet:` URI. HTTP/FTP torrent download is reserved but not implemented.
- Optional `file=` selects a path inside the torrent; if omitted, the largest file is selected after metadata is available.
- Optional `cache=` selects a persistent cache directory; otherwise a temporary cache directory is created and removed on unload.
- Exposes libtorrent settings such as connection limit, rate limits, listen/outgoing interfaces, and user-agent.
- Configures DHT bootstrap nodes, sequential behavior, tracker announcement behavior, and alert categories.
- Starts libtorrent session and an alert-handling pthread in `.after_fork`.
- Waits in `.preconnect` until metadata/file selection is available.
- Opens the selected cache file once it exists, blocking until at least one piece has been downloaded if needed.
- `pread` maps file offsets to torrent pieces, raises priority for missing pieces, waits for completion, then reads from the local cache file.
- `.cache` prefetches by raising piece priority without waiting for full data.
- Reports preferred block size as torrent piece size when reasonable.

Integration points:
- Registers plugin through a C++ helper factory to avoid older toolchain/plugin initialization issues.
- Uses `NBDKIT_THREAD_MODEL_PARALLEL`.
- Uses pthread mutex/condition to coordinate libtorrent alert thread and nbdkit request threads.
- `.magic_config_key = "torrent"`.

Risks and edge cases:
- The alert thread loops indefinitely and is not explicitly joined; teardown relies on process/plugin lifetime and libtorrent/session cleanup.
- `pread` assumes local cache file data is readable once libtorrent reports a piece present.
- Only read path is implemented; no write callbacks are exposed.
- Temporary cache cleanup uses `rm -rf` on a generated path.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/torrent/torrent.cpp -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/vddk/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/vddk/Makefile.am

Builds the VMware VDDK plugin on non-Windows systems when VDDK support is enabled.

Key behavior:
- Distributes `nbdkit-vddk-plugin.pod` and `README.VDDK`.
- Builds `nbdkit-vddk-plugin.la` from:
  - `vddk.c`, `vddk.h`
  - `reexec.c`
  - `stats.c`
  - `utils.c`
  - `vddk-structs.h`
  - `vddk-stubs.h`
  - `worker.c`
- Defines default `VDDK_LIBDIR` as `$(libdir)/vmware-vix-disklib`.
- Includes common nbdkit headers and utility headers.
- Links against common utils, dynamic loader libs, and Windows import support.
- Generates `nbdkit-vddk-plugin.1` when POD support is enabled.

Integration points:
- Conditional on `HAVE_VDDK` and not Windows.
- Uses dynamic loading rather than static VDDK linkage.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/vddk/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/vddk/reexec.c -->
# File Research: sources/virtualization/nbdkit/plugins/vddk/reexec.c

Provides VDDK plugin re-exec support so `LD_LIBRARY_PATH` includes the discovered VDDK library directory before VDDK loads dependent libraries.

Key behavior:
- Hidden `noreexec` disables this behavior.
- `reexeced` stores the original `LD_LIBRARY_PATH` passed through an internal `reexeced_=` parameter.
- Reads `/proc/self/cmdline` and `/proc/self/exe` to reconstruct the original command line on Linux-like systems.
- Removes original `password=` arguments from reconstructed argv and, if a password is already available, writes it to an unlinked temporary file, passing it after re-exec as `password=-FD`.
- Appends internal `reexeced_=<old env>` argument.
- Prepends the VDDK directory to `LD_LIBRARY_PATH` and `execvp`s `/proc/self/exe`.
- `reexec_if_needed` skips re-exec when disabled, already re-execed, or when the path is already present.
- `restore_ld_library_path` restores the environment to the original value after plugin configuration completes, so child processes see the caller’s original environment.

Integration points:
- Called from VDDK library-loading code after finding a suitable shared library path.
- Depends on global VDDK config state `password` and `libdir`.

Risks and edge cases:
- Re-exec is Linux `/proc` dependent; absent proc files cause a debug-only return.
- Password preservation across re-exec is complex but avoids rereading consumed stdin/fds.
- Environment validation in restore catches garbled `reexeced_` state.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/vddk/reexec.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/vddk/stats.c -->
# File Research: sources/virtualization/nbdkit/plugins/vddk/stats.c

Implements VDDK API timing/statistics collection for `-D vddk.stats=1`.

Key behavior:
- Exports debug flag `vddk_debug_stats`.
- Defines one `struct vddk_stat stats_<api>` per VDDK API listed in `vddk-stubs.h`.
- Uses `statlist` vector to collect all stats at display time.
- Sorts stats in descending total microseconds.
- Prints VDDK function name without `VixDiskLib_` prefix, total time, call count, and byte count where applicable.
- Does nothing unless `vddk_debug_stats` is enabled.

Integration points:
- `vddk.h` macros call `update_stats` around VDDK API invocations.
- Uses `stats_lock` to protect updates.
- Called from VDDK plugin unload after `VixDiskLib_Exit`/`dlclose` handling.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/vddk/stats.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/vddk/utils.c -->
# File Research: sources/virtualization/nbdkit/plugins/vddk/utils.c

Small VDDK utility file.

Key behavior:
- Defines `trim(char *str)`, removing one trailing newline if present.
- Used for formatting VDDK log/error callback strings before forwarding them to nbdkit logging.

Integration points:
- Declared in `vddk.h`.
- Used by VDDK debug and error callback implementations in `vddk.c`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/vddk/utils.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/vddk/vddk-structs.h -->
# File Research: sources/virtualization/nbdkit/plugins/vddk/vddk-structs.h

Defines the local subset of VMware VDDK ABI types, constants, enums, and structs needed by the plugin.

Key contents:
- Vix error constants such as `VIX_OK`, `VIX_E_FAIL`, `VIX_E_NOT_SUPPORTED`, and async marker `VIX_ASYNC`.
- VDDK open flags for unbuffered, single-link, read-only, and compression modes.
- Sector size constant `VIXDISKLIB_SECTOR_SIZE = 512`.
- Disk type enum for monolithic/split/vmfs/sparse/thin/stream-optimized variants.
- Hardware version constants.
- Query-allocated-blocks chunk constants.
- Opaque connection and handle typedefs.
- Callback typedefs for logging and async completion.
- Credential and spec enums.
- `VixDiskLibConnectParams`, including UID and session-id credential unions plus VStorage object fields.
- Geometry, adapter type, disk info, block/block-list, and create-params structs.

Integration points:
- Included by `vddk.h`.
- Allows the plugin to use VDDK through `dlopen`/`dlsym` without directly including VMware headers at build time.

Risks and edge cases:
- Struct layout must match supported VDDK versions. Header comment says updated to VDDK 7.0, while the loader supports library major versions 6 through 9.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/vddk/vddk-structs.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/vddk/vddk-stubs.h -->
# File Research: sources/virtualization/nbdkit/plugins/vddk/vddk-stubs.h

Macro list of VDDK API functions dynamically resolved by the plugin.

Key behavior:
- Intended for repeated inclusion with caller-defined `STUB` and `OPTIONAL_STUB` macros.
- Lists required APIs, including:
  - Initialization/shutdown: `VixDiskLib_InitEx`, `VixDiskLib_Exit`
  - Error handling: `GetErrorText`, `FreeErrorText`
  - Connect/open/close/disconnect
  - Disk info/free info
  - Sync and async read/write
  - Create and flush
  - Wait
  - Allocated-blocks query/free
  - Allocate/free connect params
- Comments document baseline availability and that VDDK >= 6.7 is required for the currently needed APIs.
- `OPTIONAL_STUB` remains available for future APIs but is not currently used for optional behavior.

Integration points:
- Included by:
  - `vddk.c` to define global function pointers and load symbols.
  - `vddk.h` to declare extern pointers/stats.
  - `stats.c` to create stat records.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/vddk/vddk-stubs.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/vddk/vddk.c -->
# File Research: sources/virtualization/nbdkit/plugins/vddk/vddk.c

Main implementation of the VMware VDDK nbdkit plugin.

Key behavior:
- Dynamically loads `libvixDiskLib.so` versions 9, 8, 7, or 6 from `libdir`, preferring newer versions and both `lib64/` and direct paths.
- Re-execs nbdkit when needed so VDDK dependent libraries are discoverable through startup `LD_LIBRARY_PATH`.
- Parses many VDDK options:
  - Local/remote file selection: `file`, `export`
  - Library/config: `libdir`, `config`, `noreexec`
  - Auth/remote: `server`, `user`, `password`, `cookie`, `thumbprint`, `port`, `nfchostport`, `vm`, `snapshot`, `transports`
  - Open behavior: `single-link`, `unbuffered`, `compression`
  - Local create behavior: `create`, `create-size`, `create-type`, `create-adapter-type`, `create-hwversion`
- Validates local vs remote mode:
  - Local mode requires `file`.
  - Remote mode requires `file` or `export`, plus `server`, `user`, `password`, and `vm`.
  - `create=true` is local-only and requires sector-aligned positive size.
- Restores original `LD_LIBRARY_PATH` after config validation.
- Initializes VDDK in `.after_fork` because VDDK creates background threads.
- Converts VDDK log/warn/panic callbacks into nbdkit debug/error messages, demoting known CEIP/phone-home noise.
- Serializes `VixDiskLib_Open` and `VixDiskLib_Close` with `open_close_lock`.
- For each connection:
  - Allocates connect params.
  - Applies remote credentials if needed.
  - Connects with `VixDiskLib_ConnectEx`.
  - Optionally creates local VMDK once.
  - Opens the disk with flags.
  - Starts one worker thread to perform actual VDDK API I/O.
- Implements size, block size, FUA/flush, read/write, extents through commands sent to `worker.c`.

Integration points:
- Registers as `vddk`, long name `VMware VDDK plugin`, magic config key `file`.
- Uses `NBDKIT_THREAD_MODEL_PARALLEL`, with internal worker-thread serialization around VDDK calls.
- Uses API timing macros and stats from `vddk.h`/`stats.c`.
- Uses `fnmatch` for `export=<WILDCARD>` when available.

Risks and edge cases:
- VDDK behavior is sensitive to fork/thread ordering; the code deliberately defers initialization.
- Remote parameter validation is strict because VDDK can crash on NULL fields.
- `export` mode trusts the negotiated export name after wildcard matching and cannot be used for create.
- Read/write alignment constraints are enforced in worker code, not at config time.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/vddk/vddk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/vddk/vddk.h -->
# File Research: sources/virtualization/nbdkit/plugins/vddk/vddk.h

Shared internal header for the VDDK plugin implementation.

Key contents:
- Declares global dynamic loader state, VDDK library state, connection mode, config variables, debug flags, and resolved VDDK function pointers.
- Defines `VDDK_CALL_START`, `VDDK_CALL_END`, and `VDDK_CALL_END_ASYNC` macros for debug logging and stats collection around VDDK API calls.
- Defines `VDDK_ERROR` helper macro to convert `VixError` values to text via VDDK and log through nbdkit.
- Defines command queue model:
  - Command types: `INFO`, `READ`, `WRITE`, `FLUSH`, `CAN_EXTENTS`, `EXTENTS`, `STOP`
  - `struct command` with request fields, serial id, timing, mutex/condition, and status.
  - `command_queue` vector type.
- Defines per-connection `struct vddk_handle`, including VDDK connect params, connection, disk handle, worker thread, command queue, export filename, readonly flag, cached size, and cached extents.
- Declares helpers from `reexec.c`, `stats.c`, `utils.c`, and `worker.c`.
- Defines inline `update_stats`.

Integration points:
- Central contract between `vddk.c`, `worker.c`, `stats.c`, `reexec.c`, and `utils.c`.
- Pulls in nbdkit cleanup/vector/alignment/time helpers and local VDDK ABI structs.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/vddk/vddk.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/vddk/worker.c -->
# File Research: sources/virtualization/nbdkit/plugins/vddk/worker.c

Implements the per-connection VDDK worker thread and command execution path.

Key behavior:
- `send_command_and_wait` appends a stack-owned command to the handle’s queue, assigns a serial id, initializes per-command mutex/condition, signals the worker, and blocks until completion.
- Worker thread removes commands from the queue and executes VDDK API calls.
- Async read/write:
  - Requires offset and count to be 512-byte sector aligned.
  - Converts byte offsets/counts to sectors.
  - Calls `VixDiskLib_ReadAsync` or `WriteAsync`.
  - Completion callback updates stats, maps Vix result to command status, and wakes the caller.
- Flush:
  - Calls `VixDiskLib_Wait` first, then `VixDiskLib_Flush`.
- Info:
  - Calls `VixDiskLib_GetInfo` and optionally logs detailed disk geometry/metadata.
- Extents:
  - Tests `QueryAllocatedBlocks` once at worker startup with error suppression.
  - For readonly handles, pre-caches whole-disk extents on first extent request to avoid many slow serialized VDDK calls.
  - For writable handles, queries extents lazily over requested ranges.
  - Synthesizes holes between allocated blocks and handles unqueryable unaligned tail regions as allocated.
  - Marks hole extents as zero unless `single_link` is set.
- STOP waits for outstanding async commands and terminates the worker loop.

Integration points:
- Called by main `vddk.c` callbacks through `send_command_and_wait`.
- Uses VDDK API pointers and stats from `vddk.h`.
- Uses nbdkit extents APIs for NBD block status responses.

Risks and edge cases:
- Commands are stack objects owned by caller; correctness relies on caller waiting until completion before returning.
- Async commands are not marked complete in the main worker loop; completion is entirely callback-driven.
- Extent pre-caching may take noticeable time but is chosen to avoid much worse repeated `QueryAllocatedBlocks` latency.
- Query behavior must avoid VDDK’s chunk-boundary/end-of-disk limitations.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/vddk/worker.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/vram/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/vram/Makefile.am

Builds the OpenCL-backed VRAM plugin when OpenCL is available.

Key behavior:
- Distributes `nbdkit-vram-plugin.pod`.
- Builds `nbdkit-vram-plugin.la` from `opencl-errors.h`, `vram.c`, and public plugin header.
- Includes nbdkit common headers and local plugin directory.
- Compiles with warnings and `$(OPENCL_CFLAGS)`.
- Links with common utils, OpenCL libraries, and Windows import support.
- Generates `nbdkit-vram-plugin.1` from POD with magic-parameter insertion when POD support is enabled.

Integration points:
- Conditional on `HAVE_OPENCL`.
- Uses standard nbdkit plugin module flags and optional linker script.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/vram/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/vram/opencl-errors.h -->
# File Research: sources/virtualization/nbdkit/plugins/vram/opencl-errors.h

Provides OpenCL error-code-to-string support for the VRAM plugin.

Key behavior:
- Defines `opencl_errstr(cl_int err)` with a switch over common OpenCL error constants.
- Handles success, device/platform/memory/build/program/kernel/argument/queue/event/image errors, plus `CL_PLATFORM_NOT_FOUND_KHR`.
- Defaults to `"unknown OpenCL error"`.
- Defines `opencl_to_error(err, what)` macro to log `what`, numeric error, and symbolic error through `nbdkit_error`.

Integration points:
- Included by `vram.c`.
- Depends on OpenCL constants being available before inclusion.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/vram/opencl-errors.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/vram/vram.c -->
# File Research: sources/virtualization/nbdkit/plugins/vram/vram.c

Implements the `vram` plugin, serving a sparse block device backed by OpenCL device memory.

Key behavior:
- Enumerates all OpenCL devices across all platforms, collecting name, vendor, availability, global memory size, max allocation size, and queue sizes.
- Supports config:
  - `size=<SIZE>` to cap virtual disk size.
  - `device=<N|NAME>` to select OpenCL device.
- `.dump_plugin` lists detected devices and memory capabilities.
- Config validation:
  - Requires at least one OpenCL device.
  - Resolves name or index to a device.
  - Ensures max allocation supports fixed `BUFFER_SIZE` of 64 KiB.
  - Defaults disk size to device global memory and rounds up to 64 KiB.
- Detects fork between `.get_ready` and `.after_fork`, rejecting use unless nbdkit stays foreground (`-f`) because OpenCL may hang after fork.
- Allocates a vector of sparse buffer slots. Each slot lazily maps to one OpenCL `cl_mem` buffer.
- Creates OpenCL context and command queue in `.after_fork`.
- Serves all connections from shared global VRAM state and advertises multi-conn.
- Request handling:
  - `pread` reads allocated buffers with `clEnqueueReadBuffer`; sparse buffers return zeroes.
  - `pwrite` lazily allocates buffers and writes whole 64 KiB buffers, using bounce buffers for unaligned requests.
  - `zero` fills allocated buffers using `clEnqueueFillBuffer`, keeping memory allocated.
  - `trim` releases fully covered buffers, making them sparse zeroes again.
  - `extents` reports allocated vs sparse-zero regions by buffer slot.
  - `flush` is no-op because GPU memory is volatile.

Integration points:
- Uses API v2 callbacks with flags.
- Uses `NBDKIT_THREAD_MODEL_SERIALIZE_ALL_REQUESTS` because buffer locking is not implemented.
- `.magic_config_key = "size"`.
- Uses common vector/alignment/rounding helpers.

Risks and edge cases:
- The plugin intentionally refuses daemonizing/forking usage.
- Disk size is rounded up beyond requested size if not already 64 KiB aligned.
- Trim ignores unaligned head/tail portions and frees only fully covered buffers.
- No explicit can-write/can-trim/can-zero callbacks are present; nbdkit defaults depend on implemented callbacks.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/vram/vram.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/zero/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/zero/Makefile.am

Builds the minimal zero-size `zero` plugin.

Key behavior:
- Distributes `nbdkit-zero-plugin.pod`.
- Builds `nbdkit-zero-plugin.la` from `zero.c` and public plugin header.
- Uses source/build include directories.
- Links Windows import library support.
- Uses standard plugin module flags and optional linker script.
- Generates `nbdkit-zero-plugin.1` from POD when available.

Integration points:
- Not conditionally disabled; this is a simple core plugin build.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/zero/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/zero/zero.c -->
# File Research: sources/virtualization/nbdkit/plugins/zero/zero.c

Implements the `zero` plugin, a zero-length NBD export.

Key behavior:
- `.open` returns `NBDKIT_HANDLE_NOT_NEEDED`.
- `.get_size` returns `0`.
- Advertises multi-conn because all connections observe the same empty export.
- Advertises native cache with no `.cache` implementation, allowing nbdkit to treat cache requests as no-op.
- Provides `.pread` only because the plugin API expects it, but any call is treated as unexpected and fails.

Integration points:
- Uses `NBDKIT_THREAD_MODEL_PARALLEL`.
- Sets `.errno_is_preserved = 1`.

Risks and edge cases:
- Any data request would be a server/protocol logic error because size is zero; the plugin logs this explicitly.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/zero/zero.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/Makefile.am -->
# File Research: sources/virtualization/nbdkit/server/Makefile.am

Builds the main `nbdkit` server executable and related test/support artifacts.

Key behavior:
- Builds `sbin_PROGRAMS = nbdkit` from server sources covering backend dispatch, connections, crypto, debug, exports, extents, filters, locking, logging, main, parsing, password handling, protocol handshakes, public API, sockets, signals, timeouts, URI parsing, user/group handling, and formatting.
- Adds libfuzzer source conditionally.
- Defines install path macros such as `bindir`, `libdir`, `plugindir`, `filterdir`, `sbindir`, and `sysconfdir`.
- Includes nbdkit public headers and common protocol/replacement/utils headers.
- Links GnuTLS, SELinux, dl, rt, BSD, common protocol, common utils, compatibility library, and math library.
- Applies `nbdkit.syms` linker script when enabled.
- On Windows, generates `libnbdkit.a` import library and `nbdkit.def` from exported symbols.
- Generates `synopsis.c` from `docs/synopsis.txt`.
- Defines `pkgconfig_DATA = nbdkit.pc`.
- Builds and runs `test-public`, linking selected public API support files and common libraries.

Integration points:
- Central automake file for server-side executable.
- Plugin build files depend on public headers and, on Windows, import library generated here.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/backend.c -->
# File Research: sources/virtualization/nbdkit/server/backend.c

Implements core backend/filter/plugin dispatch helpers for nbdkit.

Key behavior:
- `backend_init` initializes a backend node with type, index, filename, dl handle, and next backend pointer.
- `backend_load` validates backend/plugin/filter `.name` syntax, stores a local copy, applies debug flags, and calls optional load callback.
- `backend_unload` locks unload, calls optional unload callback, optionally `dlclose`s, frees backend metadata, and releases lock.
- `backend_list_exports` and `backend_default_export` route export listing/default-name calls and cache default export names per connection/backend index.
- Defines `next_ops`, the `struct nbdkit_next_ops` used by filters to call the next backend layer.
- `backend_open` creates a per-backend `context`, determines TLS mode, resolves default export name for empty export, stores export name for plugin access, calls backend `.open`, and handles filter nesting.
- `backend_prepare` walks inner-to-outer for prepare callbacks, marking handles connected.
- `backend_finalize` walks outer-to-inner after use, marking failed state if finalize fails.
- `backend_close` closes outer-to-inner and frees context/export name.
- Capability callbacks cache results in `struct context`: size, block sizes, can-write, flush, trim, zero, fast-zero, extents, FUA, multi-conn, cache, rotational.
- Capability wrappers enforce dependencies:
  - trim/zero/FUA require write.
  - fast-zero depends on zero.
- Data-path wrappers assert connected state, valid ranges, capability preconditions, and valid flags before calling backend methods.
- Provides emulation:
  - Zero emulation writes static zero buffer chunks and handles FUA behavior.
  - Extents fallback reports allocated data.
  - Cache emulation reads into a static sink buffer.
- Ensures failed backend calls set an error value through `err`.

Integration points:
- Central runtime bridge between protocol handling, filters, and plugins.
- Uses thread-local current connection/context macros from `internal.h`.
- Debug flags `nbdkit.backend.controlpath` and `nbdkit.backend.datapath` control backend tracing.

Risks and edge cases:
- Many invariants are enforced with `assert`, so release behavior depends on earlier negotiation and state-machine correctness.
- `backend_open` failure after duplicating `exportname` frees the context but does not visibly free `c->exportname` in that failure path.
- Emulated zero/cache use static buffers; correctness depends on higher-level threading guarantees around backend calls.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/backend.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/background.c -->
# File Research: sources/virtualization/nbdkit/server/background.c

Implements daemonization/backgrounding for nbdkit.

Key behavior:
- Global `forked_into_background` records whether the server forked into background.
- On non-Windows:
  - `fork_into_background` is a no-op when `foreground` is set.
  - Otherwise forks; parent exits success.
  - Child changes directory to `/`.
  - If not verbose, redirects stderr to stdout, which should already be `/dev/null`.
  - Sets `forked_into_background` and logs the new pid.
- On Windows:
  - Requires foreground mode and reports daemonizing as unsupported.

Integration points:
- Uses global server options `foreground` and `verbose` from `internal.h`.
- Called from server startup path after standard fds have been prepared.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/background.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/server/captive.c -->
# File Research: sources/virtualization/nbdkit/server/captive.c

Implements the `--run` captive mode, where nbdkit runs as a child while an external command runs with connection variables.

Key behavior:
- No-op if `run` is unset.
- Builds a shell script in memory that exports shell variables:
  - `uri`
  - `nbd` as synonym for `uri`
  - `exportname`
  - `port`
  - `unixsocket`
  - TLS variables: `tls`, `tls_certificates`, `tls_psk`
- Appends the user-supplied `--run` command unquoted, intentionally treating it as shell code.
- Forks:
  - Parent restores original stdin/stdout, runs the shell command with `system`, collects its exit code, then checks/kills/waits for captive nbdkit child as needed. Final exit code comes primarily from the external command unless nbdkit exited unexpectedly while command succeeded.
  - Child continues as nbdkit and logs the background pid.
- On Windows, `--run` is unsupported.

Integration points:
- Uses saved stdio fds, generated connection URI/export/socket/TLS globals, and `shell_quote`.
- Supports workflows where a client command is launched with a ready NBD endpoint in environment-style shell variables.

Risks and edge cases:
- `run` command is intentionally shell-evaluated.
- Parent kills the captive nbdkit process with `SIGTERM` if the external command finishes while nbdkit is still running.
- Uses `WNOHANG` to distinguish still-running child from early nbdkit exit.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/server/captive.c -->