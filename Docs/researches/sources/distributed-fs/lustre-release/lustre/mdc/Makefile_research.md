<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/Makefile -->
# sources/distributed-fs/lustre-release/lustre/mdc/Makefile

## Purpose
The MDC `Makefile` declares the Lustre Metadata Client kernel module object composition. It builds `mdc.o` from request, reintegration, procfs, library, lock, changelog, device, and batch metadata sources, with ACL support included conditionally.

## Important APIs, Types, And Functions
There are no C APIs here. Build variables are `obj-m`, `mdc-objs-y`, `mdc-objs-$(CONFIG_FS_POSIX_ACL)`, `mdc-objs`, and optional `GCOV_PROFILE`.

## Control Flow
Kbuild sees `obj-m += mdc.o`, expands `mdc-objs-y` into the module's component objects, appends `mdc_acl.o` when `CONFIG_FS_POSIX_ACL` is enabled, and assigns the final list to `mdc-objs`. If Lustre GCOV profiling is configured, it enables `GCOV_PROFILE := y` for this directory.

## State And Persistence
The file affects build-time module composition only. Its persistent output is the generated `mdc.o` kernel module and optional coverage instrumentation metadata.

## Dependencies And Integration Points
It ties together the MDC implementation files used by llite metadata operations, including `lproc_mdc.c`, `mdc_batch.c`, and optional `mdc_acl.c`. The conditional ACL object must match C preprocessor use of `CONFIG_FS_POSIX_ACL`.

## Risks And Edge Cases
Omitting an object breaks link-time symbol resolution for metadata operations or tunables. Enabling `mdc_acl.o` without POSIX ACL kernel support would fail compilation, while disabling it removes ACL unpacking support.

## Test Signals
Build with and without `CONFIG_FS_POSIX_ACL`, build with `CONFIG_GCOV_PROFILE_LUSTRE`, inspect `mdc.o` link inputs, and run metadata operations that exercise request, lock, changelog, batch, procfs, and ACL code paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdc/Makefile -->
