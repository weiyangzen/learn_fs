<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/mkdebian -->
# sources/distributed-fs/ceph-client/scripts/package/mkdebian

## Purpose

`mkdebian` generates a Debian packaging directory for the current kernel build. It creates control metadata, changelog, rules, source-package patches, and package stanzas for image, headers, libc headers, and optional debug packages.

## Important APIs, Types, and Functions

Helpers are `is_enabled()`, `if_enabled_echo()`, `set_debarch()`, and `gen_source()`. Important variables include maintainer identity, package version, source name, image package name, Debian architecture, host GNU tuple, distribution, and build profiles.

## Control Flow

The script removes and recreates `debian/`, derives maintainer and package version, optionally creates source package metadata and quilt patches, maps `UTS_MACHINE` and config flags to a Debian architecture, detects the changelog distribution, writes `debian/arch`, `changelog`, `control`, rules, and support files. It uses package profiles and config flags to include or omit package variants.

## State and Persistence Behavior

It persistently replaces the `debian/` directory and may write patches under `debian/patches`. Source generation includes `.config` and local diffs as quilt patches.

## Dependencies and Integration Points

It depends on shell, dpkg tools, `lsb_release`, Kbuild config/output files, `scripts/setlocalversion`, `scripts/build-version`, `gen-diff-patch`, and Debian package conventions.

## Risks and Edge Cases

Architecture mapping can fall back to host architecture, which is risky for unsupported targets. Replacing `debian/` discards local packaging edits. Maintainer identity and distribution are environment-sensitive. Source patches depend on current uncommitted tree state.

## Test Signals

Run for multiple architectures, `ARCH=um`, source and binary package modes, custom `KDEB_*` variables, no `lsb_release`, and unsupported architecture fallback. Validate `dpkg-buildpackage` succeeds from generated metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/mkdebian -->
