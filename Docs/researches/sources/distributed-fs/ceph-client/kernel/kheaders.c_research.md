# sources/distributed-fs/ceph-client/kernel/kheaders.c

## Purpose
`kheaders.c` exposes the compressed kernel header archive used for building tracing/eBPF programs through a sysfs binary attribute.

## Important APIs, Types, And Functions
Inline assembly emits `kernel_headers_data` and `kernel_headers_data_end` in `.rodata` by including `kernel/kheaders_data.tar.xz`. `kheaders_attr` is a `struct bin_attribute` created with `__BIN_ATTR_SIMPLE_RO(kheaders.tar.xz, 0444)`. `ikheaders_init()` sets the binary attribute's private pointer and size, then calls `sysfs_create_bin_file(kernel_kobj, ...)`; `ikheaders_cleanup()` removes it.

## Control Flow
At module/init time, the archive symbols are already present in read-only data. The init function publishes the archive under `/sys/kernel/kheaders.tar.xz`; module exit removes the sysfs file.

## State And Persistence
The archive is immutable kernel/module rodata. The only runtime state is the sysfs bin attribute metadata. It persists while the module/built-in feature is active.

## Dependencies And Integration Points
The file depends on `kernel_kobj` from `ksysfs.c`, sysfs binary attributes, module init/exit, and the build-generated `kernel/kheaders_data.tar.xz` artifact.

## Risks And Edge Cases
Failure to initialize `/sys/kernel` first would make `kernel_kobj` invalid. Missing or stale generated header archives break build/reproducibility expectations. The archive is world-readable, so content should be limited to build headers and not secrets.

## Test Signals
Signals are successful creation/removal of `/sys/kernel/kheaders.tar.xz`, correct file size matching linker symbols, readable xz tar content, module load/unload behavior, and build coverage when kernel headers are generated.
