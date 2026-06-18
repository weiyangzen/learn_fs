# sources/distributed-fs/glusterfs/xlators/mount/Makefile.am

## Purpose

This Automake file is the top-level build dispatcher for mount translators. It conditionally enters the FUSE client subtree through `SUBDIRS = @FUSE_CLIENT_SUBDIR@`, allowing configure-time feature detection to include or omit FUSE-related build products.

## Important Build Variables

- `SUBDIRS` is substituted by configure as `@FUSE_CLIENT_SUBDIR@`. When FUSE client support is enabled it is expected to name the `fuse` subdirectory; when disabled it can be empty.
- `CLEANFILES` is explicitly present but empty.

## Control Flow and Integration

Automake recursively descends into whatever configure substitutes into `FUSE_CLIENT_SUBDIR`. This makes the mount translator subtree depend on configure results rather than hard-coding FUSE on all platforms. The next-level file is `xlators/mount/fuse/Makefile.am`, which then descends into `src` and `utils`.

## State and Persistence Behavior

There is no runtime state or persisted data. The only state is generated build-system state from configure and Automake. A wrong substitution changes which subdirectories are built and packaged.

## Dependencies

The file depends on the Autotools configure layer defining `FUSE_CLIENT_SUBDIR`. It indirectly depends on the FUSE source subtree only when that variable includes it.

## Risks and Edge Cases

- If configure enables FUSE but substitutes a missing or misspelled subdirectory, recursive make fails at this level.
- If configure disables FUSE unexpectedly, the mount translator library and utilities are not built, which may produce a Gluster build without the normal FUSE client path.
- Empty `CLEANFILES` is harmless but provides no local cleanup behavior.

## Test Signals

Build tests should run configure with FUSE enabled and disabled, then verify recursive make enters or skips `xlators/mount/fuse` as expected. Distribution tests should ensure the conditional subtree is still included in release tarballs when needed.
