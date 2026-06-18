# Group Research: group_684_libguestfs_sources_virtualization_libguestfs_lib_launch_libvirt_c_so_a01413aa3118

Scope: `Docs/research_subset_a.md`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/launch-libvirt.c -->
# File Research: sources/virtualization/libguestfs/lib/launch-libvirt.c

Libvirt backend implementation for launching the libguestfs appliance as a transient libvirt domain.

Important behavior:
- Registers the `libvirt` backend through `guestfs_int_init_libvirt_backend`.
- `launch_libvirt` selects `qemu:///session` for non-root and `qemu:///system` for root unless a backend URI is supplied.
- Reads libvirt capabilities and domain capabilities to choose qemu vs KVM, default emulator path, and firmware autoselection support.
- Builds or locates the appliance, creates qcow2 overlays for the appliance and read-only drives, and creates Unix sockets for guestfsd and console communication.
- Constructs complete libvirt domain XML with memory, CPU model, ACPI/timers, kernel/initrd/cmdline, optional UEFI loader/nvram, sVirt labels, virtio-scsi disks, console/channel sockets, optional passt networking, and qemu command-line extras.
- Handles file, block, network, and overlay disks; rejects qemu curl protocols for libvirt with a direct-backend suggestion.
- Uses libvirt secrets for authenticated network disks, including base64 decode for RBD secrets and protocol-specific secret types.
- Launches with `virDomainCreateXML(..., VIR_DOMAIN_START_AUTODESTROY)`, accepts console/daemon connections, waits for `GUESTFS_LAUNCH_FLAG`, then marks the appliance ready through protocol handling.
- `shutdown_libvirt` destroys and frees the domain/connection, unlinks sockets, frees labels, secrets, UEFI state, and capability-derived strings.
- `destroy_domain` retries indefinitely on libvirt `EBUSY`, ignores missing-domain errors, and can request graceful destruction.

Filesystem relevance:
- This is the main libvirt path for attaching guest disks safely to the appliance, including copy-on-write overlays for read-only access, discard settings, block sizes, disk labels, and network-backed storage.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/launch-libvirt.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/launch.c -->
# File Research: sources/virtualization/libguestfs/lib/launch.c

Generic launch orchestration and backend registry.

Important behavior:
- `guestfs_impl_launch` validates CONFIG state, checks backend max disks when available, creates tmpdir lazily, logs launch diagnostics, then delegates to `g->backend_ops->launch`.
- Launch progress is approximate and emitted after five seconds through `guestfs_int_launch_send_progress`.
- Provides state queries: config, launching, ready, busy compatibility, and raw state.
- `guestfs_impl_config` appends extra hypervisor parameters while rejecting parameters that would conflict with libguestfs-managed kernel, display, serial, and graphics options.
- Backend registration uses a global linked list populated by backend constructor functions.
- `guestfs_int_set_backend` resolves backend names and `backend:arg` strings, maps legacy `appliance` to `direct`, installs backend ops, and allocates backend-private data.
- `guestfs_int_passt_runnable` probes `passt --help` and accepts exit status 0 or 1.
- `guestfs_int_force_load_backends` keeps static linking from dropping backend constructors.

Filesystem relevance:
- Controls when appliance-backed filesystem access can start and enforces backend disk-count limits before guest disks are exposed.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/launch.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/libguestfs.pc.in -->
# File Research: sources/virtualization/libguestfs/lib/libguestfs.pc.in

Installed pkg-config template for libguestfs.

Important behavior:
- Defines configured `prefix`, `exec_prefix`, `libdir`, and `includedir`.
- Exposes package name, version, and description.
- Leaves `Requires` and `Cflags` empty.
- Provides `Libs: -lguestfs`.

Filesystem relevance:
- Build integration metadata for clients linking against libguestfs filesystem/image access APIs.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/libguestfs.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/libvirt-auth.c -->
# File Research: sources/virtualization/libguestfs/lib/libvirt-auth.c

Libvirt authentication bridge for libguestfs events.

Important behavior:
- Maps libvirt credential constants to API strings such as `username`, `authname`, `passphrase`, and prompt variants.
- `guestfs_impl_set_libvirt_supported_credentials` validates and atomically installs supported credential types.
- `guestfs_int_open_libvirt_connection` opens `virConnectOpenAuth` with either custom event-driven auth or a wrapper around libvirt default auth.
- Custom auth stores requested credentials on the handle and fires `GUESTFS_EVENT_LIBVIRT_AUTH`.
- Event-only getters expose requested credential names, prompt, challenge, and default result.
- `guestfs_impl_set_libvirt_requested_credential` stores a NUL-terminated result buffer for libvirt and records the exact byte length.
- Non-libvirt builds return consistent “compiled without libvirt” API errors.

Filesystem relevance:
- Enables libguestfs to access domains and storage pools whose disk metadata or secrets require libvirt authentication.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/libvirt-auth.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/libvirt-domain.c -->
# File Research: sources/virtualization/libguestfs/lib/libvirt-domain.c

Implements adding disks from an existing libvirt domain.

Important behavior:
- `guestfs_impl_add_domain` opens libvirt, locates the domain by UUID optionally and then by name, and forwards selected options to `guestfs_add_libvirt_dom_argv`.
- Live access is removed and explicitly rejected.
- `guestfs_impl_add_libvirt_dom` refuses writable access to running VMs, preventing disk corruption.
- Reads libvirt XML with `virDomainGetXMLDesc` and parses it with libxml2 using `XML_PARSE_NONET`.
- Extracts SELinux `seclabel`/`imagelabel` and passes them to backend settings before disks are added.
- Checkpoints drive state so either all domain disks are added or the previous drive list is restored.
- Handles disk XML types `file`, `block`, `network`, and `volume`.
- Network disk parsing supports source protocol/name, hosts, optional auth username, libvirt secrets by UUID or usage, and base64 encoding for Ceph secrets.
- Volume disks resolve storage pool and volume names to file paths, supporting only file-based libvirt volumes.
- Honors `readonlydisk` policy: `error`, `read`, `write`, or `ignore`.
- Extracts driver format, readonly flag, and logical block size.

Filesystem relevance:
- Converts libvirt domain storage definitions into libguestfs drives, preserving read-only safety, block size, network storage credentials, and SELinux context handling.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/libvirt-domain.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/libvirt-is-version.c -->
# File Research: sources/virtualization/libguestfs/lib/libvirt-is-version.c

Small command-line helper that checks the runtime libvirt version.

Important behavior:
- Accepts `MAJOR [MINOR [PATCH]]`.
- Initializes libvirt and calls `virGetVersion`.
- Converts the target version to libvirt’s numeric encoding: `major * 1000000 + minor * 1000 + release`.
- Exits success if installed libvirt is greater than or equal to the requested version.
- Uses strict integer parsing for arguments.

Filesystem relevance:
- Build/test helper for enabling libvirt-dependent filesystem appliance launch features conditionally.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/libvirt-is-version.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/local/libguestfs.pc.in -->
# File Research: sources/virtualization/libguestfs/lib/local/libguestfs.pc.in

Out-of-tree build pkg-config template for an uninstalled libguestfs tree.

Important behavior:
- Documents that it is a dummy pkg-config file for packages configured against the build tree.
- Points `prefix` and `exec_prefix` at `@abs_top_builddir@`.
- Sets `libdir` to the in-tree `lib/.libs` directory.
- Sets `includedir` to the source tree `include`.
- Emits `Cflags: -I${includedir}` and `Libs: -L${libdir} -lguestfs`.

Filesystem relevance:
- Lets companion tools build against in-tree libguestfs filesystem APIs before installation.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/local/libguestfs.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/lpj.c -->
# File Research: sources/virtualization/libguestfs/lib/lpj.c

Calculates host kernel `loops_per_jiffy` for TCG appliances.

Important behavior:
- `guestfs_int_get_lpj` computes once under a process-wide mutex and caches the result.
- Attempts to find `lpj=NNN` first from `dmesg`, then from readable boot log files `/var/log/dmesg` and `/var/log/boot.msg`.
- Uses grep through libguestfs command helpers and reads the whole command output via callback.
- Failures are intentionally non-fatal; callers ignore non-positive results.
- Parses the value after `lpj=` and logs debug details on invalid output or command status.

Filesystem relevance:
- Optimizes appliance boot under emulation, reducing launch overhead before filesystem inspection.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/lpj.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/match.c -->
# File Research: sources/virtualization/libguestfs/lib/match.c

PCRE2 wrapper helpers for internal regular-expression matching.

Important behavior:
- Provides boolean matching and capture-returning helpers for one, two, three, four, and six captures.
- Uses `pcre2_match_data_create_from_pattern` with cleanup attributes.
- Treats no-match as normal false/NULL.
- Unexpected PCRE2 errors are logged via debug and treated as no match.
- Captures are copied with `safe_strndup`; callers own returned strings.

Filesystem relevance:
- Shared parsing utility used by version parsing and other libguestfs code that interprets storage/device strings.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/match.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/mountable.c -->
# File Research: sources/virtualization/libguestfs/lib/mountable.c

Public helpers for decomposing mountable identifiers.

Important behavior:
- `guestfs_impl_mountable_device` parses a mountable string and returns its device component.
- `guestfs_impl_mountable_subvolume` returns the btrfs subvolume component.
- If the parsed mountable has no subvolume, it reports `EINVAL` with “not a btrfs subvolume identifier”.
- Uses generated internal mountable parsing and cleanup helpers.

Filesystem relevance:
- Separates physical device and btrfs subvolume identity for mount operations and callers that need path components.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/mountable.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/private-data.c -->
# File Research: sources/virtualization/libguestfs/lib/private-data.c

C API private data area attached to a `guestfs_h`.

Important behavior:
- Lazily allocates a gnulib hash table of key to opaque data pointer.
- `guestfs_set_private` replaces existing entries by key and frees only the key wrapper, not caller-owned data.
- `guestfs_get_private` returns the stored opaque pointer or NULL.
- `guestfs_first_private` and `guestfs_next_private` iterate entries, skipping entries with NULL data pointers.
- All access is protected by `g->lock`.
- Hashing uses `hash_pjw`; comparison is string equality.

Filesystem relevance:
- Lets C callers associate filesystem workflow state with a libguestfs handle without changing library internals.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/private-data.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/proto.c -->
# File Research: sources/virtualization/libguestfs/lib/proto.c

Client-side RPC protocol and file transfer engine.

Important behavior:
- Defines the call patterns for simple RPC, FileIn, FileOut, and mixed transfer APIs.
- `guestfs_int_send` serializes an XDR message header and optional args, prefixes the message length, checks for stale cancellation/progress, and writes through the current connection.
- `guestfs_int_recv_from_daemon` reads length/flag words, handles launch, cancel, progress, max message size, EOF, and log/progress transparency.
- Receiving `GUESTFS_LAUNCH_FLAG` in LAUNCHING state transitions the handle to READY and emits `GUESTFS_EVENT_LAUNCH_DONE`.
- `child_cleanup` shuts down the backend, frees connection and drives, resets state to CONFIG, and emits subprocess quit.
- File upload uses chunked XDR encoding, handles user cancellation and daemon cancellation, and sends completion or cancel chunks.
- File download opens/creates the target, receives chunks, writes fully, and sends cancellation to the daemon if local write/user cancellation occurs.
- Progress callbacks are represented as four uint64 values and emitted through event callbacks.
- Appliance console log messages are forwarded as appliance events and also inspected for launch progress sentinels.

Filesystem relevance:
- Carries all filesystem RPCs and file upload/download payloads between host library and appliance daemon.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/proto.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/qemu.c -->
# File Research: sources/virtualization/libguestfs/lib/qemu.c

QEMU feature/version helpers and drive-source formatting.

Important behavior:
- `generic_qmp_test` runs qemu with QMP on stdio, sends capabilities, a query command, and quit, then captures the query response.
- `guestfs_int_platform_has_kvm` uses QMP `query-kvm` JSON to determine whether KVM is enabled.
- JSON parsing is strict and UTF-8 validated.
- `guestfs_int_qemu_escape_param` doubles commas for qemu parameter escaping.
- `guestfs_int_drive_source_qemu_param` formats file, ftp/ftps/http/https, iscsi, nbd, rbd, and ssh sources for qemu/qemu-img.
- File paths are resolved with `realpath` so overlays reference absolute backing paths.
- RBD formatting builds escaped monitor host lists and includes auth/key options when present.
- `guestfs_int_discard_possible` validates discard support by overlay state, known source format, and protocol.

Filesystem relevance:
- Converts libguestfs drive sources into qemu-compatible backing strings and validates discard semantics for block/filesystem image operations.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/qemu.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/readdir.c -->
# File Research: sources/virtualization/libguestfs/lib/readdir.c

Implements `guestfs_readdir` by decoding daemon-produced XDR dirents.

Important behavior:
- Creates a temporary file path, calls `guestfs_internal_readdir(dir, tmpfn)`, and opens the result locally.
- Determines file size, then decodes `guestfs_int_dirent` records until XDR position reaches EOF.
- Grows the result array by doubling and checks for integer overflow.
- Transfers decoded name ownership into public `guestfs_dirent` entries.
- Frees partial results on error and unlinks the temporary file in all cases.

Filesystem relevance:
- Bridges appliance directory enumeration into host-side public dirent structures.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/readdir.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/rescue.c -->
# File Research: sources/virtualization/libguestfs/lib/rescue.c

Support helper for `virt-rescue`.

Important behavior:
- `guestfs_impl_internal_get_console_socket` requires a launched handle with an active connection.
- Verifies the connection class supports `get_console_sock`.
- Returns the connection’s console socket descriptor or a not-supported error.

Filesystem relevance:
- Exposes the appliance console for rescue workflows where users interact with the mounted/available guest environment.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/rescue.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/stringsbuf.c -->
# File Research: sources/virtualization/libguestfs/lib/stringsbuf.c

Expandable NULL-terminated string vector utility.

Important behavior:
- `guestfs_int_add_string_nodup` appends an owned string pointer and grows capacity in chunks of 64.
- `guestfs_int_add_string` appends a duplicated string.
- `guestfs_int_add_sprintf` formats a string with `vasprintf` and appends it.
- `guestfs_int_end_stringsbuf` appends the terminating NULL.
- `guestfs_int_free_stringsbuf` frees all stored strings and the vector.
- Separate from the daemon-side stringsbuf type.

Filesystem relevance:
- Shared utility for APIs that return string lists, including libvirt auth credential lists and storage-related result vectors.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/stringsbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/tmpdirs.c -->
# File Research: sources/virtualization/libguestfs/lib/tmpdirs.c

Temporary, cache, socket, and PID path management.

Important behavior:
- All configured tmp/runtime/cache paths are converted to absolute paths and validated as directories.
- `guestfs_get_tmpdir` prefers API-set tmpdir, then environment tmpdir, then `/tmp`.
- `guestfs_get_cachedir` prefers API-set cachedir, then environment tmpdir, then `/var/tmp`.
- `guestfs_get_sockdir` uses `/tmp` for root so libvirt/qemu can reach sockets; non-root prefers runtime dir, then `/tmp`.
- Lazily creates per-handle tmpdir and sockdir as `libguestfsXXXXXX`.
- Root-created temporary directories are chmodded `0755` for qemu access.
- Generates unique temporary file paths, socket paths bounded by `UNIX_PATH_MAX`, and PID paths under sockdir.
- Creates and security-checks the cached supermin appliance directory `.guestfs-$uid`, requiring ownership by current UID, directory type, and no group/other write bits.
- Removes tmpdir/sockdir recursively through `rm -rf`.

Filesystem relevance:
- Supplies secure host-side scratch space for overlays, appliance caches, RPC serialization files, sockets, and temporary filesystem metadata outputs.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/tmpdirs.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/tsk.c -->
# File Research: sources/virtualization/libguestfs/lib/tsk.c

Host-side wrappers for Sleuth Kit filesystem walk results.

Important behavior:
- `guestfs_impl_filesystem_walk` and `guestfs_impl_find_inode` ask the daemon to write XDR records into a temporary file.
- Parses that temp file into `guestfs_tsk_dirent_list`.
- Result arrays start at length 8 and double as needed.
- Each entry is zeroed before XDR decoding so xdr allocation behavior is correct.
- Final list length is set to the decoded entry count.
- Parse errors free partial result lists.

Filesystem relevance:
- Converts inode/filesystem walk data from the appliance into host-side structures for forensic-style filesystem traversal.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/tsk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/umask.c -->
# File Research: sources/virtualization/libguestfs/lib/umask.c

Thread-safe current umask retrieval.

Important behavior:
- `guestfs_int_getumask` first tries `/proc/self/status` and falls back to a fork-based method.
- `/proc` parser looks for `Umask: %o`; missing `/proc` or missing field triggers fallback, while other open errors are fatal.
- Fallback creates a CLOEXEC pipe, forks, and has the child call `umask(0)` and write the previous mask back.
- Child uses only async-safe operations after fork.
- Parent reads the mask and waits using libguestfs wait helpers.
- Command-style errors are reported if the child exits unsuccessfully.

Filesystem relevance:
- Used during launch diagnostics and helps preserve/understand host file creation permissions for temporary files and overlays.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/umask.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/unit-tests.c -->
# File Research: sources/virtualization/libguestfs/lib/unit-tests.c

Internal unit tests for small libguestfs utility functions.

Important behavior:
- Tests string split, concat, join, GUID validation, drive name/index conversion, umask retrieval, command helper basics, qemu parameter escaping, timeval difference, regex match helpers, stringsbuf behavior, and string validation macros.
- Creates libguestfs handles but does not launch appliances.
- `test_command` covers argv-style and shell-style command helper use with touch/rm.
- `test_valid` mirrors validation macros from drive parsing for formats, disk labels, and hostnames.
- Uses `assert` throughout and exits success if all tests pass.

Filesystem relevance:
- Protects utility functions that underpin drive naming, parsing, validation, temporary command execution, and launch diagnostics.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/unit-tests.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/version.c -->
# File Research: sources/virtualization/libguestfs/lib/version.c

Version parsing and comparison helpers.

Important behavior:
- Stores explicit version values in `struct version`.
- Parses `X.Y` from arbitrary strings with a default regex or caller-provided regex.
- Can also parse a whole integer as `X.0.0` when allowed.
- Successful parses set major/minor/micro; missing regex match leaves the version unchanged and returns 0.
- `guestfs_int_version_ge` and `guestfs_int_version_cmp_ge` implement lexicographic greater-or-equal comparison.
- Integer parsing uses `xstrtol` and rejects trailing characters.

Filesystem relevance:
- Shared feature-gating utility for external tools and backends whose behavior depends on parsed version numbers.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/version.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/wait.c -->
# File Research: sources/virtualization/libguestfs/lib/wait.c

Signal-safe wait wrappers.

Important behavior:
- `guestfs_int_waitpid` retries `waitpid` on `EINTR` and reports other errors with context.
- `guestfs_int_waitpid_noerror` waits while ignoring errors except retrying interruption.
- `guestfs_int_wait4` provides the same retry behavior for `wait4` with rusage collection.
- Comments explain the interaction with non-restartable SIGCHLD handlers installed by embedding programs.

Filesystem relevance:
- Supports robust management of subprocesses used by launch, command helpers, temporary probes, and host-side tooling.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/wait.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/whole-file.c -->
# File Research: sources/virtualization/libguestfs/lib/whole-file.c

Trusted local whole-file reader.

Important behavior:
- Opens a local file read-only with CLOEXEC.
- Uses `fstat` to size the file, allocates `size + 1`, and reads until the expected byte count is reached.
- Treats premature EOF as an error.
- Closes the descriptor and reports close failures.
- NUL-terminates the returned buffer for caller convenience without counting the NUL in `size_r`.
- Explicitly documents that this is only for regular, local, trusted files because untrusted files can cause denial of service.

Filesystem relevance:
- Utility for reading trusted host-side metadata/configuration files into memory during libguestfs operations.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/whole-file.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libguestfs/lib/yara.c -->
# File Research: sources/virtualization/libguestfs/lib/yara.c

Host-side wrapper for YARA scan results.

Important behavior:
- `guestfs_impl_yara_scan` asks the daemon to scan a guest path and write serialized detections to a temp file.
- Parses the temp file into `guestfs_yara_detection_list`.
- Result arrays start at length 8 and double when full.
- Each detection entry is zeroed before XDR decode.
- XDR decode failures are reported and partial results are freed.
- Final list length is the number of decoded detections.

Filesystem relevance:
- Converts appliance-side malware/signature scan results over guest filesystems into public host-side result structures.
<!-- END FILE RESEARCH: sources/virtualization/libguestfs/lib/yara.c -->