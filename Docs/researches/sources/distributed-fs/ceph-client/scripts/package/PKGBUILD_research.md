<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/PKGBUILD -->
# sources/distributed-fs/ceph-client/scripts/package/PKGBUILD

## Purpose

`PKGBUILD` packages a built kernel for Arch Linux-style package management, producing the main kernel package and optional headers, API headers, and debug packages.

## Important APIs, Types, and Functions

Package functions include `_prologue()`, `build()`, `_package()`, `_package-headers()`, `_package-api-headers()`, and debug-package handling. Variables derive `pkgbase`, `pkgname`, `pkgver`, `pkgrel`, `arch`, dependencies, and extra package selection from Kbuild and pacman environment variables.

## Control Flow

`build()` invokes Kbuild with fixed `KERNELRELEASE` and build revision. The main package installs the kernel image, pkgbase marker, modules, and optional DTBs. The headers package calls `install-extmod-build`, adds `System.map` and `.config`, and creates `/usr/src` links. API headers run `headers_install`; debug packaging extracts debug info and build-id links.

## State and Persistence Behavior

It writes into makepkg's `pkgdir` package roots, installing files under `/usr/lib/modules`, `/usr/src`, `/usr/include`, boot/module debug paths, and package metadata.

## Dependencies and Integration Points

It depends on makepkg, Kbuild, `install-extmod-build`, `modules_install`, `dtbs_install`, `headers_install`, objcopy/readelf for debug packaging, and Arch packaging conventions.

## Risks and Edge Cases

MAKEFLAGS must be restored from Kbuild to avoid makepkg overrides. Package split behavior depends on config and environment variables. Stale images or missing DTB directories can produce incomplete packages. Debug extraction assumes module paths and build IDs are valid.

## Test Signals

Run `make pacman-pkg` variants with and without modules, DTBs, extra packages, and debug package enabled. Inspect package contents, symlinks, module dependency generation, and installability with pacman.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/PKGBUILD -->
