# sources/distributed-fs/ceph-client/fs/udf/Kconfig

## Purpose

`sources/distributed-fs/ceph-client/fs/udf/Kconfig` defines the kernel configuration switch for the UDF filesystem. The source was read as a complete 19-line Kconfig file.

## Important APIs, Types, and Functions

The sole symbol is `CONFIG_UDF_FS`, a tristate option labelled "UDF file system support". It selects `BUFFER_HEAD`, `CRC_ITU_T`, `NLS`, and `LEGACY_DIRECT_IO`.

## Control Flow

There is no runtime control flow. Kconfig dependency resolution determines whether the UDF implementation is compiled built-in, as a module named `udf`, or not at all. The selected symbols enable buffer-head based block I/O, CRC helpers, native language support for filenames, and the direct-I/O path used by UDF file operations.

## State and Persistence Behavior

No runtime state or persistent data is owned by this file. It controls build inclusion and the availability of dependencies required to read and write UDF media structures.

## Dependencies and Integration Points

This file integrates with the top-level filesystem Kconfig tree and the UDF `Makefile`. Its help text points users to `Documentation/filesystems/udf.rst` and describes optical and removable-disk use cases.

## Risks and Edge Cases

Dropping any selected dependency can create compile failures or silent feature breakage in UDF sources. Changing tristate semantics affects module availability and init/link coverage. The help text is user-facing and should remain aligned with current UDF capabilities.

## Test Signals

Build tests should cover `CONFIG_UDF_FS=y`, `m`, and `n`, plus dependency resolution in minimal configs. Runtime smoke tests should mount read-only optical images and writable removable-media images when the module or built-in filesystem is enabled.
