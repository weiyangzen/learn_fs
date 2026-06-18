# sources/distributed-fs/ceph-client/tools/include/nolibc/Makefile

## Purpose
Builds and exports nolibc headers as a standalone tools include component. It supports installing the header set, producing a combined `nolibc.h`, and validating architecture-specific compiler flags.

## APIs, Types, and Functions
Important variables are `srctree`, `ARCH`, `OUTPUT`, `architectures`, `arch_files`, `all_files`, and per-architecture `CFLAGS_*`. Targets include `all`, `headers`, `headers_standalone`, `headers_install`, `clean`, and generated standalone header fragments.

## Control Flow, State, and Persistence
Make control flow resolves the kernel source root, derives `ARCH` from `SUBARCH` when unset, builds file lists, concatenates headers through scripted preprocessing for standalone mode, and installs output under the selected include destination. State persists only in generated/installed header files under `OUTPUT` or the requested install directory.

## Dependencies and Integration
Depends on kernel build scripts such as `scripts/subarch.include`, standard Make functions, compiler support for architecture flags, and the complete nolibc header set. It is the packaging and developer-test entry point for the nolibc library embedded under `tools/include`.

## Risks and Test Signals
Risks include missing a new architecture header from `architectures`, stale per-arch CFLAGS, incorrect `srctree` inference when invoked from unusual directories, and generated standalone header drift. Test signals are `make -C tools/include/nolibc headers`, install-path checks, all listed architecture compile probes, and diffing generated standalone output after header edits.
