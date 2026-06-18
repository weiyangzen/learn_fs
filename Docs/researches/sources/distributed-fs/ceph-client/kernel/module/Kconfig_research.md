# sources/distributed-fs/ceph-client/kernel/module/Kconfig

## Purpose
Defines the kernel configuration surface for loadable module support. It enables the module subsystem itself and selects optional features for debugging, unloading, symbol versioning, signatures, compression/decompression, namespace import enforcement, modprobe path configuration, exported symbol trimming, and fast module address lookup.

## Important APIs, Types, And Functions
This is Kconfig rather than C code. Symbols include `MODULES`, `MODULE_DEBUGFS`, `MODULE_DEBUG`, `MODULE_STATS`, `MODULE_DEBUG_AUTOLOAD_DUPS`, `MODULE_FORCE_LOAD`, `MODULE_UNLOAD`, `MODULE_FORCE_UNLOAD`, `MODULE_UNLOAD_TAINT_TRACKING`, `MODVERSIONS`, `GENKSYMS`, `GENDWARFKSYMS`, `EXTENDED_MODVERSIONS`, `BASIC_MODVERSIONS`, `MODULE_SIG`, `MODULE_SIG_FORCE`, `MODULE_SIG_ALL`, `MODULE_COMPRESS`, `MODULE_DECOMPRESS`, `MODULE_ALLOW_MISSING_NAMESPACE_IMPORTS`, `MODPROBE_PATH`, `TRIM_UNUSED_KSYMS`, and `MODULES_TREE_LOOKUP`.

## Control Flow
At configuration time, `MODULES` gates the rest of the menu. Nested choices select versioning implementation, signature hash, and compression algorithm. Several symbols select support libraries, for example `MODULE_SIG` selects `MODULE_SIG_FORMAT`, compression selects crypto/decompression code, and module tree lookup is enabled when perf, tracing, or CFI need frequent lookups.

## State And Persistence
The file persists build-time policy in `.config`. Runtime effects include whether syscalls are available, whether module unload paths exist, whether signatures are enforced, and what `/proc/sys/kernel/modprobe` defaults to.

## Dependencies And Integration Points
Integrates Kbuild, modpost, signing tools, OpenSSL requirements, crypto libraries, debugfs, sysfs/procfs consumers, userspace `modprobe`, and architecture capabilities such as `HAVE_ASM_MODVERSIONS`.

## Risks And Edge Cases
Incompatible options can change ABI expectations: forced loads taint kernels, strict signature enforcement rejects unsigned modules, compression requires matching userspace and in-kernel support, and extended modversions are important for long names and Rust support. Missing namespace imports can be fatal unless explicitly relaxed.

## Test Signals
Signals are Kconfig dependency resolution, allmodconfig/defconfig builds, module load/unload tests under each feature set, signature enforcement tests, compressed module loading, and debugfs/procfs/sysfs presence when corresponding options are enabled.
