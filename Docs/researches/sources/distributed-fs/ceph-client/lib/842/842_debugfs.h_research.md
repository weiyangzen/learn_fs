<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/842/842_debugfs.h -->
# sources/distributed-fs/ceph-client/lib/842/842_debugfs.h

## Purpose
Provides optional debugfs instrumentation shared by the 842 compressor and decompressor modules. It exposes per-template counters when the module parameter `template_counts` is enabled.

## APIs, Types, and Functions
This header defines the static module parameter `sw842_template_counts`, atomic counters for normal templates plus repeat, zeros, short-data, and end templates, the debugfs root dentry, and two helpers: `sw842_debugfs_create()` and `sw842_debugfs_remove()`. There are no exported global functions because the header is included directly into each 842 module, making the state module-local.

## Control Flow, State, and Persistence
At module init, the compressor/decompressor call `sw842_debugfs_create()` only if `template_counts` is true. The helper checks `debugfs_initialized()`, creates a directory named by `MODULE_NAME`, and creates writable atomic files for each counter. At exit, `sw842_debugfs_remove()` recursively removes the tree. Counters persist only for the lifetime of the loaded module and are incremented by compression/decompression template paths.

## Dependencies and Integration
Depends on `linux/debugfs.h`, atomic debugfs helpers, `OPS_MAX`, `MODULE_NAME`, and module-parameter support from the including C file. Integration is intentionally header-local so both `842_compress.c` and `842_decompress.c` get independent counters and debugfs directories.

## Risks and Test Signals
Risks are duplicate static definitions if included incorrectly, debugfs root creation failures being non-fatal, and counter ABI changes affecting diagnostic scripts. Test signals include module load with `template_counts=0` and `1`, verifying created debugfs files match all template names, exercising compressor/decompressor paths and observing counters, and unloading modules to confirm recursive cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/842/842_debugfs.h -->
