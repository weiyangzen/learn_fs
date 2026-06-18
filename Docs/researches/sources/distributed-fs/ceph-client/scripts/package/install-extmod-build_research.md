<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/install-extmod-build -->
# sources/distributed-fs/ceph-client/scripts/package/install-extmod-build

## Purpose

`install-extmod-build` installs the subset of a kernel build tree required to build external modules against packaged headers.

## Important APIs, Types, and Functions

The script accepts an installation directory and copies/synchronizes Makefiles, generated headers, scripts, tools needed by external module builds, `Module.symvers` when present, and architecture-specific include/build files.

## Control Flow

It prepares the destination, creates required directory structure, copies core Kbuild metadata and generated config headers, installs module build scripts, and prunes unnecessary files so the result is suitable for `/lib/modules/<release>/build` or distro header packages.

## State and Persistence Behavior

It writes into the destination directory supplied by packaging scripts. It does not modify the source tree.

## Dependencies and Integration Points

It depends on rsync/cp/find-style tools, Kbuild output layout, generated headers, `scripts/mod/modpost`, and packaging callers such as Arch `PKGBUILD` and Debian `builddeb`.

## Risks and Edge Cases

Omitting generated files breaks external module builds; copying too much bloats header packages. Cross-compile and separate output-tree layouts require source and object paths to be handled carefully. Stale build output can leak into packages.

## Test Signals

Install headers, then build simple and modversioned external modules against the result. Test in-tree and `O=` builds, cross-compiles, missing `Module.symvers`, and clean package-content checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/install-extmod-build -->
