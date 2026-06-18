# sources/cloud-native/cri-o/hack/build-rpms.sh

## Purpose
Release helper that builds CRI-O RPM/SRPM artifacts and a local yum/dnf repository.

## Important APIs, Types, and Functions
Sources hack/lib/init.sh, requires rpmbuild and createrepo, calls RPM version helpers, rpmspec, dnf builddep, Go download, rpmbuild, make clean, and createrepo.

## Control Flow
Creates rpm temp SOURCES, archives repo plus CI data, optionally forces yum IPv4, installs builddeps/latest Go, runs rpmbuild with version/release/commit defines, moves artifacts to _output/local/releases/rpms, creates repo metadata and .repo files.

## State and Persistence
Writes rpm temp tree, _output release/RPM directories, .commit marker, repo metadata, and may edit /etc/yum.conf.

## Dependencies
Depends on RPM toolchain, dnf, curl, go.dev availability, spec file, Makefile clean, and hack/lib build helpers.

## Integration Points
Used by release/CI jobs to create local installable RPM repositories.

## Risks and Edge Cases
Network-dependent Go download, privileged host package changes, best-effort builddep, /etc/yum.conf mutation, and destructive make clean.

## Test Signals
Successful rpmbuild, RPM files, SRPM, createrepo metadata, and local-release.repo are output signals.
