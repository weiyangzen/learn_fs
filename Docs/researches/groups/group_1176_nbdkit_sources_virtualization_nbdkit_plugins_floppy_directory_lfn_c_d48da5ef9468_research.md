# Group Research: group_1176_nbdkit_sources_virtualization_nbdkit_plugins_floppy_directory_lfn_c_d48da5ef9468

Scope: `Docs/research_subset_a.md`, source tree `sources/virtualization/nbdkit`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/floppy/directory-lfn.c -->
# File Research: sources/virtualization/nbdkit/plugins/floppy/directory-lfn.c

This file implements FAT directory table creation for the floppy plugin, with most of the complexity centered on VFAT long filename handling.

Key behavior:
- `create_directory` builds each directory's on-disk `dir_entry` vector, adding a root volume label or subdirectory `.`/`..` entries first.
- It converts every child directory and file name in a directory before emitting entries so 8.3 short-name collisions can be resolved across the whole directory.
- `add_directory_entry` emits the VFAT LFN entries in reverse sequence order, followed by the 8.3 entry with attributes, timestamps, size, and deferred cluster fields.
- `update_directory_first_cluster` later patches cluster numbers after `virtual-floppy.c` has assigned clusters to all directories/files.

Important implementation details:
- Long names are converted from UTF-8 to UTF-16LE with `iconv`, using `//TRANSLIT` under GNU libc.
- Short names are built from an ASCII allowlist, uppercased, and duplicate names are renamed using a `~<index>` suffix.
- FAT timestamps are derived from local `stat` times and packed into FAT date/time fields.
- LFN entries are detected by attribute `0x0f`; root volume labels and `.`/`..` are skipped when patching normal file/directory cluster references.

Dependencies:
- Uses structures and constants from `virtual-floppy.h`.
- Uses `dir_entries_append`, `floppy->dirs`, and `floppy->files` populated by `virtual-floppy.c`.

Risks and edge cases:
- The code assumes the current locale/input filenames are UTF-8.
- Short-name collision handling is O(n^2) and simple; comments acknowledge this.
- `pad_string` truncates labels/names without validation.
- The cluster patcher relies on the exact order in which directory entries were emitted.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/floppy/directory-lfn.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/floppy/floppy.c -->
# File Research: sources/virtualization/nbdkit/plugins/floppy/floppy.c

This is the nbdkit plugin entry point for serving a host directory as a read-only virtual FAT32 floppy-like disk image.

Key behavior:
- Parses `dir`, `label`, and optional `size` parameters.
- Initializes and frees a global `struct virtual_floppy`.
- In `.get_ready`, calls `create_virtual_floppy` to scan the directory and construct all virtual disk regions.
- Exposes `.get_size`, `.block_size`, `.can_multi_conn`, `.can_cache`, and `.pread`.

Read path:
- `floppy_pread` repeatedly finds the virtual region covering the current offset.
- `region_file` opens the corresponding host file, reads from the adjusted offset, and closes it.
- `region_data` copies from in-memory metadata buffers.
- `region_zero` fills with zeroes.

Integration:
- Delegates all FAT32 layout work to `virtual-floppy.c` and directory entry work to `directory-lfn.c`.
- Uses `regions.h` for sparse virtual disk layout.
- Advertises parallel thread model and multi-connection safety because the generated image is immutable after `.get_ready`.

Risks and edge cases:
- Host files are reopened on each file-region read segment, which is simple but can be costly.
- Files changing after `.get_ready` could invalidate stored size/metadata assumptions.
- Only a single `dir` is accepted; a TODO mentions future multi-directory merging.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/floppy/floppy.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/floppy/virtual-floppy.c -->
# File Research: sources/virtualization/nbdkit/plugins/floppy/virtual-floppy.c

This file constructs the full FAT32 disk image model used by the floppy plugin.

Key behavior:
- `create_virtual_floppy` scans the input directory tree, builds directory/file lists, creates directory tables, assigns clusters, creates MBR/boot/fsinfo/FAT metadata, and builds final virtual regions.
- `visit` recursively walks directories using `chdir` during `.get_ready`, ignoring non-directory and non-regular files.
- Directories are stored before files in the data region, and both are allocated contiguous cluster chains.
- Optional user-specified `size` reserves extra zero-filled data clusters if larger than content.

Disk layout:
- Sector 0 is MBR.
- Partition starts at sector 2048.
- FAT32 boot sector, FSInfo sector, reserved sectors, backup boot sector, two FAT copies, and data region follow.
- Cluster size is fixed from `SECTOR_SIZE` and `SECTORS_PER_CLUSTER`.

Important implementation details:
- FAT32 cluster numbers are limited to 28 bits.
- MBR partition type is `0x0c` FAT32 LBA.
- Boot sector uses OEM name `MSWIN4.1`, fixed volume ID `0x01020304`, two FATs, root cluster 2.
- Zero-size files occupy no region or FAT cluster.
- Region construction pads FATs and data objects to cluster alignment.

Dependencies:
- Uses `directory-lfn.c` via `create_directory`, `update_directory_first_cluster`, and `pad_string`.
- Uses common helpers: `regions`, `rounding`, `byte-swapping`, cleanup macros, and dynamic vectors.

Risks and edge cases:
- Uses `chdir` recursively, safe only because execution happens before daemonization/threading.
- Symlinks and special files are ignored.
- Host file mutation after image creation can lead to read errors or inconsistent exported data.
- Random/deterministic ordering depends on host `readdir` order.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/floppy/virtual-floppy.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/floppy/virtual-floppy.h -->
# File Research: sources/virtualization/nbdkit/plugins/floppy/virtual-floppy.h

This header defines the on-disk FAT32 structures and in-memory model for the floppy plugin.

Key definitions:
- Packed MBR/boot-sector, partition-entry, FSInfo, FAT directory-entry, and LFN-entry structs.
- `struct file` stores Unix name, host path, stat metadata, first cluster, and cluster count.
- `struct dir` stores parent index, name, stat metadata, first cluster, children indexes, file indexes, and on-disk directory table.
- `struct virtual_floppy` stores regions, metadata sectors, FAT buffer, file/dir vectors, data/FAT sizing fields, and sector offsets.

Constants:
- `SECTOR_SIZE` is 512.
- `SECTORS_PER_CLUSTER` is 32.
- `CLUSTER_SIZE` is 16 KiB.
- Directory attribute constants mirror FAT directory entry flags.

Integration:
- `floppy.c` owns the global instance and uses `init_virtual_floppy`, `create_virtual_floppy`, and `free_virtual_floppy`.
- `directory-lfn.c` consumes the directory/file vectors and on-disk structs to build directory tables.
- `virtual-floppy.c` fills layout metadata and regions.

Risks and constraints:
- Packed structs are asserted to exact sector/entry sizes at runtime.
- Comments warn cluster sizing is tied to disk layout and maximum supported size.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/floppy/virtual-floppy.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/full/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/full/Makefile.am

This Automake file builds and documents the `full` plugin.

Key behavior:
- Builds `nbdkit-full-plugin.la` from `full.c` and `nbdkit-plugin.h`.
- Adds include paths for source and build `include`.
- Links Windows import library when needed.
- Uses module/shared libtool flags and optional linker version script.
- If POD tooling is available, builds `nbdkit-full-plugin.1` from the POD source and inserts the magic-parameter documentation snippet.

Integration:
- The plugin is unconditional in this file, unlike plugins gated on external dependencies.
- Documentation generation follows the standard nbdkit plugin pattern.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/full/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/full/full.c -->
# File Research: sources/virtualization/nbdkit/plugins/full/full.c

This plugin simulates a block device that reads as zeroes but fails all space-consuming writes with `ENOSPC`.

Key behavior:
- Requires `size=<SIZE>` and stores it globally.
- `.pread` zero-fills every read.
- `.pwrite` and `.trim` fail with `errno = ENOSPC`.
- `.extents` reports the entire export as hole plus zero.
- `.can_cache` returns native cache because data is synthetic and already available.
- Multi-connection is safe.

Intentional behavior:
- `.zero` is omitted so nbdkit fast-zero handling returns `ENOTSUP` for fast zeroes, while normal zeroes fall back to `.pwrite` and report `ENOSPC`.
- `.flush` is omitted because successful writes never happen.

Integration:
- API version 2 plugin.
- Uses nbdkit parse helpers and extent API.

Risks:
- Simple global `size`; no per-connection state.
- Mainly useful as a behavior-testing or failure-simulation plugin.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/full/full.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/gcs/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/gcs/Makefile.am

This Automake file installs the Python Google Cloud Storage plugin script.

Key behavior:
- Distributes `gcs.py`, `nbdkit.py`, and the plugin POD.
- When Python is available, creates executable `nbdkit-gcs-plugin` by substituting `@sbindir@` in `gcs.py`.
- Installs the generated script as a plugin script.
- If POD tooling is available, builds `nbdkit-gcs-plugin.1`.

Integration:
- The generated shebang points at the built or installed nbdkit Python runner.
- `nbdkit.py` is distributed for unit-test stubbing, not as the real in-process module.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/gcs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/gcs/gcs.py -->
# File Research: sources/virtualization/nbdkit/plugins/gcs/gcs.py

This Python plugin exposes Google Cloud Storage objects as an NBD block device, supporting both single-object read-only mode and multi-object writable block mode.

Configuration and capabilities:
- `bucket` and `key` are required.
- `json-credentials` selects a service-account JSON file; otherwise Application Default Credentials are used.
- `size` and `object-size` must be supplied together for writable block mode.
- Single-object mode reads `key` directly and cannot write.
- Block mode maps block `N` to object `<key>/<N as 16-digit hex>`.
- Advertises parallel thread model, multi-connection, trim, zero, fast zero, native FUA, and flush.

Read/write behavior:
- `pread` reads directly from one object or splits across block objects.
- Missing objects read as zeroes.
- `pwrite` requires block mode and rewrites full objects as needed for unaligned writes.
- Whole-object writes upload exactly `cfg.obj_size` bytes.
- `zero` rewrites partial edge blocks and deletes fully covered blocks.
- `trim` deletes only fully covered block objects, rounding inward as NBD permits.

Concurrency:
- `MultiLock` serializes operations per object key while allowing parallel operations on different keys.
- Per-object locking protects read-modify-write sequences for unaligned writes.

Error handling:
- Top-level callbacks translate GCS `GatewayTimeout` and `DeadlineExceeded` to `ETIMEDOUT`.
- Missing objects are treated as sparse zero blocks via `NotFound`.

Embedded tests:
- `LocalTest` uses mocked GCS objects and compares behavior against a temporary reference file for read/write/zero/trim corner cases.
- `RemoteTest` can run against a real bucket when `TEST_BUCKET` and `TEST_JSON_CREDENTIALS` are set.

Risks and edge cases:
- `_put_object` asserts exact object-size uploads; partial logical writes must be expanded before upload.
- Single-object mode is effectively read-only despite `can_write` depending on `obj_size`.
- GCS consistency, latency, and object listing semantics are external dependencies.
- The global config object is mutated by tests and runtime setup.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/gcs/gcs.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/gcs/nbdkit.py -->
# File Research: sources/virtualization/nbdkit/plugins/gcs/nbdkit.py

This is a minimal Python stub for unit-testing `gcs.py` outside the nbdkit process.

Provided API:
- `FLAG_MAY_TRIM = 1`.
- `parse_size` converts a string to `int`.
- `debug` logs via Python logging.
- `set_error` is a no-op.

Integration:
- The real `nbdkit` Python module exists only inside nbdkit.
- This stub allows local tests in `gcs.py` to import expected names without running inside nbdkit.

Limitations:
- It intentionally implements only the attributes needed by the embedded tests.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/gcs/nbdkit.py -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/golang/Makefile.am

This Automake file builds the Go plugin binding examples and documentation.

Key behavior:
- Defines shared Go binding sources under `src/libguestfs.org/nbdkit`.
- Distributes binding sources, test helper, example plugins, Go modules, and POD docs.
- When Go is available, builds four example plugins with `go build -buildmode=c-shared`.
- Sets `PKG_CONFIG_PATH` so cgo finds the built nbdkit package metadata.
- Runs `dump-plugin-examples.sh` as the test.
- If POD tooling is available, builds `nbdkit-golang-plugin.3`.

Integration:
- The binding package is not built separately; it is compiled into each example shared library.
- Clean rules remove generated example `.so` and `.h` files.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/config-test.go -->
# File Research: sources/virtualization/nbdkit/plugins/golang/config-test.go

This is a configure-time smoke test for Go support.

Behavior:
- Defines an empty `main` package with an empty `main` function.
- Used by `./configure` to confirm the Go toolchain can compile a trivial program.

Integration:
- It is distributed with the Go plugin sources and referenced by the build system.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/config-test.go -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/dump-plugin-examples.sh -->
# File Research: sources/virtualization/nbdkit/plugins/golang/dump-plugin-examples.sh

This shell test validates that built Go example plugins can be loaded by nbdkit.

Behavior:
- Runs with `set -e` and `set -x`.
- Iterates over `examples/*/nbdkit-*-plugin.so`.
- For each existing shared object, runs `../../nbdkit -f -v <plugin> --dump-plugin`.

Purpose:
- Confirms plugins were compiled correctly and can be loaded enough to answer `--dump-plugin`.
- Does not exercise read/write NBD I/O.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/dump-plugin-examples.sh -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/examples/disk/disk.go -->
# File Research: sources/virtualization/nbdkit/plugins/golang/examples/disk/disk.go

This Go example implements a per-client temporary writable disk.

Key behavior:
- Requires `size` config and parses it with `strconv.ParseUint`.
- `Open` creates an unlinked temporary file in `/var/tmp`, truncates it, and stores the file handle per connection.
- `GetSize` reads size from the temporary file metadata.
- `PRead` and `PWrite` use `ReadAt` and `WriteAt`, rejecting short I/O.
- `CanWrite` and `CanFlush` enable write and flush callbacks.
- `Flush` calls `Sync`.

Semantics:
- `CanMultiConn` returns false because each client receives a different temporary disk.
- The disk is transient and deleted after open/unlink and close.

Integration:
- Embeds `nbdkit.Plugin` and `nbdkit.Connection` defaults.
- Exports `plugin_init`, returning `nbdkit.PluginInitialize`.

Risks:
- Comments note reads/writes should loop for short I/O but currently fail instead.
- Uses deprecated `ioutil.TempFile`, reflecting older Go style.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/examples/disk/disk.go -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/examples/dump-plugin/dumpplugin.go -->
# File Research: sources/virtualization/nbdkit/plugins/golang/examples/dump-plugin/dumpplugin.go

This Go example is a minimal read-only zero disk that also demonstrates `DumpPlugin`.

Key behavior:
- `DumpPlugin` prints `golang_dump_plugin=1`.
- `Open` returns a stateless connection.
- `GetSize` returns a fixed 1 MiB size.
- `PRead` fills the buffer with zeroes.

Integration:
- Uses required cgo boilerplate: imports `C` and `unsafe`, exports `plugin_init`, and calls `nbdkit.PluginInitialize`.
- Used by the build test to verify `--dump-plugin` behavior.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/examples/dump-plugin/dumpplugin.go -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/examples/minimal/minimal.go -->
# File Research: sources/virtualization/nbdkit/plugins/golang/examples/minimal/minimal.go

This is the smallest practical Go nbdkit plugin example.

Behavior:
- Opens a stateless connection.
- Reports a fixed 1 MiB export.
- Reads return zero-filled data.
- Does not implement writes, flush, trim, zero, or config.

Integration:
- Demonstrates the required Go plugin boilerplate: `C` import, `unsafe`, exported `plugin_init`, and a dummy `main`.
- Embeds default `nbdkit.Plugin` and `nbdkit.Connection` implementations.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/examples/minimal/minimal.go -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/examples/ramdisk/ramdisk.go -->
# File Research: sources/virtualization/nbdkit/plugins/golang/examples/ramdisk/ramdisk.go

This Go example implements a shared in-memory writable RAM disk.

Key behavior:
- Requires `size` configuration.
- `GetReady` allocates a global `[]byte` of the requested size.
- `Open` returns a stateless connection.
- `GetSize` returns the configured size.
- `PRead` and `PWrite` copy to/from the global byte slice.
- `CanWrite` enables writes.
- `CanMultiConn` returns true because all clients share the same backing slice.

Risks:
- No explicit locking around the shared byte slice; safety depends on nbdkit/threading expectations and Go runtime behavior for concurrent slice access.
- Offset conversion mixes `uint64` and `int`, which can overflow on very large sizes.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/examples/ramdisk/ramdisk.go -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/src/libguestfs.org/nbdkit/nbdkit.go -->
# File Research: sources/virtualization/nbdkit/plugins/golang/src/libguestfs.org/nbdkit/nbdkit.go

This is the main Go binding layer that lets Go code implement nbdkit plugins.

Public API:
- Defines `PluginInterface` for lifecycle/config/open callbacks.
- Defines `ConnectionInterface` for per-connection size, read, write, flush, trim, zero, multi-conn, rotational, and close callbacks.
- Provides default `Plugin` and `Connection` structs with no-op or conservative implementations.
- Exposes nbdkit constants for thread models, flags, FUA, cache, extents, and API version.
- Defines `PluginError` to carry an error message and optional errno.

C/Go bridge:
- Exported `impl*` functions convert C callbacks into Go method calls.
- Connections are stored in a global `map[uintptr]ConnectionInterface`, protected by a mutex.
- `implOpen` assigns nonzero integer handles cast to pointers.
- `implPRead` and `implPWrite` wrap C memory as Go `[]byte` using `reflect.SliceHeader` and `unsafe`.
- `PluginInitialize` builds a C `struct nbdkit_plugin`, fills callback pointers from C wrappers, mallocs a permanent copy, and returns it.

Important behavior:
- The binding sets thread model to parallel in the plugin struct.
- Go plugins are marked as not preserving errno.
- `set_error` maps `PluginError` through `nbdkit_set_error` and `nbdkit_error`.

Risks:
- Uses unsafe slice construction over C buffers.
- Connection handle IDs are pointer-shaped integers, requiring nonzero start.
- Some locking uses exclusive `Lock` where `RLock` would suffice, but correctness is maintained.
- `PluginError.String` appears inverted: it prints errno text when `Errno == 0`, likely contrary to intent.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/src/libguestfs.org/nbdkit/nbdkit.go -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/src/libguestfs.org/nbdkit/utils.go -->
# File Research: sources/virtualization/nbdkit/plugins/golang/src/libguestfs.org/nbdkit/utils.go

This file exposes small Go utility wrappers around nbdkit C helper functions.

Key behavior:
- cgo imports `nbdkit-plugin.h` and defines `_nbdkit_debug` and `_nbdkit_error` wrappers because cgo cannot call varargs functions directly.
- `Debug` sends a string to `nbdkit_debug`.
- `Error` sends a string to `nbdkit_error`.
- `SetError` calls `nbdkit_set_error`.

Integration:
- Used by `nbdkit.go` error mapping and by example plugins for debug logging.
- Relies on `pkg-config: nbdkit`.

Risk:
- `C.CString` allocations in `Debug` and `Error` are not freed, which can leak for repeated calls.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/src/libguestfs.org/nbdkit/utils.go -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/src/libguestfs.org/nbdkit/wrappers.go -->
# File Research: sources/virtualization/nbdkit/plugins/golang/src/libguestfs.org/nbdkit/wrappers.go

This file contains C wrapper functions embedded via cgo so nbdkit can call stable C symbols that forward into exported Go functions.

Key behavior:
- Defines `wrapper_*` functions for load, unload, dump_plugin, config, config_complete, get_ready, preconnect, open, close, get_size, capability checks, and I/O callbacks.
- Each wrapper calls the corresponding exported `impl*` Go function.
- Saves the original PID during load.
- `nonwrapper_after_fork` warns if the process has forked after loading a Go plugin.

Integration:
- `nbdkit.go` installs these wrapper function pointers into `struct nbdkit_plugin`.
- `wrappers.h` declares the wrapper symbols for cgo compilation.

Important note:
- The after-fork handler warns but currently returns success; a commented `return -1` shows stricter behavior was considered.
- This reflects the documented concern that Go plugins should not be used across forked processes.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/src/libguestfs.org/nbdkit/wrappers.go -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/src/libguestfs.org/nbdkit/wrappers.h -->
# File Research: sources/virtualization/nbdkit/plugins/golang/src/libguestfs.org/nbdkit/wrappers.h

This header declares the C wrapper callback symbols used by the Go binding.

Contents:
- Lifecycle wrappers: load, unload, dump_plugin, config, config_complete, get_ready, after_fork, preconnect.
- Connection wrappers: open, close, get_size, capability checks.
- I/O wrappers: pread, pwrite, flush, trim, zero.

Integration:
- Included by cgo blocks in `nbdkit.go` and `wrappers.go`.
- Function signatures match nbdkit API version 2 callback types.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/golang/src/libguestfs.org/nbdkit/wrappers.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/guestfs/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/guestfs/Makefile.am

This Automake file builds the libguestfs-backed plugin when libguestfs is available.

Key behavior:
- Gated by `HAVE_LIBGUESTFS`.
- Builds `nbdkit-guestfs-plugin.la` from `guestfs-plugin.c`.
- Adds include paths for nbdkit headers and common utilities.
- Links `libutils`, Windows import library if needed, and `LIBGUESTFS_LIBS`.
- Uses module/shared libtool flags and optional linker version script.
- Builds the man page when POD tooling is available.

Integration:
- Dependency gating prevents building when libguestfs development files are absent.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/guestfs/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/guestfs/guestfs-plugin.c -->
# File Research: sources/virtualization/nbdkit/plugins/guestfs/guestfs-plugin.c

This plugin uses libguestfs to expose a file or block device from inside disk images or libvirt domains over NBD.

Configuration:
- `export` is required and names the device or file inside the guestfs appliance.
- At least one `disk` or `domain` is required.
- `format` applies to subsequent disk arguments.
- `connect` sets libvirt URI for domains.
- `mount` can be `inspect`, `DEVICE`, or `DEVICE:MOUNTPOINT`.
- `debug` and `trace` enable libguestfs verbosity/tracing.

Connection setup:
- Creates a libguestfs handle with no environment.
- Parses guestfs environment after explicit handle creation.
- Installs a libguestfs event callback that forwards logs to `nbdkit_debug`.
- Adds disks/domains in original user order using recursion over reverse-built lists.
- Launches guestfs, mounts requested filesystems, then determines exported size with either block-device or file APIs.

I/O behavior:
- Uses serialized-connections thread model.
- `.pread` calls `guestfs_pread_device` or `guestfs_pread` in a loop.
- `.pwrite` calls the matching write API in a loop.
- `.flush` calls `guestfs_sync`.
- Errors are translated through `guestfs_last_error` and `guestfs_last_errno`.

Risks and edge cases:
- `mount` parsing mutates the config string after casting away `const`.
- Recursive list replay could be deep for very many disks/mounts, though typical use is small.
- Read/write loop depends on libguestfs returning progress; zero-size progress would be problematic but is not expected.
- Export path beginning `/dev/` decides block-device mode.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/guestfs/guestfs-plugin.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/info/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/info/Makefile.am

This Automake file builds the `info` plugin.

Key behavior:
- Builds `nbdkit-info-plugin.la` from `info.c`.
- Includes common headers and optional GnuTLS flags/libs for base64 support.
- Uses module/shared libtool flags and optional linker version script.
- Generates `nbdkit-info-plugin.1` with magic-parameter documentation insertion when POD tooling is available.

Integration:
- Base64 mode support depends on GnuTLS configuration macros and libraries.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/info/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/info/info.c -->
# File Research: sources/virtualization/nbdkit/plugins/info/info.c

This plugin exposes small synthetic block exports containing connection or server metadata.

Modes:
- `exportname` returns the client export name.
- `base64exportname` decodes the export name as base64.
- `address` returns peer address as text.
- `time` returns current wall-clock seconds/useconds.
- `uptime` returns time since plugin load.
- `conntime` returns time since connection open.
- `version` returns the nbdkit version string.

Implementation:
- `info_load` records plugin load time.
- `info_open` constructs per-connection data depending on mode.
- Time modes allocate 12 bytes and refresh data on every read.
- Time values are packed big-endian: 8-byte seconds plus 4-byte microseconds.
- `.can_multi_conn` returns true only for stable modes.
- `.can_cache` returns native cache.

Optional dependencies:
- Base64 mode needs GnuTLS base64 decode support.
- Address mode needs `inet_ntop`.

Security considerations:
- Comments explicitly call out avoiding unbounded output, crashes, hangs, and host information leaks.
- Unix socket address mode returns only `unix`, not a filesystem path.

Risks:
- Time modes are intentionally not multi-connection safe.
- Base64 empty string is special-cased due to GnuTLS behavior.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/info/info.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/iso/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/iso/Makefile.am

This Automake file builds the ISO-generating plugin when ISO tooling is available and the platform is not Windows.

Key behavior:
- Gated by `HAVE_ISO` and `!IS_WINDOWS`.
- Builds `nbdkit-iso-plugin.la` from `iso.c`.
- Includes nbdkit headers, common utilities, and current directory.
- Links common utils and optional Windows import library.
- Uses optional linker version script.
- Builds the man page when POD tooling is available.

Reason for Windows exclusion:
- Comment notes the plugin uses `open_memstream` to construct shell commands.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/iso/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/iso/iso.c -->
# File Research: sources/virtualization/nbdkit/plugins/iso/iso.c

This plugin creates a temporary ISO image from one or more directories and serves it read-only over NBD.

Configuration:
- Requires at least one `dir`.
- `prog` overrides the ISO creation tool selected at compile time.
- `params` appends extra arguments to the ISO creation command.

Image creation:
- `.get_ready` calls `make_iso`.
- Creates a temporary file under `$TMPDIR` or `LARGE_TMPDIR`, then unlinks it.
- Builds a shell command with `shell_quote` for program and directories.
- Uses xorriso `-as mkisofs` when compiled for xorriso.
- Redirects ISO command output to the temp fd.
- Uses `exit_status_to_nbd_error` for command result mapping.

NBD behavior:
- `.get_size` uses `device_size` on the temp fd.
- `.block_size` prefers 2048 bytes to resemble CD media.
- `.can_multi_conn` is true.
- `.can_cache` asks nbdkit to emulate cache via reads.
- `.pread` loops on `pread` from the temp fd.

Risks:
- `params` is appended raw, intentionally allowing user-supplied command parameters but requiring trust.
- Requires external ISO tooling.
- Temporary ISO is fixed at `.get_ready`; source directory changes after that are not reflected.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/iso/iso.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/libvirt/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/libvirt/Makefile.am

This Automake file builds the libvirt plugin when libvirt is available.

Key behavior:
- Gated by `HAVE_LIBVIRT`.
- Builds `nbdkit-libvirt-plugin.la` from `libvirt-plugin.c`.
- Adds nbdkit include paths and libvirt compiler flags.
- Links libvirt libraries and optional Windows import library.
- Uses module/shared flags and optional linker version script.
- Builds the man page when POD tooling is available.

Integration:
- This build target is separate from the `guestfs` plugin even though both can interact with libvirt domains.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/libvirt/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/libvirt/libvirt-plugin.c -->
# File Research: sources/virtualization/nbdkit/plugins/libvirt/libvirt-plugin.c

This read-only plugin exposes a libvirt guest disk using `virDomainBlockPeek`.

Configuration:
- `domain` is required.
- `disk` is required.
- `connect` optionally sets a libvirt URI.

Connection setup:
- Opens a libvirt connection with `virConnectOpen`.
- Looks up the domain by name.
- Gets block info for the named disk and uses `info.physical` as export size.

I/O:
- Thread model serializes requests.
- `.pread` loops until the request is served.
- Individual `virDomainBlockPeek` calls are capped at 1 MiB for compatibility with older libvirt limits.
- Read failures set `errno = EIO`.

Limitations:
- Read-only by design because libvirt has no equivalent write API here.
- Uses libvirt error output indirectly; nbdkit messages point to earlier libvirt errors.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/libvirt/libvirt-plugin.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/linuxdisk/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/linuxdisk/Makefile.am

This Automake file builds the Linux virtual disk plugin when `mke2fs -d` support is available and the platform is not Windows.

Key behavior:
- Gated by `HAVE_MKE2FS_WITH_D` and `!IS_WINDOWS`.
- Builds `nbdkit-linuxdisk-plugin.la` from filesystem, plugin, GPT, virtual disk, and header files.
- Includes common GPT, regions, utils, and nbdkit headers.
- Links `libgpt`, `libregions`, `libutils`, and optional Windows import library.
- Uses optional linker version script.
- Builds the man page when POD tooling is available.

Integration:
- The plugin depends on external `mke2fs` behavior as well as in-tree GPT and region helpers.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/linuxdisk/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/linuxdisk/filesystem.c -->
# File Research: sources/virtualization/nbdkit/plugins/linuxdisk/filesystem.c

This file creates the ext-family filesystem image used inside the linuxdisk plugin's GPT disk.

Key behavior:
- If size is not explicitly supplied, estimates source directory size using `du -c -k -s <dir> | tail -n1`.
- Adds 20 percent metadata overhead and enforces a 1 MiB minimum.
- Adds 32 MiB for ext3/ext4 journal overhead.
- Supports `size=+SIZE` by adding the estimate to the user-supplied extra size.
- Rounds final size to 512-byte sectors.
- Creates and truncates a temporary file, runs `mke2fs -q -F -t <type> [-L label] -d <dir> <file>`, unlinks it, and stores the fd/size in `struct virtual_disk`.

Dependencies:
- Uses `shell_quote` and `exit_status_to_nbd_error` for command safety/status handling.
- Reads globals from `virtual-disk.h`: `dir`, `label`, `type`, `size`, `size_add_estimate`.

Risks:
- Relies on external `du`, `tail`, and `mke2fs`.
- `type` validation happens in `linuxdisk.c`; this file passes it into the command.
- Size estimation is intentionally approximate.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/linuxdisk/filesystem.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/linuxdisk/linuxdisk.c -->
# File Research: sources/virtualization/nbdkit/plugins/linuxdisk/linuxdisk.c

This is the nbdkit plugin entry point for serving a host directory as an ext2/ext3/ext4 filesystem inside a GPT-partitioned virtual disk.

Configuration:
- Requires `dir`.
- Optional `label`.
- `type` defaults to `ext2` and must start with `ext`.
- `size` can be exact or `+SIZE` to add extra space to the estimated filesystem size.

Lifecycle:
- `linuxdisk_load` initializes the global virtual disk and seeds random state for partition GUID generation.
- `linuxdisk_get_ready` calls `create_virtual_disk`.
- `linuxdisk_unload` frees regions, GPT buffers, and temp fd.

NBD behavior:
- Reports size from the virtual region layout.
- Multi-connection is safe because the generated disk is read-only after creation.
- Cache is emulated by nbdkit through reads.
- `.pread` dispatches across region types: temp filesystem file, in-memory GPT/MBR data, or zero padding.

Integration:
- Uses `filesystem.c` to create the ext filesystem.
- Uses `virtual-disk.c` for region layout.
- Uses `partition-gpt.c` for GPT structures.

Risks:
- Does not use `realpath` for `dir`, intentionally for external `mke2fs` path compatibility.
- Only a single `dir` is accepted.
- Source changes after `.get_ready` do not update the export.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/linuxdisk/linuxdisk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/linuxdisk/partition-gpt.c -->
# File Research: sources/virtualization/nbdkit/plugins/linuxdisk/partition-gpt.c

This file creates the GPT metadata and protective MBR for the linuxdisk plugin.

Key behavior:
- `create_partition_table` fills protective MBR, GPT partition entries, primary GPT header, and secondary GPT header.
- Protective MBR creates a partition type `0xee` covering the disk or the maximum MBR-representable span.
- GPT headers use standard signature/revision, primary/backup LBA fields, usable LBA range, partition entry location, and CRCs.
- The partition table contains one Linux filesystem partition for the region of type `region_file`.
- Partition type GUID is Linux filesystem data: `0FC63DAF-8483-4772-8E79-3D69D8477DE4`.
- Partition attributes set bit value `4` when marked bootable.

Dependencies:
- Uses common GPT structs/constants, EFI CRC32, byte swapping, alignment, rounding, and regions helpers.
- Consumes `disk->regions` and `disk->guid` created in `virtual-disk.c`.

Risks:
- The unique partition GUID is raw random bytes generated elsewhere and comments note it may not follow GUID conventions.
- Assumes exactly one `region_file` partition region.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/linuxdisk/partition-gpt.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/linuxdisk/virtual-disk.c -->
# File Research: sources/virtualization/nbdkit/plugins/linuxdisk/virtual-disk.c

This file owns the linuxdisk virtual disk object lifecycle and region layout.

Key behavior:
- `init_virtual_disk` zeroes state, sets fd to `-1`, and initializes regions.
- `create_virtual_disk` allocates GPT/MBR buffers, creates the filesystem temp file, generates a random 16-byte partition GUID, builds regions, then fills partition-table structures.
- `free_virtual_disk` frees regions and metadata buffers and closes the filesystem fd.
- `create_regions` lays out the disk as protective MBR, primary GPT header/table, aligned filesystem partition at sector 2048, secondary GPT table, and secondary GPT header.

Integration:
- Calls `create_filesystem` from `filesystem.c`.
- Calls `create_partition_table` from `partition-gpt.c`.
- Uses common `regions` helper to model sparse disk data.

Risks:
- Metadata allocation and filesystem creation happen before final partition metadata is filled, so ordering matters.
- GPT structures depend on the final `regions` virtual size.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/linuxdisk/virtual-disk.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/linuxdisk/virtual-disk.h -->
# File Research: sources/virtualization/nbdkit/plugins/linuxdisk/virtual-disk.h

This header defines shared linuxdisk plugin state and APIs.

Key definitions:
- Extern configuration globals: `dir`, `label`, `type`, `size`, and `size_add_estimate`.
- Extern `random_state` used for partition GUID generation.
- `SECTOR_SIZE` is 512.
- `struct virtual_disk` contains regions, protective MBR, primary/secondary GPT headers, GPT partition table, filesystem size, partition GUID, and temp filesystem fd.

Declared APIs:
- `init_virtual_disk`, `create_virtual_disk`, `free_virtual_disk`.
- `create_partition_table`.
- `create_filesystem`.

Integration:
- Shared by `linuxdisk.c`, `filesystem.c`, `partition-gpt.c`, and `virtual-disk.c`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/linuxdisk/virtual-disk.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/lua/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/lua/Makefile.am

This Automake file builds the Lua language plugin when Lua is available.

Key behavior:
- Distributes the POD and `example.lua`.
- Gated by `HAVE_LUA`.
- Builds `nbdkit-lua-plugin.la` from `lua.c`.
- Uses Lua compiler/linker flags.
- Uses module/shared flags and optional linker version script.
- Builds `nbdkit-lua-plugin.3` when POD tooling is available.

Integration:
- The Lua plugin is a language binding plugin rather than a direct storage backend.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/lua/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/lua/example.lua -->
# File Research: sources/virtualization/nbdkit/plugins/lua/example.lua

This Lua script is an example plugin that serves a local file.

Key behavior:
- `dump_plugin` prints `example_lua=1`.
- `config` accepts `file=<path>` and rejects unknown parameters.
- `config_complete` requires `file`.
- `open` opens the file in `rb` or `r+b` depending on readonly mode and returns the Lua file handle.
- `close` closes the handle.
- `get_size` seeks to end and returns file size.
- `pread` seeks and reads the requested bytes.
- `pwrite` seeks and writes the supplied buffer.

Integration:
- Intended to be run through `nbdkit lua example.lua file=disk.img`.
- Demonstrates that Lua handles can be arbitrary Lua objects.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/lua/example.lua -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/lua/lua.c -->
# File Research: sources/virtualization/nbdkit/plugins/lua/lua.c

This file implements the nbdkit Lua language plugin, forwarding nbdkit callbacks into functions defined by a Lua script.

Lifecycle/config:
- Creates a global Lua interpreter in `.load` and opens standard libraries.
- Requires the first parameter to be `script=<path>`.
- Loads and runs the Lua script during config.
- Requires Lua functions `open`, `get_size`, and `pread`.
- Subsequent config keys are forwarded to Lua `config` if defined.
- `config_complete` forwards to Lua `config_complete` if defined.
- `dump_plugin` prints Lua version and optionally calls Lua `dump_plugin`.

Handle model:
- `open` calls Lua `open(readonly)` and stores the returned Lua object in the registry.
- The C handle is an allocated integer registry reference.
- `close` optionally calls Lua `close(handle)`, then unreferences the Lua object.

I/O and capabilities:
- `get_size` expects integer/number result.
- `pread` expects a string at least as long as requested.
- `pwrite`, `flush`, `trim`, and `zero` call matching Lua functions when available.
- `can_write`, `can_flush`, `can_trim`, and `is_rotational` call Lua capability functions when available.
- If `pwrite`, `flush`, or `trim` exists without a matching `can_*`, capability defaults to enabled for write/flush/trim.
- `zero` falls back with `EOPNOTSUPP` if no Lua zero function exists.

Threading:
- Uses `NBDKIT_THREAD_MODEL_SERIALIZE_ALL_REQUESTS`, appropriate for a single global Lua state.

Compatibility:
- Provides a fallback `lua_isinteger` for Lua versions lacking it.

Risks:
- One global Lua state means all scripts/connections share interpreter state.
- Lua callback type validation is strict but simple.
- `can_flush` checks for `plugin_flush` in one fallback branch, while the actual callback name is `flush`; this looks suspicious.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/lua/lua.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/memory/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/memory/Makefile.am

This Automake file builds the in-memory block device plugin.

Key behavior:
- Builds `nbdkit-memory-plugin.la` from `memory.c`.
- Includes allocator, replacement, utility, and nbdkit headers.
- Links allocator, compat, utils, and optional Windows import libraries.
- Uses module/shared flags and optional linker version script.
- Builds `nbdkit-memory-plugin.1` with magic-parameter insertion when POD tooling is available.

Integration:
- Runtime allocator behavior is supplied by the common allocator library.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/memory/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/memory/memory.c -->
# File Research: sources/virtualization/nbdkit/plugins/memory/memory.c

This plugin implements a writable volatile memory-backed block device using pluggable allocator backends.

Configuration:
- Requires `size=<SIZE>`.
- Optional `allocator=<type>` defaults to `sparse`.
- Exposes debug variable `memory_debug_dir` for allocator directory operations.

Lifecycle:
- `.get_ready` creates the selected allocator and passes the size hint.
- `.unload` frees the allocator.
- No per-connection handle is needed.

Capabilities:
- Parallel thread model.
- Native FUA because flush is a no-op.
- Multi-connection safe.
- Native cache.
- Fast zero supported.
- Exposes allocator-provided extents.

I/O:
- `.pread`, `.pwrite`, `.zero`, `.trim`, and `.extents` delegate to allocator function pointers.
- `.trim` is implemented as zero.
- `.flush` returns success.

Integration:
- Uses `common/allocators` abstraction, so sparse/compressed/other behavior is selected outside this file.
- `dump_plugin` advertises `mlock` and `zstd` availability.

Risks:
- Correctness and concurrency depend on allocator implementation.
- Assertions enforce expected flags but are compiled out under `NDEBUG`.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/memory/memory.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/nbdkit/plugins/nbd/Makefile.am -->
# File Research: sources/virtualization/nbdkit/plugins/nbd/Makefile.am

This Automake file builds the nbd proxy/client plugin when libnbd is available.

Key behavior:
- Gated by `HAVE_LIBNBD`.
- Builds `nbdkit-nbd-plugin.la` from `nbd.c` and nbdkit headers.
- Includes common headers, utils, and server headers.
- Uses libnbd compiler/linker flags.
- Links common utils, optional Windows import library, and `LIBNBD_LIBS`.
- Uses module/shared flags and optional linker version script.
- Builds `nbdkit-nbd-plugin.1` with magic-parameter documentation insertion when POD tooling is available.

Integration:
- This file only covers build wiring; the runtime implementation is in `nbd.c`, which was not part of this work item.
<!-- END FILE RESEARCH: sources/virtualization/nbdkit/plugins/nbd/Makefile.am -->