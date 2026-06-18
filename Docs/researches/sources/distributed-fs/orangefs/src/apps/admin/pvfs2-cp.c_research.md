# sources/distributed-fs/orangefs/src/apps/admin/pvfs2-cp.c

## Purpose
`pvfs2-cp.c` copies a single file between Unix and OrangeFS endpoints in any direction, replacing older import/export tools. It detects endpoint type, opens or creates the destination, streams data through a fixed-size buffer, optionally reports throughput, and preserves permissions/attributes when possible.

## Important APIs, Types, And Functions
Key types are `struct options`, `enum object_type`, `enum open_type`, `pvfs2_file_object`, `unix_file_object`, and `file_object`. Key functions are `main`, `parse_args`, `resolve_filename`, `generic_open`, `generic_read`, `generic_write`, `generic_cleanup`, `make_attribs`, `convert_pvfs2_perms_to_mode`, `Wtime`, and `print_timings`. PVFS dependencies include hints (`PVFS_hint_import_env`, `PVFS_hint_free`), sysint initialization, credentials, `PVFS_sys_lookup`, `PVFS_sys_ref_lookup`, `PVFS_sys_getattr`, `PVFS_sys_create`, `PVFS_sys_read`, `PVFS_sys_write`, `PVFS_sys_setattr`, request descriptors, distributions, and path helpers.

## Control Flow
`parse_args` reads optional timing, stripe size, datafile count, and buffer size, then requires source and destination. `main` imports hints, initializes PVFS, resolves both endpoints by trying `PVFS_util_resolve`, opens the source, opens/creates the destination, allocates the buffer, and loops `generic_read`/`generic_write` at monotonically increasing offsets until EOF or error. `generic_open` handles Unix directories by appending the source basename, refuses directory sources, refuses overwriting existing PVFS destinations, creates PVFS destinations with temporary mode 0777, and optionally sets a `simple_stripe` distribution strip size. `generic_cleanup` closes Unix descriptors and preserves permissions for PVFS-to-Unix, Unix-to-PVFS, Unix-to-Unix, and PVFS-to-PVFS copies.

## State And Persistence
Persistent effects are destination file creation/truncation and attribute changes. Runtime state includes endpoint descriptors/refs, copied attributes, credentials, PVFS hints, request descriptors, and the transfer buffer. For PVFS destinations, the file may exist with permissive attrs until cleanup restores source-derived attributes.

## Dependencies And Integration Points
The utility is an admin build target and a user-facing sysint client. It integrates local POSIX file APIs with OrangeFS metadata/data APIs, distribution selection, environment hints, and internal path utilities.

## Risks And Test Signals
Risks include no retry loop for short POSIX writes, return type `size_t` carrying negative PVFS errors, missing `PVFS_Request_free` on PVFS read/write error paths, possible basename/path concatenation overflow, refusal to overwrite PVFS targets but truncation of Unix targets, and created PVFS files left behind on failed transfers. Test signals should cover all four copy directions, directory destinations, existing PVFS target refusal, large files with partial read/write conditions, attribute preservation, strip size/datafile options, and cleanup after injected write failures.
