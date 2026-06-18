# Group Research: group_678_libblockdev_sources_virtualization_libblockdev_src_utils_module_c_so_d9d2fca79dd5

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/virtualization/libblockdev`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/utils/module.c -->
# File Research: sources/virtualization/libblockdev/src/utils/module.c

Implementation of libblockdev utility helpers for Linux kernel module discovery/loading/unloading and cached running-kernel version detection.

Key responsibilities:
- Defines `bd_utils_module_error_quark()` for the GLib error domain used by module and kernel-version helpers.
- Bridges libkmod logging into libblockdev logging through `utils_kmod_log_redirect()` and `set_kmod_logging()`, using `LOG_DEBUG` in debug builds and `LOG_INFO` otherwise.
- Implements `bd_utils_have_kernel_module()`, which uses `kmod_module_new_from_lookup()` so aliases are considered, then treats a module as available if it has a filesystem path or is reported as `KMOD_MODULE_BUILTIN`.
- Implements `bd_utils_load_kernel_module()`, which resolves a module by name, rejects missing module paths with `BD_UTILS_MODULE_ERROR_NOEXIST`, then calls `kmod_module_probe_insert_module()` with `KMOD_PROBE_FAIL_ON_LOADED`.
- Implements `bd_utils_unload_kernel_module()`, which enumerates loaded modules, finds an exact module-name match, and calls `kmod_module_remove_module()`.
- Implements `bd_utils_get_linux_version()` and `bd_utils_check_linux_version()` around a process-global cached `BDUtilsLinuxVersion` populated from `uname(2)`.

Dependencies and integration:
- Depends on GLib, libkmod, syslog priority constants, POSIX locale APIs, and `uname(2)`.
- Includes local `module.h`, `exec.h`, and `logging.h`; only `module.h` supplies the public declarations used here.
- Built into `libbd_utils.la` by `src/utils/Makefile.am` and linked with `$(KMOD_LIBS)`.
- The main in-tree caller of `bd_utils_have_kernel_module()` is `src/plugins/check_deps.c`, where failed checks are folded into plugin dependency availability bitmaps.
- Exported API symbols are listed in `docs/libblockdev-sections.txt`.

Implementation notes:
- Kmod contexts are created with a null config pointer array, so these helpers avoid loading libkmod configuration snippets from an explicit caller-supplied configuration.
- Error text uses `strerror_l()` with a freshly created C locale to make system error strings locale-stable.
- `bd_utils_have_kernel_module()` returns `FALSE` with no `GError` when lookup succeeds but yields no module list; callers distinguish this from operational lookup failures.
- The load helper treats already-loaded modules as a failure because `KMOD_PROBE_FAIL_ON_LOADED` is intentionally used for backward-compatible behavior.
- The unload helper only attempts removal after finding the module among currently loaded modules; an unloaded or unknown module produces `BD_UTILS_MODULE_ERROR_NOEXIST`.
- Linux version detection validates `buf.sysname` against `Linux`, parses up to `major.minor.micro` from `buf.release`, and leaves missing minor/micro components as zero because the cached struct is zeroed before `sscanf()`.
- `bd_utils_check_linux_version()` serializes access with `G_LOCK`, lazily initializes the cache if needed, and returns the first nonzero difference among major, minor, and micro.

Notable risks:
- The kmod log prefix is spelled `[libmkod]`, which looks like a typo but may be visible in logs.
- `newlocale()` return values are not checked before use with `strerror_l()`; allocation failure would make error formatting fragile.
- `bd_utils_check_linux_version()` ignores initialization failure because it calls `_get_linux_version(FALSE, NULL)` and then compares the zeroed cached struct if detection failed.
- The module loading path rejects modules without a module file path, so built-in modules are "available" to `bd_utils_have_kernel_module()` but not loadable through `bd_utils_load_kernel_module()`.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/utils/module.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/utils/module.h -->
# File Research: sources/virtualization/libblockdev/src/utils/module.h

Public libblockdev utility header for kernel module helper errors, module management entry points, and Linux kernel version comparison.

Key responsibilities:
- Declares `bd_utils_module_error_quark()` and the `BD_UTILS_MODULE_ERROR` domain macro.
- Defines `BDUtilsModuleError` values for kmod initialization failure, generic module operation failure, missing module state, dependency-check aggregation failure, and invalid platform.
- Defines `BDUtilsLinuxVersion` as a simple `guint` triplet of major, minor, and micro kernel release components.
- Declares public helpers to check for a module, load a module with optional options, unload a module, get the cached Linux version, and compare the running kernel against a minimum version.

Dependencies and integration:
- Includes GLib for `GQuark`, `gboolean`, `gchar`, `GError`, `guint`, and `gint`.
- Installed as a public header by `src/utils/Makefile.am` under `$(includedir)/blockdev`.
- Included by the umbrella `src/utils/utils.h`, making this API visible to consumers that include `<blockdev/utils.h>`.
- Its symbols are documented/exported through `docs/libblockdev-sections.txt`.

Notable risks:
- `BD_UTILS_MODULE_ERROR_MODULE_CHECK_ERROR` is not raised by `module.c` directly; it is used by higher-level dependency checking in `src/plugins/check_deps.c`, so consumers need to treat the enum as shared across utility and plugin dependency layers.
- `BDUtilsLinuxVersion *` returned by the implementation is library-owned static storage; callers must not free or mutate it even though the struct type itself is not const-qualified in the API.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/utils/module.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/utils/sizes.h -->
# File Research: sources/virtualization/libblockdev/src/utils/sizes.h

Public convenience header defining binary and decimal byte-size suffix macros for readable storage constants.

Key responsibilities:
- Defines binary suffixes `KIBIBYTE` through `EXBIBYTE` as chained `*1024ULL` macro fragments.
- Provides short IEC aliases `KiB`, `MiB`, `GiB`, `TiB`, `PiB`, and `EiB`.
- Defines decimal suffixes `KILOBYTE` through `EXABYTE` as chained `*1000ULL` macro fragments.
- Provides short SI aliases `KB`, `MB`, `GB`, `TB`, `PB`, and `EB`.

Dependencies and integration:
- Includes GLib, though this header only defines macros and does not use GLib types directly.
- Installed as a public header by `src/utils/Makefile.am` and included by the umbrella `src/utils/utils.h`.
- Used throughout libblockdev plugins to keep storage constants readable, for example filesystem feature limits in `src/plugins/fs/generic.c`, LVM limits in `src/plugins/lvm/lvm-common.c`, and MD RAID defaults in `src/plugins/mdraid.h`.
- Size symbols are included in `docs/libblockdev-sections.txt`, so they are part of the public documentation surface.

Implementation notes:
- The macros are intended to be used as suffix-like fragments, for example `(4 MiB)` expands to `(4 *1024ULL *1024ULL)`.
- The chained definitions make every expanded result an unsigned long long expression, which is useful for large storage constants up to EiB/EB scale.

Notable risks:
- These are not function-like or parenthesized value macros; using them without a left-hand numeric operand is invalid, and using them inside more complex macro expressions requires normal C precedence care.
- Short names such as `KB`, `MB`, and `GB` are broad public macros and can collide with other headers or application code.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/utils/sizes.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/libblockdev/src/utils/utils.h -->
# File Research: sources/virtualization/libblockdev/src/utils/utils.h

Umbrella public header for libblockdev utility APIs used by the core library, plugins, and external consumers.

Key responsibilities:
- Includes the utility subheaders for size constants, process execution helpers, extra argument handling, device helpers, kernel module helpers, D-Bus helpers, and logging.
- Provides the GTK-Doc section block describing the utilities library and establishing `utils.h` as the public include.
- Uses a simple include guard `BD_UTILS`.

Dependencies and integration:
- Pulls in `sizes.h`, `exec.h`, `extra_arg.h`, `dev_utils.h`, `module.h`, `dbus.h`, and `logging.h`.
- Installed by `src/utils/Makefile.am` as `<blockdev/utils.h>`.
- Used by plugin code such as `src/plugins/check_deps.c` and `src/plugins/mdraid.h` to access shared utility APIs and size macros through a single include.
- Listed in package metadata and documentation as the main utility include.

Notable risks:
- Because this is an umbrella header, every consumer receives all included utility headers and their public macros; this increases namespace exposure, especially from `sizes.h`.
- Include-order changes here can affect downstream consumers that rely on transitive declarations from `<blockdev/utils.h>`.
<!-- END FILE RESEARCH: sources/virtualization/libblockdev/src/utils/utils.h -->