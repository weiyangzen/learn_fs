<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/842/Makefile -->
# sources/distributed-fs/ceph-client/lib/842/Makefile

## Purpose
Builds the 842 compression subdirectory objects according to kernel configuration.

## APIs, Types, and Functions
The file has two object rules: `obj-$(CONFIG_842_COMPRESS) += 842_compress.o` and `obj-$(CONFIG_842_DECOMPRESS) += 842_decompress.o`. It defines no source-level APIs.

## Control Flow, State, and Persistence
Kbuild includes this directory when the parent `lib/Makefile` adds `842/` for either 842 option. The rules independently compile the compressor and decompressor, allowing one direction to be enabled without the other. There is no runtime state.

## Dependencies and Integration
Depends on parent `lib/Makefile` recursion and `lib/Kconfig` symbols. Both selected objects depend on `842.h`; each object includes `842_debugfs.h` and gets its own module metadata.

## Risks and Test Signals
Risks are configuration skew where a consumer expects both compression and decompression but selects only one, or missing parent recursion rules preventing this Makefile from being reached. Test signals include build matrices for `CONFIG_842_COMPRESS=m/y`, `CONFIG_842_DECOMPRESS=m/y`, both enabled, and neither enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/842/Makefile -->
