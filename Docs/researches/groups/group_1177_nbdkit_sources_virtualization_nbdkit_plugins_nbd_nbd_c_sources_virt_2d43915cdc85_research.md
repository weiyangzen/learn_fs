# Group Research: group_1177_nbdkit_sources_virtualization_nbdkit_plugins_nbd_nbd_c_sources_virt_2d43915cdc85

Scope verified against `Docs/research_subset_a.md`: `sources/virtualization/nbdkit` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/nbd/nbd.c -->
# File Research: sources/virtualization/nbdkit/plugins/nbd/nbd.c

Implements the `nbd` plugin, a libnbd-backed proxy that re-exports a remote NBD server through nbdkit. It supports connection by URI, Unix socket, TCP hostname/port, vsock, external command via socket activation, or pre-opened socket fd. It also supports explicit export names, dynamic export pass-through, retry, shared connections, and TLS settings.

Key state:
- `struct transaction` tracks an async libnbd command cookie, completion semaphore, early error, final error, and completion callback.
- `struct handle` owns one `struct nbd_handle`, a pipe used to wake the reader thread, readonly state, and the reader thread id.
- Global config records the chosen connection mode, export policy, retry count, shared-handle setting, and TLS parameters.

Important control flow:
- `.config` parses connection and TLS parameters.
- `.config_complete` enforces exactly one connection mode, validates URI/vsock/TLS support against libnbd, sets defaults, and rejects incompatible `dynamic-export` combinations.
- `.after_fork` creates the shared connection after daemon fork when `shared=true`, `command=`, or `socket-fd=` is used.
- `nbdplug_open_handle` creates the libnbd handle, applies export and TLS settings, negotiates, retries if requested, and starts a dedicated reader thread.
- `nbdplug_reader` polls libnbd’s fd plus the wake pipe and drives `nbd_aio_notify_read/write`.
- Synchronous nbdkit callbacks are implemented by submitting async libnbd commands, registering a completion callback, then waiting on a semaphore.

NBD operations:
- Capability callbacks mirror remote server state: write, flush, rotational, trim, zero, fast zero, FUA, multi-conn, cache, extents, and block size.
- `.pread`, `.pwrite`, `.zero`, `.trim`, `.flush`, `.cache`, and `.extents` translate nbdkit flags to libnbd command flags.
- Extents use `LIBNBD_CONTEXT_BASE_ALLOCATION`; the code relies on nbdkit extent flags matching libnbd base allocation state bits.

Research notes:
- This is concurrency-sensitive code: one background reader thread services asynchronous libnbd progress, while request threads wait per transaction.
- Shared mode deliberately returns the same handle to multiple clients; this depends on libnbd async safety and nbdkit parallel threading.
- Dynamic export support depends on newer libnbd option-mode APIs and is disabled for shared connections.
- Error preservation is advertised via `.errno_is_preserved = 1`; libnbd errors are mapped through `nbd_get_errno()` or completion callback status.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/nbd/nbd.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/nfs/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/nfs/Makefile.am

Automake build definition for the NFS plugin.

Build behavior:
- Includes shared nbdkit rules through `common-rules.mk`.
- Distributes `nbdkit-nfs-plugin.pod`.
- Builds `nbdkit-nfs-plugin.la` only under `HAVE_LIBNFS`.
- Sources are `nfs.c` and the public `nbdkit-plugin.h`.
- Adds include paths for top-level/build include dirs and local directory.
- Uses `$(LIBNFS_CFLAGS)` and links `$(LIBNFS_LIBS)`.
- Links common utility library, Windows import library support, and `$(GNUTLS_LIBS)`.
- Applies plugin shared-module flags and optional linker version script.
- If POD support is present, generates `nbdkit-nfs-plugin.1` with `podwrapper`, including the magic-parameter documentation insert.

Research notes:
- The plugin is feature-gated entirely by libnfs availability.
- Documentation generation is independent of the C source but only active when `HAVE_POD`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/nfs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/nfs/nfs.c -->
# File Research: sources/virtualization/nbdkit/plugins/nfs/nfs.c

Implements the `nfs` plugin, exposing a single file inside an NFS export as an NBD disk using libnfs.

Configuration:
- `uri=nfs://...` is required and parsed with `nfs_parse_url_full`.
- `readonly=true|false` optionally forces readonly behavior.
- `-D nfs.debug=<N>` controls libnfs RPC debug level.

Lifecycle:
- `.get_ready` initializes libnfs, wires libnfs logging to nbdkit debug output, parses the URI, validates that a filename component exists, mounts the NFS path, and opens the file.
- If libnfs was built with multithreading support, file opening is deferred until `.after_fork`, after `nfs_mt_service_thread_start`.
- `.unload` closes the file handle, stops the libnfs service thread if used, unmounts, destroys parsed URL, and destroys the libnfs context.

I/O behavior:
- Uses one global `nfs_context`, parsed URL, and file handle.
- Each nbdkit connection gets a small handle containing readonly status.
- `.get_size` uses `nfs_fstat64`.
- `.pread` loops until the requested count is filled and treats short EOF as an error.
- `.pwrite` loops through `nfs_pwrite` and honors FUA by calling `.flush`.
- `.flush` calls `nfs_fsync`.

Capabilities:
- Thread model is parallel if libnfs multithreading support exists, otherwise serialize-all-requests.
- `.can_write` is false if the client opened readonly or `readonly=true` was configured.
- `.can_multi_conn` returns true, based on libnfs guidance.
- `.block_size` reports 1 byte minimum, page size preferred, and `0xffffffff` maximum.

Research notes:
- The plugin has a single opened NFS file shared by all client connections.
- The code assumes libnfs negative errno conventions; read-side errors are checked as `r < 0`, while write-side checks `r < -1`.
- Without libnfs multithreading, all requests are serialized to protect the shared context/file handle.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/nfs/nfs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/null/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/null/Makefile.am

Automake build definition for the `null` plugin.

Build behavior:
- Always builds `nbdkit-null-plugin.la`.
- Sources are `null.c` and public `nbdkit-plugin.h`.
- Uses top-level/build include paths and standard warning flags.
- Links Windows import library support where needed.
- Uses shared-module plugin flags plus optional linker version script.
- Distributes `nbdkit-null-plugin.pod`.
- If POD support is enabled, generates `nbdkit-null-plugin.1` with magic-parameter insertion.

Research notes:
- No external feature gate or dependency library is required.
- This is one of the simplest plugin build files in the group.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/null/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/null/null.c -->
# File Research: sources/virtualization/nbdkit/plugins/null/null.c

Implements the `null` plugin: a virtual disk of configurable size that reads as zeroes and discards all writes.

Configuration:
- `size=<SIZE>` sets the exported virtual disk size and is also the magic config key.

Behavior:
- `.open` returns `NBDKIT_HANDLE_NOT_NEEDED`.
- `.get_size` returns the configured size.
- `.pread` fills the requested buffer with zero bytes.
- `.pwrite`, `.zero`, and `.trim` are no-ops.
- `.flush` is a no-op.

Capabilities:
- Parallel thread model.
- Multi-conn is safe because all connections see the same stateless zero disk.
- Cache is reported as native because data is implicit and no cache callback is needed.
- Fast zero is supported.
- FUA is native because flushing is a no-op.
- Extents report the whole disk as hole plus zero.

Research notes:
- This plugin is useful as a sink/source for testing block workflows.
- It has no persistent backing store and no per-client state.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/null/null.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/ocaml/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/ocaml/Makefile.am

Automake build definition for the OCaml plugin support library and example plugin.

Build behavior:
- Distributes `NBDKit.mli`, `NBDKit.ml`, plugin POD, `example.ml`, and `example-debug-flag.c`.
- Active only when `HAVE_OCAML` and not Windows.
- Installs OCaml interface/build artifacts: `NBDKit.mli`, `NBDKit.cmi`, `NBDKit.cmx`, `NBDKit.o`.
- Builds `libnbdkitocaml.la`, which is a support library linked into OCaml-authored plugins rather than an nbdkit plugin itself.
- Library sources are `bindings.c`, `buf.c`, `callbacks.h`, `plugin.c`, `plugin.h`, and public `nbdkit-plugin.h`.
- Compiles with `-DCAML_NAME_SPACE`, OCaml include path, nbdkit include paths, and `-fPIC`.
- Builds an example `.so` using `ocamlopt -output-obj -runtime-variant _pic`, the OCaml support library, `NBDKit.cmx`, the example object, and `example-debug-flag.o`.
- If POD support is present, generates `nbdkit-ocaml-plugin.3`; if OCamldoc is present, also generates `NBDKit.3`.

Research notes:
- This file distinguishes the reusable OCaml bridge library from actual OCaml plugins.
- Windows is disabled because the OCaml plugin path still needs porting work.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/ocaml/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/ocaml/bindings.c -->
# File Research: sources/virtualization/nbdkit/plugins/ocaml/bindings.c

Provides C stubs exposing miscellaneous nbdkit server APIs to OCaml code.

Exposed functionality:
- Error handling: `ocaml_nbdkit_set_error`.
- Parsers: size, probability, bool, and delay.
- Password and path helpers: `read_password`, `realpath`.
- Runtime/server helpers: `stdio_safe`, `nanosleep`, `export_name`, `is_tls`, `shutdown`, `disconnect`, `debug`.
- Debug buffer helpers: `debug_hexdump`, `debug_hexdiff`.
- Introspection: timestamp, package version, API version, nbdkit instance name.
- Peer identity: peer socket name where supported, pid, uid, gid, security context, TLS DN, TLS issuer DN.

Implementation details:
- Uses OCaml runtime macros (`CAMLparam`, `CAMLlocal`, `CAMLreturn`) for GC correctness.
- Converts nbdkit failures to OCaml `invalid_argument` or `failwith` exceptions.
- Uses blocking-section enter/leave around `nbdkit_nanosleep`.
- Converts allocated C strings to OCaml strings and frees the C allocation.
- Handles OCaml socket address allocation conditionally via `HAVE_CAML_SOCKETADDR_H`.

Research notes:
- This file is utility binding surface only; actual plugin callback wrapping lives in `plugin.c`.
- The bindings preserve nbdkit API semantics but necessarily collapse some C error detail into OCaml exceptions.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/ocaml/bindings.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/ocaml/buf.c -->
# File Research: sources/virtualization/nbdkit/plugins/ocaml/buf.c

Provides optimized C stubs for copying between OCaml strings/bytes and nbdkit buffer Bigarrays.

Functions:
- `ocaml_nbdkit_blit_from`: copies from an OCaml string into a Bigarray-backed nbdkit buffer.
- `ocaml_nbdkit_blit_to_bytes`: copies from a Bigarray-backed nbdkit buffer into OCaml bytes.

Implementation details:
- Uses `Caml_ba_array_val` to access Bigarray data.
- Uses `memcpy` with explicit source/destination offsets and length.
- Defines `Bytes_val` compatibility for OCaml versions before 4.06.
- Functions are marked/commented as noalloc-style stubs.

Research notes:
- This exists because OCaml-generated code for copying into Bigarrays was considered inefficient.
- Bounds are expected to be enforced by OCaml-side callers; the C stubs do raw offset arithmetic.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/ocaml/buf.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/ocaml/callbacks.h -->
# File Research: sources/virtualization/nbdkit/plugins/ocaml/callbacks.h

X-macro include file listing all OCaml plugin callbacks supported by the bridge.

Callbacks listed:
- Lifecycle/config: `load`, `unload`, `dump_plugin`, `config`, `config_complete`, `thread_model`, `get_ready`, `after_fork`, `cleanup`, `preconnect`.
- Export negotiation: `list_exports`, `default_export`, `export_description`.
- Connection: `open`, `close`.
- Capabilities: `block_size`, `can_write`, `can_flush`, `is_rotational`, `can_trim`, `can_zero`, `can_fua`, `can_fast_zero`, `can_cache`, `can_extents`, `can_multi_conn`.
- Data operations: `get_size`, `pread`, `pwrite`, `flush`, `trim`, `zero`, `extents`, `cache`.

Research notes:
- This is intentionally not a normal standalone header; it is included multiple times by `plugin.c` with different `CB(name)` definitions.
- It centralizes callback inventory so global roots, wrapper assignment, and root cleanup stay synchronized.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/ocaml/callbacks.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/ocaml/example-debug-flag.c -->
# File Research: sources/virtualization/nbdkit/plugins/ocaml/example-debug-flag.c

Small C helper for the OCaml example plugin demonstrating nbdkit debug flags.

Behavior:
- Exports `ocamlexample_debug_foo`, set by nbdkit when `-D ocamlexample.foo=<N>` is used.
- Exports `get_ocamlexample_debug_foo`, a noalloc OCaml-callable function returning the debug flag as an OCaml integer.

Research notes:
- This file is example support, not part of the reusable OCaml bridge.
- It shows how OCaml plugins can read nbdkit C debug-flag globals through tiny C stubs.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/ocaml/example-debug-flag.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/ocaml/plugin.c -->
# File Research: sources/virtualization/nbdkit/plugins/ocaml/plugin.c

Core C-to-OCaml bridge that turns an OCaml module registering callbacks into an nbdkit plugin.

Initialization:
- Defines a custom `plugin_init` instead of using `NBDKIT_REGISTER_PLUGIN`.
- Calls `caml_startup`, releases the OCaml runtime lock, initializes thread tracking, records original PID, and expects OCaml top-level code to call `NBDKit.register_plugin`.
- Uses `plugin.name == NULL` as a canary for failed OCaml registration.

Thread/runtime handling:
- For OCaml 5+, uses pthread thread-local state to register non-main nbdkit threads with the OCaml runtime and unregister them at thread teardown.
- Each wrapper calls `register_thread` and acquires the OCaml runtime for the scope.
- `.after_fork` invokes OCaml runtime atfork handling when PID changed.

Callback management:
- Uses `callbacks.h` to define one global OCaml value per callback.
- `ocaml_nbdkit_set_field` assigns C wrapper pointers into the plugin struct, stores OCaml function values, and registers them as generational GC roots.
- `remove_roots` unregisters callback roots during unload.
- `ocaml_nbdkit_set_string_field` sets plugin string fields such as name, longname, version, description, config help, and magic config key; `free_strings` releases them.

Wrapper behavior:
- Converts OCaml exceptions into nbdkit errors, with special handling for `NBDKit.Error`, `Failure`, `Invalid_argument`, and `Unix.Unix_error`.
- Wraps OCaml handles in a C `struct handle` and registers each handle value as a GC root.
- Converts list exports and extents returned from OCaml lists into nbdkit export/extent calls.
- Wraps pread/pwrite buffers as OCaml Bigarrays to avoid copying.
- Converts nbdkit flags to OCaml list constructors by integer tag.

Capabilities and I/O:
- Supports broad API v2 callback set: config, lifecycle, export, capability, read/write, zero, trim, flush, extents, cache, block size, thread model.
- `Val_flags` exposes `MAY_TRIM`, `FUA`, and `REQ_ONE`; fast-zero is not included in that conversion list in this file.
- `block_size_wrapper` validates minimum/preferred/maximum ranges; notable implementation detail: after reading maximum into `i64`, the non-`-1` branch assigns `*maximum = i`, where `i` still holds the preferred value.

Research notes:
- This file is high-sensitivity glue: runtime lock discipline, GC roots, exception translation, and buffer aliasing all affect correctness.
- The bridge allows parallel nbdkit thread model by default, but actual OCaml callback execution is serialized by the OCaml runtime lock.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/ocaml/plugin.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/ocaml/plugin.h -->
# File Research: sources/virtualization/nbdkit/plugins/ocaml/plugin.h

Shared internal header for the OCaml bridge.

Contents:
- Provides compatibility implementation of `caml_alloc_initialized_string` when missing.
- Defines `do_caml_acquire_runtime_system` and `do_caml_release_runtime_system`, with an optional debug-logging variant disabled under `#if 0`.
- Defines `ACQUIRE_RUNTIME_FOR_CURRENT_SCOPE`, a cleanup-attribute RAII-style macro that acquires the OCaml runtime and releases it at scope exit.
- Defines `cleanup_release_runtime_system`.

Research notes:
- This header keeps runtime lock pairing local and less error-prone across many wrapper functions.
- It depends on GCC/Clang cleanup attributes, matching the C style used in nbdkit common code.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/ocaml/plugin.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/ondemand/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/ondemand/Makefile.am

Automake build definition for the `ondemand` plugin.

Build behavior:
- Distributes `default-command.sh.in` and plugin POD.
- Disabled on Windows because it needs `open_memstream` and related porting work.
- Generates `default-command.c` from `default-command.sh.in` by stripping comments, escaping quotes, appending C string newlines, and substituting `__TRUNCATE__` with `$(TRUNCATE)`.
- Builds `nbdkit-ondemand-plugin.la` from generated `default-command.c`, `ondemand.c`, and public `nbdkit-plugin.h`.
- Includes nbdkit headers plus common include/replacements/utils paths.
- Links common utils and compatibility libraries.
- Uses plugin shared-module flags and optional linker version script.
- If POD support is present, generates `nbdkit-ondemand-plugin.1` with magic-parameter insertion.

Research notes:
- The generated C source embeds a shell script as `const char *command`.
- Build-time substitution selects the configured truncate implementation.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/ondemand/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/ondemand/default-command.sh.in -->
# File Research: sources/virtualization/nbdkit/plugins/ondemand/default-command.sh.in

Default shell command template embedded into the ondemand plugin.

Behavior:
- Defaults filesystem `type` to `ext4`.
- Chooses mkfs extra flags by filesystem family:
  - `ext?`: `-F`
  - `*fat` or `msdos`: `-I`
  - `ntfs`: `-Q -F` and label option `-n`
  - `xfs`: `-f`
- Creates/truncates the target disk using `__TRUNCATE__ -s $size "$disk"`.
- Runs `mkfs -t "$type"` with optional label handling.

Research notes:
- `__TRUNCATE__` is replaced at build time by `Makefile.am`.
- Variables such as `disk`, `size`, `type`, and `label` are supplied by `ondemand.c` before executing the generated command.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/ondemand/default-command.sh.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/ondemand/ondemand.c -->
# File Research: sources/virtualization/nbdkit/plugins/ondemand/ondemand.c

Implements the `ondemand` plugin, which lazily creates filesystem images in an export directory and serves them as NBD exports.

Configuration:
- Required: `dir=<EXPORTSDIR>` and `size=<SIZE>`.
- Optional: `command=<COMMAND>`, `wait=<BOOL>`, `share=<BOOL>`, and arbitrary shell-variable parameters.
- Rejects user-supplied `disk=` because that variable is reserved for the generated command.
- Unknown keys that are valid shell variable names are stored and forwarded into the command environment.

Lifecycle and exports:
- `.get_ready` opens the export directory.
- `.list_exports` returns default export first as `""`, then scans directory entries, filtering invalid names and hidden/dot entries.
- `.default_export` canonicalizes the empty export to `default`.
- Export names are rejected if empty, too long, hidden, containing `/`, or dot-style names.

Disk creation:
- `ondemand_open` serializes creation with `open_lock`.
- Attempts to open the export file; if missing, builds the disk path and runs the configured or default command.
- `run_command` uses `open_memstream` to construct a shell script, redirects stdin/stdout to `/dev/null`, shell-quotes variables, appends the command, runs it with `system`, and deletes the disk on command failure.

Locking:
- Unless `share=true`, `lock_export` uses Linux OFD locks (`F_OFD_SETLK`/`F_OFD_SETLKW`) to prevent multiple clients from corrupting the same filesystem image.
- `wait=true` waits for the lock instead of immediately failing.
- `.can_multi_conn` returns false because current locking does not support multiple NBD connections to the same export.

I/O:
- Handle stores fd, size, export name, and whether hole punching is still viable.
- `.get_size` returns the probed device/file size.
- `.pread` and `.pwrite` loop through POSIX pread/pwrite.
- `.flush` uses `fdatasync`.
- `.trim` attempts `fallocate(FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE)` when available, disables future punch attempts on unsupported errors, ignores advisory trim failures except EPERM/EIO, and honors FUA with flush.

Research notes:
- The command execution path is carefully shell-quoted for variable values, but the configured `command` itself is trusted shell code.
- The plugin is Linux/POSIX-oriented and explicitly disabled on Windows.
- Export-name validation is central to preventing directory traversal.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/ondemand/ondemand.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/ones/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/ones/Makefile.am

Automake build definition for the `ones` plugin.

Build behavior:
- Always builds `nbdkit-ones-plugin.la`.
- Sources are `ones.c` and public `nbdkit-plugin.h`.
- Uses top-level/build include paths and warning flags.
- Links Windows import library support where needed.
- Uses standard plugin shared-module flags and optional linker version script.
- Distributes `nbdkit-ones-plugin.pod`.
- If POD support is present, generates `nbdkit-ones-plugin.1` with magic-parameter insertion.

Research notes:
- Structurally mirrors the `null` plugin build file.
- No external libraries are required.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/ones/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/ones/ones.c -->
# File Research: sources/virtualization/nbdkit/plugins/ones/ones.c

Implements the `ones` plugin: a virtual disk of configurable size whose reads return a repeated byte, defaulting to `0xff`.

Configuration:
- `size=<SIZE>` sets disk size and is the magic config key.
- `byte=<BYTE>` sets the repeated byte via `nbdkit_parse_uint8_t`.

Behavior:
- `.open` returns `NBDKIT_HANDLE_NOT_NEEDED`.
- `.get_size` returns configured size.
- `.pread` fills the buffer with `databyte`.
- `.pwrite`, `.zero`, `.trim`, and `.flush` are no-ops.

Capabilities:
- Parallel thread model.
- Multi-conn is safe.
- Cache is native because data is implicit.
- Fast zero is supported.
- FUA is native because flush is a no-op.
- Extents report the whole disk as allocated data, unlike `null`, which reports hole/zero.

Research notes:
- Despite the name, `byte=` makes it a generic repeated-byte source.
- Writes are accepted but discarded.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/ones/ones.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/partitioning/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/partitioning/Makefile.am

Automake build definition for the `partitioning` plugin.

Build behavior:
- Distributes `nbdkit-partitioning-plugin.pod`.
- Disabled on Windows because `device_size` is unsupported.
- Builds `nbdkit-partitioning-plugin.la` from `partitioning.c`, `partition-gpt.c`, `partition-mbr.c`, `virtual-disk.c`, `virtual-disk.h`, and public `nbdkit-plugin.h`.
- Includes common GPT, include, regions, replacements, and utils directories.
- Links common GPT, regions, utils, and compatibility libraries.
- Uses plugin shared-module flags plus optional linker version script.
- If POD support is present, generates `nbdkit-partitioning-plugin.1` with magic-parameter insertion.

Research notes:
- The build dependencies reflect the plugin’s split between virtual-disk region mapping and partition table encoding.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/partitioning/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/partitioning/partition-gpt.c -->
# File Research: sources/virtualization/nbdkit/plugins/partitioning/partition-gpt.c

Creates GPT metadata for the partitioning plugin.

Main behavior:
- `create_gpt_layout` builds:
  - protective MBR at LBA 0,
  - primary partition table array,
  - primary GPT header,
  - backup partition table array,
  - backup GPT header.
- `create_gpt_partition_header` fills GPT header fields, LBA ranges, partition-table location, partition entry counts/sizes, partition array CRC, and final header CRC.
- `create_gpt_partition_table` scans virtual disk regions and emits entries for each file-backed partition.
- `create_gpt_partition_table_entry` writes partition type GUID, per-file unique GUID, first/last LBA, bootable attribute for first partition, and an optional UTF-16LE ASCII filename.
- `create_gpt_protective_mbr` emits an MBR partition entry of type `0xee` spanning the disk or MBR-addressable maximum.

GUID parsing:
- `parse_guid` accepts canonical 36-character GUIDs or brace-wrapped 38-character form.
- Validates hyphen positions and hex digits.
- Converts the first three GUID fields to little-endian byte order and the remaining fields to big-endian byte order, matching GPT representation.

Research notes:
- GPT array sizing depends on `GPT_PTA_SIZE` and `GPT_PTA_LBAs` from `virtual-disk.h`.
- Partition names may reveal server-side filenames when filenames are short 7-bit ASCII; the source comments call this out.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/partitioning/partition-gpt.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/partitioning/partition-mbr.c -->
# File Research: sources/virtualization/nbdkit/plugins/partitioning/partition-mbr.c

Creates MBR and EBR metadata for the partitioning plugin.

Main behavior:
- `create_mbr_layout` writes boot signatures and partition entries.
- For up to four files, each file becomes a primary partition entry.
- For more than four files:
  - first three files become primary partitions,
  - fourth primary entry becomes an extended partition,
  - remaining files become logical partitions described by EBR sectors.
- EBR entries describe the logical partition relative to the EBR sector and, when needed, the next EBR relative to the extended partition start.

Helpers:
- `find_file_region` scans the virtual region list for a file-backed region matching a file index.
- `find_ebr_region` finds the EBR data region for logical partitions.
- `chs_too_large` writes a saturated CHS value.
- `create_mbr_partition_table_entry` writes boot flag, CHS placeholders, partition id, start sector, and sector count in little-endian form.

Research notes:
- MBR size constraints are checked earlier in `partitioning_config_complete`.
- Region ordering matters; helper functions use a scratch scan index for linear traversal.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/partitioning/partition-mbr.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/partitioning/partitioning.c -->
# File Research: sources/virtualization/nbdkit/plugins/partitioning/partitioning.c

Main nbdkit plugin implementation for composing multiple files into a virtual partitioned disk.

Configuration:
- `file=<FILENAME>` may be repeated; each file becomes a partition.
- `partition-type=mbr|dos|gpt` selects table format; if omitted, the plugin chooses MBR unless size/file-count requires GPT.
- `alignment=<N>` sets following partition alignment.
- `mbr-id=default|0xN` sets following MBR partition type byte.
- `type-guid=default|GUID` sets following GPT partition type GUID.

File setup:
- Each `file=` is opened read/write.
- Size is obtained with `device_size`.
- Zero-length partitions are rejected.
- A random 16-byte unique GUID is generated per file for GPT.
- Per-file alignment, MBR id, and GPT type GUID snapshot the current config state when the file is added.

Lifecycle:
- `.load` initializes region vector, default GPT type GUID, and random state.
- `.config_complete` requires at least one file, computes total size, selects default partition type, and rejects too-large MBR requests.
- `.get_ready` calls `create_virtual_disk_layout`.
- `.unload` closes file fds and frees file vector, regions, partition table buffers, and EBR buffers.

I/O model:
- The virtual disk is a sequence of regions: generated partition metadata, file-backed partitions, and zero padding.
- `.get_size` returns total virtual size.
- `.pread` locates regions by offset and reads from file, copies generated metadata, or fills zeroes.
- `.pwrite` writes through to file regions only. Writes to generated metadata must match existing bytes; writes to padding must be zero, otherwise EIO.
- `.flush` fdatasyncs all underlying files.

Capabilities:
- Parallel thread model.
- Multi-conn is advertised.
- Cache is emulated by nbdkit through pread.

Research notes:
- This plugin intentionally protects generated partition table bytes from mutation.
- It depends on `regions` common code for virtual address mapping.
- File fds are global and shared by all connections.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/partitioning/partitioning.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/partitioning/virtual-disk.c -->
# File Research: sources/virtualization/nbdkit/plugins/partitioning/virtual-disk.c

Builds the virtual disk layout used by the partitioning plugin.

Main function:
- `create_virtual_disk_layout` allocates metadata buffers, constructs the region list, and delegates partition table encoding.

Layout behavior:
- For MBR:
  - allocates one sector for the primary MBR.
  - if more than four files, allocates EBR sectors for logical partitions.
  - appends the MBR as a data region.
- For GPT:
  - allocates primary metadata buffer covering protective MBR, primary header, and primary partition array.
  - allocates secondary metadata buffer covering backup partition array and backup header.
  - appends primary GPT metadata at the start and secondary GPT metadata at the end.
- For each file:
  - appends an EBR before logical MBR partitions when needed.
  - appends a file-backed region using requested alignment and sector-size padding.
- Optionally logs all regions when `partitioning_debug_regions` is set.
- Verifies partition region alignment and then calls `create_partition_table`.

Research notes:
- This file owns the high-level virtual address plan; `partition-mbr.c` and `partition-gpt.c` only fill already allocated metadata buffers.
- Generated metadata buffers are referenced by region data pointers and freed by `partitioning_unload`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/partitioning/virtual-disk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/partitioning/virtual-disk.h -->
# File Research: sources/virtualization/nbdkit/plugins/partitioning/virtual-disk.h

Shared internal header for the partitioning plugin.

Defines:
- Sector size: 512 bytes.
- Maximum approximate MBR disk size.
- GPT partition table array sizing macros.
- Maximum/default alignment: 2048 sectors.
- Default MBR id `0x83`.
- Default GPT Linux filesystem type GUID.
- Partition type constants for unset, MBR, and GPT.

Declares global state:
- Debug flag, current alignment, current MBR id, current GPT type GUID, selected partition type.
- `struct file` and vector type for command-line files.
- Global vectors/buffers: `the_files`, `the_regions`, `primary`, `secondary`, and `ebr`.

Declares functions:
- `create_virtual_disk_layout`.
- `parse_guid`.
- `create_mbr_partition_table_entry`.
- `create_mbr_layout`.
- `create_gpt_layout`.

Research notes:
- This header exposes globals shared across the plugin’s split implementation files.
- The `struct file` stores both backing file metadata and per-partition table attributes captured at config time.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/partitioning/virtual-disk.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/pattern/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/pattern/Makefile.am

Automake build definition for the `pattern` plugin.

Build behavior:
- Always builds `nbdkit-pattern-plugin.la`.
- Sources are `pattern.c` and public `nbdkit-plugin.h`.
- Uses nbdkit include paths plus common include/utils paths.
- Links common utils, compatibility library, and Windows import support.
- Uses plugin shared-module flags and optional linker version script.
- Distributes `nbdkit-pattern-plugin.pod`.
- If POD support is present, generates `nbdkit-pattern-plugin.1` with magic-parameter insertion.

Research notes:
- The common utils dependency supplies helpers used by the deterministic data pattern implementation.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/pattern/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/pattern/pattern.c -->
# File Research: sources/virtualization/nbdkit/plugins/pattern/pattern.c

Implements the `pattern` plugin, a deterministic virtual disk where reads encode offsets into data.

Configuration:
- `size=<SIZE>` sets virtual disk size and is the magic config key.
- `stride=<BLOCK_SIZE>` sets spacing between encoded 8-byte offset words; must be at least 8 and power-of-two.
- `upper=BITS|random` sets upper 16 bits mixed into each encoded word; `random` chooses a nonzero random value.

Behavior:
- `.load` seeds random state.
- `.open` returns `NBDKIT_HANDLE_NOT_NEEDED`.
- `.get_size` returns configured size.
- `.pread` writes big-endian 64-bit values equal to `upper ^ offset` at each stride boundary, with zero-filled gaps when stride exceeds 8.
- Handles unaligned reads with a slow path that emits partial encoded words correctly.
- `.pwrite` generates the expected pattern for the requested range and verifies the client wrote exactly that data; mismatch returns EIO.

Capabilities:
- Parallel thread model.
- Multi-conn is safe.
- Cache is native because generated data is deterministic and memory-resident.

Research notes:
- Useful for testing data integrity through block stacks.
- Writes do not alter state; they are validation checks against the generated pattern.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/pattern/pattern.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/perl/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/perl/Makefile.am

Automake build definition for the Perl plugin.

Build behavior:
- Distributes `nbdkit-perl-plugin.pod` and `example.pl`.
- Active only when `HAVE_PERL`.
- Builds `nbdkit-perl-plugin.la` from `perl.c` and public `nbdkit-plugin.h`.
- Uses nbdkit include paths, common include/utils, `$(PERL_CFLAGS)`, and Perl CORE include path.
- Links common utils, Windows import support, and `$(PERL_LDOPTS)`.
- Uses shared-module plugin flags and optional linker version script.
- If POD support is present, generates `nbdkit-perl-plugin.3`.

Research notes:
- The plugin embeds a Perl interpreter and therefore depends on Perl development/linker flags discovered by configure.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/perl/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/perl/example.pl -->
# File Research: sources/virtualization/nbdkit/plugins/perl/example.pl

Example Perl plugin implementing a 1 MiB in-memory ramdisk.

Behavior:
- Stores disk data in a global Perl string initialized with zero bytes.
- `config` prints and ignores extra parameters.
- `open` logs readonly state and returns a hashref handle.
- `get_size` returns disk string length.
- `pread` returns a substring for the requested offset/count.
- `pwrite` replaces a substring with client data.
- `zero` handles `Nbdkit::FLAG_MAY_TRIM` by writing zero bytes; otherwise sets `EOPNOTSUPP` via `Nbdkit::set_error` and dies to request fallback.

Research notes:
- Demonstrates required Perl callbacks and nbdkit flag constants.
- Uses POSIX errno constants for explicit error signaling.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/perl/example.pl -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/perl/perl.c -->
# File Research: sources/virtualization/nbdkit/plugins/perl/perl.c

Embeds Perl and exposes Perl scripts as nbdkit plugins.

Interpreter lifecycle:
- `.load` initializes Perl system state, allocates, and constructs an interpreter.
- Full script parsing is deferred until the first config parameter, which must be `script=<path>`.
- `.unload` destructs and frees the interpreter and terminates Perl system state.

Script loading/config:
- `perl_config` enforces that the first parameter is `script`.
- Parses and runs the Perl script.
- Requires `open`, `get_size`, and `pread` callbacks.
- Subsequent config parameters are forwarded to Perl `config` if defined; otherwise rejected.
- Supports optional `config_complete`, `get_ready`, and `dump_plugin`.

Perl API:
- Registers XS functions `Nbdkit::debug` and `Nbdkit::set_error`.
- Publishes nbdkit flag/capability constants into the `Nbdkit::` namespace.

Callback mapping:
- `.open` calls Perl `open`, copies returned SV, and uses it as the nbdkit handle.
- `.close` optionally calls Perl `close`, then decrements handle refcount.
- `.get_size`, `.pread`, `.pwrite`, `.flush`, `.trim`, `.zero` dispatch to Perl callbacks.
- Boolean capabilities call explicit `can_*` callback if present, otherwise infer support from implementation callback presence.
- `zero` has special fallback handling for `EOPNOTSUPP`/`ENOTSUP`.

Error handling:
- `check_perl_failure` checks `$@`, strips trailing newline, and reports through `nbdkit_error`.
- `last_error` tracks `Nbdkit::set_error` use for zero fallback.
- Thread model is serialize-all-requests; `.open` also calls `PERL_SET_CONTEXT` for threads created by nbdkit.

Research notes:
- This bridge uses scalar strings for pread buffers and copies returned Perl bytes into nbdkit buffers.
- It does not advertise `.errno_is_preserved`; error mapping is driven through nbdkit error APIs and Perl exceptions.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/perl/perl.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/python/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/python/Makefile.am

Automake build definition for the Python plugin.

Build behavior:
- Distributes plugin POD and example Python plugins: `file.py`, `error.py`, `imageio.py`, `ramdisk.py`, and `url.py`.
- Active only when `HAVE_PYTHON`.
- Builds `nbdkit-python-plugin.la` from `errors.c`, `helpers.c`, `modfunctions.c`, `plugin.c`, `plugin.h`, and public `nbdkit-plugin.h`.
- Uses nbdkit include paths, common include/utils, Python compiler flags, and Python linker flags/libs.
- Links common utils and Windows import support.
- Uses plugin shared-module flags and optional linker version script.
- If POD support is present, generates `nbdkit-python-plugin.3`.

Research notes:
- This work item includes the Python helper/module files and examples, but not `plugin.c`/`plugin.h`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/python/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/python/errors.c -->
# File Research: sources/virtualization/nbdkit/plugins/python/errors.c

Python bridge error-reporting helper.

Behavior:
- `check_python_failure(callback)` detects pending Python exceptions.
- Fetches and normalizes exception type, value, and traceback.
- Attempts to import Python’s `traceback` module and call `format_exception`.
- Joins formatted traceback into a string and reports it via `nbdkit_error` with script and callback context.
- Falls back to `PyObject_Str(error)` if full traceback formatting fails.

Research notes:
- This file centralizes conversion from Python exceptions to nbdkit errors.
- Reference cleanup is partial in some fallback/error paths, but the main purpose is diagnostic reporting before returning `-1`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/python/errors.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/python/examples/error.py -->
# File Research: sources/virtualization/nbdkit/plugins/python/examples/error.py

Example Python plugin for testing NBD client error handling.

Behavior:
- Requires `file=<path>` and opens it per connection.
- Maintains a global call counter.
- Every odd call to `extents`, `pread`, or `pwrite` raises a runtime error; every even call succeeds unless the underlying file operation fails.
- Uses `THREAD_MODEL_SERIALIZE_ALL_REQUESTS` because it uses shared `lseek` plus readv/writev sequences.
- `can_extents` returns true, while `extents` reports the requested range as data on successful calls.

Research notes:
- This example intentionally injects intermittent failures.
- It demonstrates API version 2 buffer usage for read/write callbacks.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/python/examples/error.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/python/examples/file.py -->
# File Research: sources/virtualization/nbdkit/plugins/python/examples/file.py

Example Python plugin serving a local file.

Configuration:
- `file=<path>` is required and converted to an absolute path.
- Unknown config keys raise runtime errors.

Behavior:
- Returns parallel thread model.
- `open` opens the file readonly or read/write according to client mode.
- Handle stores the fd.
- `get_size` returns `os.stat(fd).st_size`.
- `pread` uses `os.preadv` into the provided buffer and rejects short reads.
- `pwrite` uses `os.pwritev` from the provided buffer and rejects short writes.

Research notes:
- Demonstrates Python API v2 zero-copy-ish buffer protocol usage.
- The example does not define `close`, so fd lifetime depends on process cleanup or bridge behavior not shown in this file.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/python/examples/file.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/python/examples/imageio.py -->
# File Research: sources/virtualization/nbdkit/plugins/python/examples/imageio.py

Example Python plugin bridging nbdkit to oVirt imageio transfers.

Configuration:
- `transfer_url` is required.
- `connections` controls imageio client pool size.
- `ca_file` supplies CA path.
- `secure` parses yes/true/1 and no/false variants.

Behavior:
- Uses API version 2.
- Returns parallel thread model.
- `open` creates a `queue.Queue` of `ImageioClient` connections.
- `close` drains the pool and closes clients.
- A context manager checks a client out of the pool for each operation and returns it afterward.
- `get_size`, `pread`, `pwrite`, `zero`, and `flush` delegate to oVirt imageio client methods.

Research notes:
- Intended for upload/download workflows with qemu-img and nbdkit over a Unix socket.
- Parallelism depends on matching nbdkit thread count and configured imageio connections.
- `boolify` compares lowered string values and includes integer `0` in the false tuple, which will not match a string value but is harmless.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/python/examples/imageio.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/python/examples/ramdisk.py -->
# File Research: sources/virtualization/nbdkit/plugins/python/examples/ramdisk.py

Example Python plugin implementing a 1 MiB in-memory ramdisk.

Behavior:
- Global `bytearray` stores disk contents.
- `config` logs and ignores all parameters.
- `open` logs readonly/TLS state and returns a simple handle value.
- `get_size` returns disk length.
- `pread` copies from the bytearray into the nbdkit buffer.
- `pwrite` writes from the nbdkit buffer into the bytearray.
- `zero` honors `FLAG_MAY_TRIM` by replacing the range with zero bytes; otherwise sets `EOPNOTSUPP` and raises an exception.

Research notes:
- Demonstrates API version 2 mutable buffer callbacks.
- Global disk contents are shared by all connections.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/python/examples/ramdisk.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/python/examples/url.py -->
# File Research: sources/virtualization/nbdkit/plugins/python/examples/url.py

Example Python plugin serving an HTTP/HTTPS URL using range requests.

Configuration:
- `url=<URL>` is required.
- Unknown keys raise runtime errors.

Behavior:
- Returns parallel thread model.
- `open` returns a dummy handle.
- `get_size` issues a HEAD request, checks `accept-ranges`, reads `content-length`, and returns it.
- `pread` issues a ranged request for the requested byte interval, reads the response body, validates exact length, and copies it into the nbdkit buffer.

Research notes:
- This is read-only by omission; no write callbacks are defined.
- Correctness depends on the remote server honoring byte ranges exactly.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/python/examples/url.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/python/helpers.c -->
# File Research: sources/virtualization/nbdkit/plugins/python/helpers.c

Small helper file for the Python plugin bridge.

Functions:
- `callback_defined(name, obj_rtn)` checks whether the loaded Python module has a callable attribute with the given name.
  - Clears `AttributeError` when the attribute is absent.
  - Logs and ignores non-callable attributes.
  - Optionally returns a new reference to the callable.
- `python_to_string(str)` converts Python Unicode or bytes objects to newly allocated C strings.

Research notes:
- The helper assumes global `script` and `module` are initialized by the main Python plugin code.
- `python_to_string` uses `strdup` and the caller must free the result.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/python/helpers.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/python/modfunctions.c -->
# File Research: sources/virtualization/nbdkit/plugins/python/modfunctions.c

Defines the embedded Python `nbdkit` module exposed to Python plugins.

Module functions:
- Logging/debug: `debug`, `debug_hexdump`, `debug_hexdiff`.
- Connection/server control: `export_name`, `set_error`, `shutdown`, `disconnect`.
- Parsers: `parse_size`, `parse_probability`, `parse_delay`, `parse_bool`.
- Runtime/server helpers: `stdio_safe`, `is_tls`, `nanosleep`, `name`, `timestamp`.
- Peer identity: `peer_pid`, `peer_uid`, `peer_gid`, `peer_security_context`, `peer_tls_dn`, `peer_tls_issuer_dn`.
- Secrets: `read_password`.

Implementation details:
- Uses `PY_SSIZE_T_CLEAN` before Python headers.
- `last_error` is thread-local and records the last errno passed to `nbdkit.set_error`.
- Buffer debug functions accept Python buffer protocol objects.
- `parse_size` returns a Python integer from parsed byte size.
- Peer string helpers allocate through nbdkit APIs, convert to Python Unicode, and free C strings.
- `create_nbdkit_module` creates the module and adds constants for thread models, command flags, FUA modes, cache modes, and extent flags.

Research notes:
- `peer_name` is explicitly not implemented because CPython socket-address construction support is not exported.
- This file is API surface for Python plugin authors; actual nbdkit callback dispatch is in the Python plugin core outside this work item.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/python/modfunctions.c -->