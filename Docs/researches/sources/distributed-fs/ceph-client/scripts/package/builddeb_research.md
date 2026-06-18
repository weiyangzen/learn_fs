<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/builddeb -->
# sources/distributed-fs/ceph-client/scripts/package/builddeb

## Purpose

`builddeb` installs built kernel artifacts into Debian package staging directories for image, headers, libc headers, and debug packages.

## Important APIs, Types, and Functions

Helpers include `is_enabled()`, `if_enabled_echo()`, image-install logic, maintainer-script generation, `install_linux_image_dbg()`, `install_kernel_headers()`, and `install_libc_headers()`. It uses package name dispatch at the end.

## Control Flow

For image packages it installs modules, image files, config/System.map, DTBs, and maintainer scripts that run hook directories. Debug packages parse `modules.order`, extract debug info with objcopy, create build-id links, and install `vmlinux` symlinks. Header packages call `install-extmod-build`; libc headers call `headers_install` and move asm headers into the Debian multiarch include path.

## State and Persistence Behavior

It writes into `debian/<package>` staging roots, creates maintainer scripts under `DEBIAN`, package file trees under `/boot`, `/lib/modules`, `/usr/src`, `/usr/include`, and `/usr/lib/debug`.

## Dependencies and Integration Points

It depends on Kbuild variables, Debian packaging layout, `modules.order`, `READELF`, `OBJCOPY`, `run-parts`, `dpkg-architecture`-derived variables, and `install-extmod-build`.

## Risks and Edge Cases

Module debug extraction assumes uncompressed accessible `.ko` files and build IDs. Cross-compiles need correct `DEB_HOST_GNU_TYPE`. Hook scripts are generated dynamically and must be shell-safe. Missing modules or images can produce incomplete packages.

## Test Signals

Build Debian packages for image, debug, headers, and libc headers; inspect maintainer scripts, build-id links, module trees, DTBs, and multiarch header placement. Test no-modules and cross-compile configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/builddeb -->
