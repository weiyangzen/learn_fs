<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/mkspec -->
# sources/distributed-fs/ceph-client/scripts/package/mkspec

## Purpose

`mkspec` generates an RPM spec file for packaging the current kernel build.

## Important APIs, Types, and Functions

It derives package name, version, release, architecture, dependencies, config flags, and install script sections from Kbuild environment and kernel release metadata.

## Control Flow

The script prints a complete spec to stdout. The spec defines build requirements, package descriptions, `%prep`, `%build`, `%install`, file lists, and optional subpackages such as headers/devel/debug depending on configuration and environment.

## State and Persistence Behavior

The script itself is read-only; callers redirect stdout to a `.spec` file consumed by rpmbuild.

## Dependencies and Integration Points

It depends on shell, rpm macro conventions, Kbuild build/install targets, and distro package expectations. It integrates with `make rpm-pkg` or related package targets.

## Risks and Edge Cases

Spec generation must match current RPM macro behavior and kernel install paths. Architecture naming, debug package handling, and module/header package splits can vary by distro. Environment-sensitive version strings affect reproducibility.

## Test Signals

Generate and build RPMs with and without modules, headers, debug info, and cross-architecture settings. Inspect file lists, dependency metadata, and install/remove script behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/package/mkspec -->
