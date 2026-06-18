# sources/distributed-fs/ceph-client/tools/perf/util/PERF-VERSION-GEN

## Purpose

`PERF-VERSION-GEN` is a shell script that generates `PERF-VERSION-FILE`, defining the `PERF_VERSION` macro used by perf builds.

## Important APIs, Types, and Functions

It accepts an optional output directory prefix, computes `GVF=${OUTPUT}PERF-VERSION-FILE`, obtains a kernel version tag via `make -sC ../.. kernelversion`, optionally appends an abbreviated git commit suffix, strips a leading `v`, compares against the existing file, and rewrites only on changes.

## Control Flow and State

When inside a git repository, it uses the kernel makefile version and `git log -1 --abbrev=12`; outside git, it can reuse an existing top-level `PERF-VERSION-FILE`. If `TAG` is still empty it falls back to kernelversion. Persistent state is the generated file content.

## Dependencies and Integration Points

It depends on POSIX shell, make, git when available, sed, expr, cut, and the top-level kernel makefile. It is invoked from perf's build system.

## Risks and Test Signals

Risks include relative-path assumptions, non-git source trees, missing make/git, and unnecessary rebuilds if comparison is wrong. Tests should run in git, exported tarball, with output directory set, and with unchanged/changing version strings.
