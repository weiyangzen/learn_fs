# Group Research: group_683_libguestfs_sources_virtualization_libguestfs_lib_errors_c_sources_vi_0c2bed5d39a4

Scope checked against `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/errors.c -->
# File Research: sources/virtualization/libguestfs/lib/errors.c

Purpose: Implements libguestfs error storage, error callbacks, warning/debug/trace message emission, buffer trace formatting, and standardized launch/external-command failure messages.

Key behavior:
- Uses per-handle pthread TLS (`g->error_data`) so each thread has its own last error, errno, and error handler stack while sharing one `guestfs_h`.
- Maintains `g->error_data_list` so all per-thread error records can be freed when the handle closes.
- `guestfs_int_error_errno` and `guestfs_int_perrorf` format messages, update last error first, then invoke the current callback.
- Warning/debug/trace messages are routed through the event callback system as `GUESTFS_EVENT_WARNING`, `GUESTFS_EVENT_LIBRARY`, and `GUESTFS_EVENT_TRACE`.
- `guestfs_int_print_BufferIn/Out` truncates trace output for large binary buffers to 256 bytes.
- Standard helpers produce user-facing diagnostics for launch failure, unexpected appliance close, launch timeout, and failed external commands.

Dependencies and state:
- Depends on `guestfs-internal.h` macros (`error`, `perrorf`, locks), `events.c` callback dispatch, pthread TLS, and safe allocation helpers.
- Mutates `g->error_data_list`, per-thread `struct error_data`, `g->abort_cb`.

Risks:
- `set_last_error` uses `strdup` directly; allocation failure leaves `last_error` NULL without invoking the abort callback.
- Callers must follow the file’s rule to set exactly one error per error path, otherwise earlier errors are overwritten.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/errors.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/events.c -->
# File Research: sources/virtualization/libguestfs/lib/events.c

Purpose: Implements the modern event callback registry plus compatibility wrappers for older single-callback APIs.

Key behavior:
- `guestfs_set_event_callback` appends callbacks to `g->events`, returning an integer event handle; flags must be zero and callback count is capped at 1000.
- `guestfs_delete_event_callback` disables callbacks by zeroing their bitmask and shrinks the tail entry when possible.
- Internal dispatchers call matching callbacks for void, message, and uint64-array payloads.
- If no message callback is registered, appliance/library/warning/trace messages are printed to stderr with escaping rules for binary and control characters.
- Old APIs such as `guestfs_set_log_message_callback`, `guestfs_set_close_callback`, and `guestfs_set_progress_callback` are emulated with wrapper callbacks stored in `opaque2`.

Dependencies and state:
- Uses `g->events` and `g->nr_events` from `guestfs_h`.
- Uses `c_isprint`, `STREQ/STRNEQ`, and handle locking on public registration/removal APIs.

Risks:
- Registry is a linear array with a hard limit; deleted non-tail entries remain as inert slots.
- Old-style callback replacement uses wrapper function identity as the sentinel, so one callback per old event type is preserved by design.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/events.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/file.c -->
# File Research: sources/virtualization/libguestfs/lib/file.c

Purpose: Provides client-side implementations and compatibility wrappers for file read/write/list/stat operations that need local temp files, list chunking, sorting, or old ABI translation.

Key behavior:
- `guestfs_impl_read_file` downloads a guest file to a temp file, reads it fully into memory, NUL-terminates it, and reports size only after success.
- `guestfs_impl_read_lines` splits a downloaded file into LF/CRLF-trimmed string lists.
- `guestfs_impl_find` and `guestfs_impl_ls` use daemon `find0`/`ls0` output, parse NUL-delimited entries, duplicate them, and sort results.
- `write_or_append` uses efficient internal write calls for content up to 2 MiB; larger writes go through temp-file upload. Append uses filesize plus upload offset and is explicitly not atomic.
- `lstatnslist`, `lxattrlist`, and `readlinklist` split large name vectors into batches of 1000 to avoid protocol limits.
- `stat`, `lstat`, and `lstatlist` translate nanosecond stat structures into older `guestfs_stat` ABI structures.

Dependencies and state:
- Depends on generated actions (`download`, `upload`, `find0`, `ls0`, `internal_*`), temp-path helpers, `full_read/full_write`, cleanup macros, and struct cleanup helpers.
- No persistent handle state beyond temp files and errors.

Risks:
- Whole-file reads allocate based on remote/local file size and can be expensive for large files.
- Large append is non-atomic and can race with other writers.
- Empty NUL-delimited outputs require careful parsing; this code has explicit handling but relies on daemon output conventions.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/file.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/fuse.c -->
# File Research: sources/virtualization/libguestfs/lib/fuse.c

Purpose: Implements `mount-local`, `mount-local-run`, and `umount-local`, exposing the mounted guest filesystem through libfuse when libguestfs is built with FUSE support.

Key behavior:
- Defines FUSE operations for lookup, access, readlink, directory read, node creation/removal, rename/link, chmod/chown, truncate, utimens, open, read, write, statfs, fsync, xattrs, release, and flush.
- Read and write operations cap single protocol transfers at 2 MiB.
- Read-only mount mode rejects write-capable operations with `EROFS`.
- `readdir` prepopulates three short-lived directory caches: lstat results, xattrs, and readlink targets.
- Cache entries are keyed by full path in gnulib hash tables and expire after `ml_dir_cache_timeout`.
- `guestfs_impl_mount_local` builds FUSE args, mounts the local mountpoint, creates the FUSE handle, stores `g->localmountpoint`, and initializes caches.
- `guestfs_impl_mount_local_run` verifies `/` is mounted, enters `fuse_loop`, then destroys FUSE state and clears the mountpoint.
- `guestfs_impl_umount_local` shells out to `guestunmount` with optional retry.
- If `HAVE_FUSE` is false, all public entry points return `ENOTSUP`.

Dependencies and state:
- Uses libfuse 2.6 APIs, generated guestfs filesystem actions, `guestfs_last_errno`, `guestfs_int_new_command`, `guestunmount`, and gnulib hash helpers.
- Mutates FUSE-specific fields in `guestfs_h`: `localmountpoint`, `fuse`, `ml_dir_cache_timeout`, `ml_read_only`, `ml_debug_calls`, and cache hash tables.
- A global `mount_local_lock` protects `g->localmountpoint`.

Risks:
- FUSE callbacks rely on the same `guestfs_h`; concurrency safety depends on public action locking and FUSE threading behavior.
- `readdir` ignores offsets, matching common examples but potentially weak for very large directories.
- xattr flag semantics are not fully supported because the underlying guestfs API ignores setxattr flags.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/fuse.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/guestfs-internal-all.h -->
# File Research: sources/virtualization/libguestfs/lib/guestfs-internal-all.h

Purpose: Shared internal header for all libguestfs C components, including daemon, library, bindings, and tools.

Key contents:
- Defines compiler compatibility macros, string comparison/prefix/suffix helpers, `ADD_ARG`, `MAX/MIN`, socket compatibility constants, and Apple XDR compatibility.
- Provides `is_zero`, an inline buffer-zero test optimized by checking the first 16 bytes then using `memcmp`.
- Defines `COMPILE_REGEXP`, a constructor/destructor macro for compiling PCRE2 regexes at library load time.
- Defines shared `mountable_type_t` for parsed mountables.
- Declares gnulib replacement prototypes for `accept4` and `pipe2` when needed.
- Provides OCaml compatibility alias for older OCaml runtime naming.

Dependencies and state:
- Uses libc string APIs, PCRE2, and low-level `write` in regexp compile failure handling.
- No runtime state except static regex objects created by `COMPILE_REGEXP` users.

Risks:
- Convenience macros evaluate some arguments multiple times, so callers must avoid side-effect expressions.
- `ADD_ARG` aborts on overflow rather than returning an error.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/guestfs-internal-all.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/guestfs-internal.h -->
# File Research: sources/virtualization/libguestfs/lib/guestfs-internal.h

Purpose: Primary private header for the libguestfs library implementation under `lib/`.

Key contents:
- Defines scoped mutex locking via cleanup attributes.
- Defines defaults and platform constants for appliance memory, launch timeout, machine type, virtio device naming, and appliance networking addresses.
- Defines core enums and structs: handle state, event registry entries, drive source/server/drive records, backend ops, connection ops, feature cache, version, and the full `struct guestfs_h`.
- `guestfs_h` centralizes configuration, runtime paths, error TLS, event callbacks, private data, protocol connection, FUSE state, libvirt auth state, feature cache, and `qemu-img -U` probe cache.
- Declares internal APIs across allocation, errors, actions support, regex matching, string buffers, protocol, sockets, events, tempdirs, drives, appliance building, launch, command execution, qemu helpers, GUID validation, wait helpers, version parsing, and UEFI firmware tables.
- Defines common macros such as `error`, `perrorf`, `warning`, `debug`, `NOT_SUPPORTED`, `ITER_DRIVES`, and `close_file_descriptors`.

Dependencies and state:
- Depends on pthreads, XDR, PCRE2, optional libvirt, and `guestfs-utils.h`.
- This header defines the shared state contract used by nearly every file in this group.

Risks:
- `guestfs_h` is broad and tightly coupled; changes to fields can affect launch, FUSE, callbacks, drives, protocol, and bindings.
- Recursive locking simplifies nested public API calls but can hide lock-order issues if new locks are added.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/guestfs-internal.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/guid.c -->
# File Research: sources/virtualization/libguestfs/lib/guid.c

Purpose: Validates GUID string shape for internal callers.

Key behavior:
- Accepts either `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` length 36 or the same form wrapped in braces length 38.
- Requires dashes at positions 8, 13, 18, and 23.
- Requires all non-dash characters to be alphanumeric via `c_isalnum`.

Dependencies and state:
- Uses `strlen` and gnulib character classification.
- Stateless.

Risks:
- Allows any alphanumeric character, not strictly hexadecimal digits, so this validates GUID-like formatting rather than canonical GUID contents.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/guid.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/handle.c -->
# File Research: sources/virtualization/libguestfs/lib/handle.c

Purpose: Creates, configures, shuts down, and destroys `guestfs_h` handles, and implements many generated getter/setter APIs.

Key behavior:
- Constructor initializes libvirt and libxml2 for multithreaded use.
- `guestfs_create_flags` allocates a handle, initializes recursive locks, TLS key, defaults, backend, program name, environment-derived settings, and optional close-on-exit registration.
- Environment parsing supports debug/trace, tmp/cache/runtime dirs, appliance path, hypervisor, append args, memsize, backend, and backend settings.
- `guestfs_close` removes the handle from the global list, emits trace/close events, shuts down if needed, frees temp dirs, FUSE state, drives, backend data, private data, strings, error TLS records, and the handle itself.
- `shutdown_backend` autosyncs when ready, invokes backend shutdown, frees connection/drives/features, and resets state to `CONFIG`.
- Implements setters/getters for verbose, autosync, path, qemu/hv, append, memsize, SELinux, version, trace, direct mode, recovery process, network, program, identifier, backend, attach method compatibility, backend settings, process group, and SMP.
- Backend settings support `name`, `name=value`, clear, get, set, and boolean lookup with suppressed “not found” errors.

Dependencies and state:
- Uses global handle list protected by `handles_lock`, per-handle lock from generated wrappers, libxml2, optional libvirt, hash private data, tempdir/drives/FUSE cleanup, backend ops, and error/event subsystems.
- Mutates most configuration fields in `guestfs_h`.

Risks:
- Double close is detected only by `g->state == NO_HANDLE`; using a freed handle remains undefined outside this guard.
- `guestfs_impl_get_hv` cannot report a backend default before backend data exists after launch.
- Environment parsing has many legacy aliases, so behavior changes can affect compatibility.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/handle.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/info.c -->
# File Research: sources/virtualization/libguestfs/lib/info.c

Purpose: Implements disk metadata APIs by running `qemu-img info --output json` and parsing its JSON output.

Key behavior:
- `guestfs_impl_disk_format` returns the JSON `format` field.
- `guestfs_impl_disk_virtual_size` returns `virtual-size`.
- `guestfs_impl_disk_has_backing_file` detects presence of `backing-filename`.
- `get_json_output` constructs the qemu-img command, conditionally adds `-U`, forces JSON output, prefixes relative filenames with `./`, captures stdout as one buffer, and checks exit status.
- `parse_json` uses json-c strict UTF-8 validation and reports parse errors through the handle.
- `qemu_img_supports_U_option` probes `qemu-img --help` once and memoizes the result in `g->qemu_img_supports_U_option`.
- Child rlimits bound address space to 1 GiB and CPU to 10 seconds when supported.

Dependencies and state:
- Depends on json-c, command execution helpers, wait status handling, external `qemu-img`, and `guestfs_int_external_command_failed`.
- Mutates only `g->qemu_img_supports_U_option`.

Risks:
- Relies on `qemu-img --help | grep` output for `-U` feature detection.
- JSON schema assumptions are narrow; missing expected keys produce errors.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/info.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/inspect-apps.c -->
# File Research: sources/virtualization/libguestfs/lib/inspect-apps.c

Purpose: Implements guest application/package inventory for Linux/Hurd package managers and Windows registry uninstall keys.

Key behavior:
- Deprecated `inspect_list_applications` wraps `inspect_list_applications2` and translates the newer struct to the older ABI.
- Dispatches by inspected OS type and package format: RPM via daemon internal action, Debian dpkg status parsing, pacman local database parsing, Alpine APK installed database parsing, and Windows registry parsing.
- dpkg and APK files are downloaded with 50 MB safety limits; pacman desc files are downloaded with an 8 KiB limit.
- Debian parsing handles installed status, version epoch/release splitting, architecture, homepage, source package, summary, and multiline descriptions.
- Pacman parsing reads `%KEY%` blocks and splits `[epoch:]ver-rel`.
- APK parsing reads one-letter fields and strips leading `r` from release revisions.
- Windows parsing opens the SOFTWARE hive with hivex, reads native and WOW64 uninstall paths, collects display/version/location/publisher/URL/comments, and adds a Windows Defender heuristic.
- Antivirus classification uses compiled PCRE2 regexes across name, display name, and publisher.
- Results are normalized through `add_application` and sorted by application name.

Dependencies and state:
- Depends on inspection getters, generated filesystem/download/hivex actions, `guestfs_int_download_to_tmp`, version parsing, PCRE2 match helpers, and struct cleanup helpers.
- No persistent handle state except hivex open/close side effects in the appliance.

Risks:
- Package database parsers are permissive and skip malformed entries.
- Windows inventory is heuristic and limited to uninstall registry keys plus Defender.
- Some fields are explicitly unimplemented or reserved, such as translated path and some source/summary coverage.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/inspect-apps.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/inspect-icon.c -->
# File Research: sources/virtualization/libguestfs/lib/inspect-icon.c

Purpose: Implements OS icon extraction for inspection, returning a PNG buffer or an empty buffer when no icon is found.

Key behavior:
- `guestfs_impl_inspect_get_icon` first optionally checks `/etc/favicon.png`, then falls back to distro/type-specific icon locations or Windows extraction.
- PNG candidates are validated with `is_file`, `realpath`, `file` output prefix, geometry bounds from 16x16 to 1024x1024, and max-size limits before download.
- Supports Fedora, RHEL-family, Debian, Ubuntu, Mageia, openSUSE/SLES, CirrOS, Void, ALT Linux, Gentoo, OpenMandriva, and selected Windows versions when build-time tools exist.
- CirrOS text logo is rendered through `pbmtext | pnmtopng` when tools are configured.
- Windows extraction downloads `explorer.exe` or known PNG sources and uses `wrestool`, `bmptopnm`, `pamcut`, and `pnmtopng` for XP/7/8 cases.
- `guestfs_int_download_to_tmp` is defined here as a shared inspection helper: it size-checks a guest file, creates a temp file, downloads via `/dev/fd/<fd>`, and returns the temp path.

Dependencies and state:
- Depends on inspection getters, generated file/download actions, external image tools based on configure macros, command helpers, and whole-file reads.
- Uses temporary files tied to the handle lifecycle.

Risks:
- Icon support is intentionally incomplete and depends on host tools compiled into macros.
- Windows support is version-specific and fragile around resource IDs and executable layout.
- Uses `guestfs_file` output text for PNG detection and geometry parsing.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/inspect-icon.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/inspect-osinfo.c -->
# File Research: sources/virtualization/libguestfs/lib/inspect-osinfo.c

Purpose: Maps libguestfs inspection results to libosinfo-style OS IDs.

Key behavior:
- Reads inspected type, distro, major version, minor version, and for Windows sometimes product name, product variant, and build ID.
- Produces distro-specific IDs for CentOS, Circle, Rocky, Debian, Fedora, Mageia, SLES/SLE, Ubuntu, Arch, Gentoo, Void, ALT Linux, BSD variants, MS-DOS, and Windows.
- Windows 5.x/6.x maps to XP, 2003, Vista, 2008, 7, 2012, 8, 8.1, etc.
- Windows 10.0 server names distinguish 2016/2019/2022/2025 from product name.
- Windows client 10.0 uses build ID >= 22000 as Windows 11, otherwise Windows 10.
- Returns `"unknown"` when no ID can be inferred.

Dependencies and state:
- Depends on inspection getter APIs and `guestfs_int_parse_unsigned_int`.
- Stateless.

Risks:
- Mapping is heuristic and must track distro/libosinfo naming conventions.
- Windows Server detection relies on product name substrings.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/inspect-osinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/journal.c -->
# File Research: sources/virtualization/libguestfs/lib/journal.c

Purpose: Implements `journal_get` library-side to avoid protocol limits for large systemd journal fields.

Key behavior:
- Calls `guestfs_internal_journal_get` to download a private binary stream to a temp file.
- Reads the whole temp file locally, then parses repeated records of big-endian 64-bit length followed by `field=data` bytes.
- Builds a `guestfs_xattr_list`, storing the field name as `attrname` and binary value as `attrval`.
- Validates truncation, oversized length, and missing `=` separator with explicit errors.

Dependencies and state:
- Depends on temp path creation, full-read, endian conversion, generated internal journal action, and xattr list allocation/free helpers.
- Stateless beyond temp files.

Risks:
- Reads the whole exported journal record stream into memory.
- Protocol is private and explicitly may change; producer and parser must remain in sync.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/journal.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/launch-direct.c -->
# File Research: sources/virtualization/libguestfs/lib/launch-direct.c

Purpose: Implements the `direct` backend, launching qemu directly without libvirt and wiring it to the libguestfs appliance.

Key behavior:
- Backend private state stores qemu binary, qemu PID, recovery PID, and daemon socket path.
- Read-only drive overlays are created as qcow2 files using `guestfs_disk_create_argv`.
- Drive qemu arguments include file/source, snapshot/read-only behavior, cache mode, format, copy-on-read, discard, overlay handling, IDs, SCSI devices, serial labels, and block sizes.
- Picks a default qemu binary from `host_cpu`.
- Launch path verifies drives exist, builds/locates appliance, probes qemu/KVM, honors `force_tcg` and `force_kvm`, creates Unix daemon socket and optional console socketpair, then constructs qemu args before forking.
- Command line disables qemu defaults/user config, display, reboot, adds machine/CPU/memory/RTC/rng/virtio-scsi/drives/appliance/virtio-serial/console/channel/network/kernel/initrd/append args and custom hypervisor params.
- Networking uses `passt` when runnable, otherwise qemu user networking.
- Child process wires stdio/stderr to console socket unless direct mode is enabled, closes extra fds, optionally starts a process group, and execs qemu.
- Parent optionally forks a recovery process that kills qemu if the parent disappears.
- Launch waits for qemu to connect over virtio-serial, receives `GUESTFS_LAUNCH_FLAG`, checks handle state becomes `READY`, and adds a dummy appliance drive when needed.
- Cleanup kills qemu/recovery/passt as needed, closes sockets, frees qemuopts, clears connection, and resets state.
- Shutdown sends SIGTERM to qemu, kills recovery, waits, reports qemu failures, logs max RSS, and unlinks daemon socket.
- Registers backend ops for create overlay, default HV, launch, shutdown, get PID, and max disks.

Dependencies and state:
- Depends on qemuopts, command helpers, appliance builder, qemu/platform helpers, connection socket module, wait helpers, UEFI helpers, passt probing, launch progress, and backend registration.
- Mutates direct backend data, `g->conn`, `g->state`, `g->launch_t`, drive overlays/dummy appliance drive, and process state.

Risks:
- Process lifecycle is complex: multiple forks, recovery process polling, passt lifetime, socket ownership, and cleanup must stay aligned.
- qemu command construction is architecture- and version-sensitive.
- Force-KVM/TCG backend settings and KVM availability produce early launch failures.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/launch-direct.c -->