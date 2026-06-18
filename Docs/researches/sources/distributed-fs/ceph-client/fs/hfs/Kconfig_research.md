# sources/distributed-fs/ceph-client/fs/hfs/Kconfig

## Purpose
This Kconfig file declares build options for the Linux HFS filesystem and its KUnit tests.

## Important Options
`HFS_FS` is a tristate option named "Apple Macintosh file system support". It depends on `BLOCK` and selects `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`. Its help text describes read-write access to Macintosh-formatted media and the module name `hfs`.

`HFS_KUNIT_TEST` is a tristate option for HFS filesystem KUnit tests. It depends on `HFS_FS && KUNIT`, defaults to `KUNIT_ALL_TESTS`, and is hidden when all KUnit tests are enabled.

## Control Flow And State
There is no runtime control flow here. The configuration controls whether HFS code is built in, built as a module, or omitted, and whether KUnit test objects are built.

## Dependencies And Integration Points
The selected symbols ensure the HFS implementation has block-device support, buffer heads, native language support, and legacy direct I/O support. The KUnit option integrates with the kernel KUnit harness and the HFS Makefile.

## Risks And Test Signals
Risks include stale dependency/selects when HFS internals change or tests building without required helpers. Signals are kernel configuration dependency resolution, module build success, and KUnit TAP output when `HFS_KUNIT_TEST` is enabled.
