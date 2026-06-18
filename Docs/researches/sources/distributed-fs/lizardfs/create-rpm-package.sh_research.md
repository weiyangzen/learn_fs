# sources/distributed-fs/lizardfs/create-rpm-package.sh

## Purpose
This script builds RPM and source RPM packages for supported Red Hat/Fedora-like distributions.

## Important APIs, Types, and Functions
It detects distro family by numeric extraction from `/etc/redhat-release`, maps to `el7`, `el8`, `fc34`, or `fc35`, creates an rpmbuild tree under `/tmp/lizardfs_rpm_working_directory`, derives version from `rpm/lizardfs.spec`, creates a Git archive source tarball, substitutes `@DISTRO@` into the spec, and runs `rpmbuild -ba`.

## Control Flow and State
The script validates the distro, removes and recreates a fixed working tree, archives `HEAD` with prefix `lizardfs-$version/`, writes the spec into `SPECS`, builds binary and source packages, copies generated packages to the original directory, and removes the working tree.

## Dependencies and Integration Points
It depends on Git, RPM build tools, `/etc/redhat-release`, `gzip`, `awk`, and `rpm/lizardfs.spec`. CMake/build behavior is delegated to the spec.

## Risks and Edge Cases
The distro detection is narrow and may reject newer releases. The working directory is fixed and removed recursively. It packages exactly `HEAD`, so uncommitted changes are excluded. Only `RPMS/x86_64` is copied, so other architectures are not handled.

## Test Signals
Successful `.rpm` and `.src.rpm` artifacts in the output directory are the main signal. Unsupported distro or rpmbuild failures stop execution.
