# Group Research: group_1797_util_linux_sources_block_storage_util_linux_libmount_python_fs_c_so_371e45641c13

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/block-storage/util-linux`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/python/fs.c -->
# File Research: sources/block-storage/util-linux/libmount/python/fs.c

Python C-extension binding for `struct libmnt_fs`, exposed as `libmount.Fs`.

Key responsibilities:
- Defines `Fs` construction with optional `source`, `root`, `target`, `fstype`, `options`, `attributes`, `freq`, and `passno`.
- Exposes libmount filesystem fields as Python properties: mountinfo IDs, source/source path, root, target, fstype, options classes, attributes, fstab dump/fsck fields, swap metadata, tag, TID, and comments.
- Implements mutating helpers for appending/prepending options and attributes.
- Implements matching/comparison helpers for filesystem type, options, source path, and target.
- Provides `copy_fs()` and `print_debug()`.
- Bridges libmount FS pointers back to Python objects via `mnt_fs_set_userdata()` in `PyObjectResultFs()`.

Important behavior:
- String getters map missing C strings to Python `None`.
- `print_debug()` works around Python stdout truncation by chunking long strings.
- `Fs_init()` replaces any existing `self->fs` with a new `mnt_new_fs()` and stores the Python object as libmount userdata.
- `PyObjectResultFs()` reuses an existing wrapper from `fs->userdata`; otherwise it creates a wrapper, refs the libmount FS, and stores the wrapper in userdata.

Dependencies:
- Depends on `pylibmount.h`, Python C API, and libmount `mnt_fs_*` APIs.
- Uses common helper functions from `pylibmount.c`: `PyObjectResultInt`, `PyObjectResultStr`, `pystos`, `UL_RaiseExc`, and `UL_IncRef`.

Notable risks:
- Existing-object `copy_fs(dest)` returns `dest` without `Py_INCREF()`, which is not normal for a Python C API return value.
- `Fs_set_freq()` and `Fs_set_passno()` return raw libmount status and do not translate errors into Python exceptions.
- `PyObjectResultFs()` uses extra Python references to keep userdata wrappers alive; correctness depends on matching cleanup in table/context owners.
- TODO comments note missing source/target matching and per-attribute/per-option accessors.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/python/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/python/meson.build -->
# File Research: sources/block-storage/util-linux/libmount/python/meson.build

Meson build recipe for the Python libmount extension package.

Key responsibilities:
- Skips the subdirectory when `build-python` is disabled.
- Builds `pylibmount` from `pylibmount.c`, `pylibmount.h`, `fs.c`, and `tab.c`.
- Adds `context.c` only on Linux.
- Locates the requested Python installation and builds an extension module installed under `libmount`.
- Installs `__init__.py` into the same package.

Important behavior:
- For Meson older than 1.4.1, explicitly checks for `Python.h` using the Python include path.
- Suppresses `-Wcast-function-type`.
- Suppresses Python 3.12 redundant-declaration warnings as a workaround for util-linux issue 2366.
- Links against `mount_dep` and `python.dependency(embed: true)`.

Dependencies:
- Meson Python module, configured `mount_dep`, `dir_include`, `LINUX`, and project options `build-python`/`python`.

Notable risks:
- Linux-only inclusion means `Context` is absent from non-Linux builds while `Fs` and `Table` remain available.
- The extension build is coupled to generated include directories and libmount availability.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/python/meson.build -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/python/pylibmount.c -->
# File Research: sources/block-storage/util-linux/libmount/python/pylibmount.c

Top-level Python module implementation for the libmount bindings.

Key responsibilities:
- Defines the `libmount.Error` exception.
- Provides shared helpers for reference increments, object freeing, exception translation, integer/string result creation, and Python-string-to-C-string conversion.
- Initializes debug masks from `PYLIBMOUNT_DEBUG`.
- Creates the `pylibmount` module and registers `Fs`, `Table`, and Linux-only `Context`.
- Exports mount userspace option constants, Linux `MS_*` constants, and iterator direction constants.

Important behavior:
- `UL_RaiseExc()` maps common `errno` and libmount-specific `MNT_ERR_*` codes to Python exceptions.
- `PyObjectResultStr()` returns `None` for NULL C strings.
- `pystos()` accepts Python 3 Unicode objects and returns their internal one-byte data pointer.
- Python 3 module state supports traversal and clear for the stored error object.
- `mnt_init_debug(0)` is called during module init.

Dependencies:
- Depends on `pylibmount.h`, Python C API, libmount constants/APIs, and the module-object registration functions from `fs.c`, `tab.c`, and Linux `context.c`.

Notable risks:
- `pystos()` assumes a one-byte Unicode representation and does not explicitly encode or verify null-terminated UTF-8/ASCII data.
- `LibmountError` is global while module state also stores an `error` field only used by the sample `error_out()` method.
- Many `PyModule_AddIntConstant()` calls ignore return values.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/python/pylibmount.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/python/pylibmount.h -->
# File Research: sources/block-storage/util-linux/libmount/python/pylibmount.h

Shared header for pylibmount C-extension source files.

Key responsibilities:
- Includes Python and libmount headers.
- Defines debug masks and debug macros for init, table, filesystem, and context paths.
- Defines common error strings.
- Declares Python wrapper structs for `FsObject`, `TableObject`, and Linux-only `ContextObjext`.
- Declares exported type objects, module registration functions, wrapper conversion helpers, and utility helpers.

Important behavior:
- Debug logging is always compiled because `CONFIG_PYLIBMOUNT_DEBUG` is defined in the header.
- `TableObject` owns a `libmnt_table`, iterator, and parser error callback.
- `FsObject` owns or references a `libmnt_fs` through libmount refcounting.
- `ContextObjext` is guarded by `__linux__`.

Dependencies:
- Depends on `c.h`, generated/public `libmount.h`, Python C API, and util-linux debug conventions.

Notable risks:
- `ContextObjext` appears misspelled, which is harmless if consistently used but awkward for maintainability.
- Header guard closing comment names `UTIL_LINUX_PYLIBMOUNT`, while the actual guard is `UTIL_LINUX_PYLIBMOUNT_H`.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/python/pylibmount.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/python/tab.c -->
# File Research: sources/block-storage/util-linux/libmount/python/tab.c

Python C-extension binding for `struct libmnt_table`, exposed as `libmount.Table`.

Key responsibilities:
- Creates and initializes table objects from nothing, a file, or a directory.
- Supports parser error callbacks from Python.
- Exposes table comments, entry count, parsing functions, find functions, add/remove FS, iteration, write, and atomic file replacement.
- Attaches a libmount cache to each initialized table.
- Converts libmount table pointers back into Python wrappers via `PyObjectResultTab()`.

Important behavior:
- `Table_init()` resets prior table state, handles optional path parsing, sets parser callback/userdata, and always installs a cache.
- `next_fs()` uses a built-in forward iterator and resets it at end-of-list.
- `Table_unref()` walks contained filesystems and decrefs Python userdata wrappers before unrefing the table.
- Parser callback calls the Python callable with `(table_object, filename, line)` and expects an integer return code.

Dependencies:
- Depends on `pylibmount.h`, Python C API, `stat(2)`, libmount table/parser/cache APIs, and `FsType`/`PyObjectResultFs()`.

Notable risks:
- `Table_add_fs()` increments the Python FS object before `mnt_table_add_fs()` but does not roll back the Python ref on failure.
- `Table_remove_fs()` decrefs the Python FS after removal regardless of whether removal succeeded.
- `Table_repr()` calls `PyObject_Repr(self->errcb)` and converts it through `pystos()` without decrefing the repr object.
- Path initialization leaves `self->tab` NULL if `path` exists but is neither regular file nor directory, then unconditionally uses it.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/python/tab.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/python/test_mount_context.py -->
# File Research: sources/block-storage/util-linux/libmount/python/test_mount_context.py

Command-line smoke test harness for the Python `Context` binding.

Key responsibilities:
- Provides shared usage and test dispatch helpers.
- Exercises `Context.mount()`, `Context.umount()`, `prepare_mount()`/flags display, and mount-all iteration.
- Parses simple mount-like options from argv.
- Sets a mount-compatible umask before dispatch.

Important behavior:
- Imports `pylibmount as mnt`, with a comment noting installed use should be `import libmount`.
- `--mount` accepts optional `-o`, `-t`, and either target-only or source+target forms.
- `--umount` supports `-f`, `-l`, and `-r`.
- `--flags` prints prepared options and mount flags.
- `--mount-all` is skeletal and appears incomplete.

Dependencies:
- Depends on Linux-only Python `Context` binding and real mount/umount privileges/environment for many paths.

Notable risks:
- `test_mountall()` uses `i.target` even though `i` is initialized to an empty tuple and never assigned from `cxt.next_mount()`.
- Some option parsing checks `argv[idx]` without ensuring `idx` is still in range after prior options.
- This is not structured as `unittest`/`pytest`; it is an executable sample harness.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/python/test_mount_context.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/python/test_mount_tab.py -->
# File Research: sources/block-storage/util-linux/libmount/python/test_mount_tab.py

Command-line smoke test harness for the Python `Table` and `Fs` bindings.

Key responsibilities:
- Parses mount table files with optional comment support.
- Installs a parser error callback.
- Iterates and prints filesystem records.
- Tests lookup by source, target, pair, mountpoint, and mounted-state checks.
- Tests copying an `Fs` object.

Important behavior:
- `create_table()` constructs an empty table, enables comments, sets `errcb`, and calls `parse_file()`.
- `--parse` prints intro/trailing comments and all entries via `next_fs()`.
- `--copy-fs` finds `/`, prints it, copies it, and prints the copy.
- `--find-forward` and `--find-backward` pass explicit iterator direction constants.

Dependencies:
- Depends on `pylibmount.Table`, `pylibmount.Fs`, parser callbacks, and real mount table files such as `/proc/self/mountinfo`.

Notable risks:
- Uses `mnt.Tab` in `test_is_mounted()`, but the binding type is registered as `Table`.
- Uses `ft.iter(...)`, but `functools` has no `iter` attribute; intended Python built-in `iter()` is used elsewhere.
- `test_find()` leaves `fs` undefined for unsupported lookup names.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/python/test_mount_tab.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/python/test_mount_tab_update.py -->
# File Research: sources/block-storage/util-linux/libmount/python/test_mount_tab_update.py

Small command-line harness for updating an fstab-style file through the Python `Table` binding.

Key responsibilities:
- Creates a new `Fs` and `Table`.
- Parses the current fstab.
- Adds a new filesystem entry from command-line source and target.
- Replaces the file named by `LIBMOUNT_FSTAB`.

Important behavior:
- Enables comment parsing before parsing fstab.
- Sets a hard-coded comment on the new filesystem.
- Uses `Table.replace_file()` for the final write/replace operation.

Dependencies:
- Depends on `pylibmount.Fs`, `pylibmount.Table`, and the `LIBMOUNT_FSTAB` environment variable.

Notable risks:
- Modifies the file named by `LIBMOUNT_FSTAB`; unsafe if pointed at a real fstab.
- Does not set fstype, options, freq, or passno for the new entry.
- Minimal argument validation and no exception handling around parse/replace.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/python/test_mount_tab_update.py -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/samples/Makemodule.am -->
# File Research: sources/block-storage/util-linux/libmount/samples/Makemodule.am

Automake fragment for libmount sample programs.

Key responsibilities:
- Adds Linux-only sample check programs for mount overwrite, statmount, and listmount.
- Defines source files, link libraries, and include flags for each sample.

Important behavior:
- Samples are included only when `LINUX` is true.
- `statmount` and `listmount` also link `libcommon.la`; `overwrite` links only `libmount.la` plus common `LDADD`.

Dependencies:
- Depends on the larger Automake build variables: `check_PROGRAMS`, `AM_CFLAGS`, `ul_libmount_incdir`, `LDADD`, `libmount.la`, and `libcommon.la`.

Notable risks:
- These are check/sample binaries, not installed utilities.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/samples/Makemodule.am -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/samples/listmount.c -->
# File Research: sources/block-storage/util-linux/libmount/samples/listmount.c

Sample comparing kernel `listmount()`/`statmount()` based mount table enumeration with `/proc/self/mountinfo`.

Key responsibilities:
- Builds a libmount table from `listmount()`.
- Optionally restricts listing to a mount ID or path-derived mount ID.
- Uses `libmnt_statmnt` to fetch mountpoint and filesystem type data.
- Prints listmount-based, procfs-based, and stepped reverse iteration outputs.
- Measures elapsed time for listmount-only, listmount+statmount, and mountinfo parsing.

Important behavior:
- Sets a statmount mask for mountpoint and filesystem type where kernel constants are available.
- Demonstrates on-demand statmount fetching by iterating the table.
- Demonstrates on-demand listmount in small steps by setting step size to 5 and enabling listmount backend.

Dependencies:
- Depends on libmount listmount/statmount support, `mountutils.h` fallbacks, `timeutils.h`, `strutils.h`, and `_PATH_PROC_MOUNTINFO`.

Notable risks:
- Designed for newer Linux kernels; failures are warned but the sample continues.
- Contains a typo in output text: `/proc/sef/mountinfo`.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/samples/listmount.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/samples/overwrite.c -->
# File Research: sources/block-storage/util-linux/libmount/samples/overwrite.c

Sample showing how to mount an fstab entry onto a different command-line target.

Key responsibilities:
- Parses `/etc/fstab`.
- Finds an entry by its original fstab target.
- Creates a mount context, installs the found `Fs`, overrides the target, and mounts.
- Prints raw libmount return and context status.

Important behavior:
- Usage is `<mnt-from-fstab> <target>`.
- Reuses fstab options/source/fstype via `mnt_context_set_fs()`.
- Calls `mnt_context_set_target()` after applying the fstab FS to overwrite only the target.

Dependencies:
- Depends on libmount table lookup and mount context APIs.

Notable risks:
- Calls `mnt_context_get_status(cxt)` after `mnt_free_context(cxt)` in the return expression, which is use-after-free.
- Performs real mounts and requires appropriate privileges/environment.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/samples/overwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/samples/statmount.c -->
# File Research: sources/block-storage/util-linux/libmount/samples/statmount.c

Sample demonstrating direct and on-demand `statmount()` data retrieval for one filesystem.

Key responsibilities:
- Accepts a mountpoint or numeric mount ID.
- Creates an `Fs` and identifies it by target or unique ID.
- Fetches all statmount data directly.
- Resets the FS and demonstrates lazy/on-demand statmount reads through a shared `libmnt_statmnt`.

Important behavior:
- Numeric argv is treated as a mount ID; non-numeric argv as a mountpoint.
- Shows that reading fstype/root triggers targeted statmount reads.
- Final full fetch fills missing statmount data.

Dependencies:
- Depends on libmount statmount support, `mountutils.h` fallbacks, and `strutils.h`.

Notable risks:
- New-kernel functionality; older systems may warn on statmount fetch.
- Intended as a diagnostic sample rather than a robust command-line tool.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/samples/statmount.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/Makemodule.am -->
# File Research: sources/block-storage/util-linux/libmount/src/Makemodule.am

Main Automake build fragment for libmount.

Key responsibilities:
- Defines generated/public libmount include installation.
- Builds `libmount.la` from core table, fs, parser, option, lock, cache, update, diff, listmount/statmount, utility, test, init, and version sources.
- Adds Linux-only context, hook, monitor, and optional Btrfs sources.
- Defines libmount link dependencies and compile flags.
- Defines static check binaries for libmount unit/smoke tests.
- Installs hooks to move shared objects from `usrlib_execdir` to `libdir` when needed.

Important behavior:
- `btrfs.c` is included only when both Linux and `HAVE_BTRFS` are true.
- Tests are gated by `BUILD_LIBMOUNT_TESTS`; monitor/context tests are Linux-only.
- Fuzz target is conditional on `FUZZING_ENGINE`.
- Shared library versioning uses `LIBMOUNT_VERSION_INFO` and optional version scripts.

Dependencies:
- Depends on libcommon, libblkid, optional SELinux, cryptsetup, systemd/udev, realtime libs, and many project configuration variables.

Notable risks:
- Build surface is highly conditional; source availability differs by platform and configure options.
- Install hook performs manual shared-library relocation and symlink recreation.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/Makemodule.am -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/btrfs.c -->
# File Research: sources/block-storage/util-linux/libmount/src/btrfs.c

Btrfs helper for discovering a mounted volume's default subvolume ID.

Key responsibilities:
- Provides missing kernel-header definitions for older `linux/btrfs.h`.
- Opens a Btrfs mount path and issues `BTRFS_IOC_TREE_SEARCH`.
- Searches the root tree directory object for the `default` dir item.
- Returns the default subvolume object ID or `UINT64_MAX` on no default/error.

Important behavior:
- Uses `opendir()`/`dirfd()` so the ioctl is issued on the mounted directory.
- Limits search to root tree object/directory and one item.
- Interprets Btrfs little-endian disk key fields through helper accessors.
- Logs failures via Btrfs debug messages and preserves errno from failing syscalls/ioctls.

Dependencies:
- Linux Btrfs ioctl ABI, `mountP.h`, `bitops.h`, and endian conversion helpers.

Notable risks:
- Relies on kernel Btrfs search result layout and local fallback structure definitions.
- Compares `"default"` using `strncmp("default", name, name_len)`, so malformed shorter prefixes could be surprising if returned by the kernel.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/btrfs.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/cache.c -->
# File Research: sources/block-storage/util-linux/libmount/src/cache.c

Refcounted libmount cache for canonical paths and filesystem tags.

Key responsibilities:
- Caches path canonicalization results and tag-to-device mappings.
- Resolves `LABEL`, `UUID`, `TYPE`, `PARTUUID`, and `PARTLABEL` through blkid and optional systemd `sd-device`.
- Provides tag-read caching for devices.
- Provides filesystem type probing.
- Resolves specs that may be paths or tags.
- Optimizes mountpoint target resolution using cached mountinfo.
- Provides `mnt_pretty_path()` including Linux loop backing-file display.

Important behavior:
- Cache entries store path keys/values or tag keys in `TAG\0VALUE\0` format.
- `mnt_resolve_path()` returns cached pointers when a cache is supplied; without cache callers own the returned allocation.
- `mnt_resolve_target()` can avoid `realpath()` for known kernel mountpoints to avoid autofs/stale mount hangs.
- Restricted contexts can enable `noprobe`, preventing active blkid probing.
- Test mode provides stdin-driven `--resolve-path`, `--resolve-spec`, and `--read-tags`.

Dependencies:
- Depends on libblkid, optional systemd `sd-device`, util-linux canonicalization, loopdev, mangle, path comparison, and libmount table APIs.

Notable risks:
- Ownership differs depending on whether a cache is passed; callers must know when returned strings are borrowed from the cache.
- Linear cache lookup is simple but may be costly with many entries.
- Tag resolution behavior differs depending on udev support, blkid cache, and noprobe mode.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/cache.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/context.c -->
# File Research: sources/block-storage/util-linux/libmount/src/context.c

Core high-level libmount context implementation shared by mount and umount flows.

Key responsibilities:
- Allocates, resets, clones, and frees `libmnt_context`.
- Manages context flags, options mode, filesystem object, option list, fstab, mountinfo, utab, cache, lock, target prefix, target namespace, and helper mode.
- Applies fstab or mountinfo entries to the current context.
- Resolves source paths/tags and guesses filesystem types.
- Prepares userspace table updates and emits update events.
- Tracks syscall/helper status and buffered kernel/libmount messages.
- Converts operation outcomes to mount-compatible exit codes.
- Supports forked mount-all children and mount namespace switching.
- Includes a `TEST_PROGRAM` command harness.

Important behavior:
- New contexts are restricted unless real root and not privileged/setuid execution.
- `mnt_reset_context()` resets per-operation state but preserves selected policy flags, cached fstab/cache, target namespace, target prefix, and patterns.
- `mnt_context_get_fs()` lazily creates an FS and links it to the context option list.
- `mnt_context_get_fstab()` and `mnt_context_get_mountinfo()` parse under the target namespace and attach context cache/callbacks.
- Restricted contexts force fstab use through `MNT_OMODE_USER`.
- Source preparation resolves tags, canonicalizes paths unless disabled, skips netfs/pseudofs/ZFS special cases, and invokes source hooks.
- Namespace switching also swaps namespace-associated caches.

Dependencies:
- Depends on `mountP.h`, option-list APIs, table/parser APIs, cache APIs, update/lock APIs, namespace support, hook framework, blkid-derived type probing, and Linux mount constants.

Notable risks:
- Namespace switching is global to the process and must always switch back correctly.
- Error paths around namespace switching can return before cleanup in some helper functions.
- Many APIs return borrowed internal pointers; callers must respect context lifetime.
- `mnt_context_read_mesgs()` loops on `read()` until `-1`; behavior depends on fd readiness/EOF.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/context.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/util-linux/libmount/src/context_mount.c -->
# File Research: sources/block-storage/util-linux/libmount/src/context_mount.c

Mount-specific high-level implementation for libmount contexts.

Key responsibilities:
- Evaluates mount permissions for root and restricted users.
- Normalizes/fixes mount option strings and user/group IDs.
- Applies helper command-line options to contexts.
- Executes `/sbin/mount.<type>` helpers.
- Performs mount attempts via hook-backed mount stages.
- Tries filesystem type lists and filesystem patterns.
- Prepares target paths and target prefixes.
- Implements `mnt_context_prepare_mount()`, `mnt_context_do_mount()`, `mnt_context_finalize_mount()`, and `mnt_context_mount()`.
- Implements mount-all and remount-all iteration helpers.
- Maps mount failures into mount-compatible exit codes/messages.
- Includes `TEST_PROGRAM` tests for permissions and option fixing.

Important behavior:
- Preparation order is fstab apply, flag merge, FS/option-list sync, permission evaluation, option fixing, source prep, fstype guess, target prep, helper discovery, only-once check, and prep hooks.
- `mnt_context_mount()` retries read-only on EROFS/EACCES/write-protected cases unless explicit RW/remount/bind forbids it.
- EROFS regular files can be retried with loop device setup after ENOTBLK.
- Helper execution drops permissions, switches to the original namespace, passes source/target/options/type/namespace, and records helper status.
- Mount-all ignores swap, root, `noauto`, nonmatching patterns, and already mounted filesystems.
- Remount-all iterates mountinfo and protects filter patterns from being interpreted as an ordinary `-t type`.

Dependencies:
- Depends on generic context APIs from `context.c`, hook stages, option-list APIs, table APIs, namespace support, util-linux string helpers, and Linux mount syscalls/constants.

Notable risks:
- Return codes deliberately separate libmount errors, syscall errno, and helper status; callers must use status/excode helpers.
- Helper argument array has a fixed size and relies on exact option-count assumptions.
- Forked mount-all children exit with raw `rc`, which may be negative if not normalized by caller.
- Error messaging path is large and tightly coupled to syscall status, user flags, and context state.
<!-- END FILE RESEARCH: sources/block-storage/util-linux/libmount/src/context_mount.c -->