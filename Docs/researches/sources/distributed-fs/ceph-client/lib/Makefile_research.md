<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/Makefile -->
# sources/distributed-fs/ceph-client/lib/Makefile

## Purpose
Defines the Kbuild object graph for the kernel generic library directory. It selects always-built helper libraries, conditionally built test modules, architecture fallback helpers, compression subdirectories, sanitizer instrumentation controls, generated sources, and bootconfig embedding artifacts.

## APIs, Types, and Functions
The "API" is Kbuild variables and targets: `lib-y`, `obj-y`, `obj-$(CONFIG_...)`, `lib-$(CONFIG_...)`, per-object flags such as `CFLAGS_string.o`, sanitizer disables like `KASAN_SANITIZE_stackdepot.o := n`, generated target rules for `default.bconf` and `oid_registry_data.c`, and recursion into subdirectories such as `842/`, `zlib_*`, `lzo/`, `lz4/`, `zstd/`, `xz/`, `raid6/`, `kunit/`, and `tests/`.

## Control Flow, State, and Persistence
Kbuild expands this Makefile after configuration. Core objects such as `argv_split.o`, `bcd.o`, `bitmap.o`, `bitmap-str.o`, and `base64.o` are always included. Feature-selected objects include `alloc_tag.o`, `assoc_array.o`, `atomic64.o`, `asn1_decoder.o`, `asn1_encoder.o`, `bch.o`, `audit.o`, `bitrev.o`, `ashldi3.o`, and `ashrdi3.o`. Generated artifacts are produced from configured inputs, for example embedded bootconfig data from `CONFIG_BOOT_CONFIG_EMBED_FILE`. Runtime persistence is not in this file, but build inclusion determines which exported symbols and initcalls exist.

## Dependencies and Integration
Depends on Kbuild, `lib/Kconfig`, compiler feature variables, sanitizer/profiler infrastructure, and generated-file helper macros such as `filechk`. It integrates nearly every kernel subsystem with shared library code and test modules, so object names and config symbols must remain aligned with declarations in Kconfig and exported symbols in source.

## Risks and Test Signals
Risks include object duplication between `lib-y` and `obj-y`, missing sanitizer opt-outs for low-level code, generated target dependency drift, and config symbols selecting source files without required dependencies. Test signals include `make lib/` under multiple configs, `randconfig` link tests, bootconfig embedding builds, OID registry generation, sanitizer builds, and module builds for conditional test objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/Makefile -->
