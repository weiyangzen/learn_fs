<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/Makefile -->
# sources/distributed-fs/ceph-client/tools/lib/bpf/Makefile

## Purpose
This Makefile builds, checks, installs, and cleans libbpf from the kernel tools tree. It produces static and shared libraries, generated helper definitions, a pkg-config file, and installable public headers.

## Important APIs, types, and functions
Key outputs are `libbpf.a`, `libbpf.so.$(LIBBPF_VERSION)`, `libbpf.so` symlinks, `libbpf.pc`, and `bpf_helper_defs.h`. It derives `LIBBPF_VERSION` from `libbpf.map`, sets `LIBBPF_MAJOR_VERSION`/`MINOR_VERSION`, builds separate shared/static object directories, invokes `scripts/bpf_doc.py` for helper definitions, and verifies ABI/version consistency with `check_abi` and `check_version`.

## Control flow
`all` depends on `fixdep` and runs `all_cmd`. Shared and static combined objects are built through the tools build system with different `OUTPUT` directories and `SHLIB_FLAGS` for shared builds. The shared library links against `-lelf -lz` with a version script and creates soname symlinks. Install targets copy libraries, pkg-config metadata, source headers, and generated headers into `prefix`/`DESTDIR`.

## State and persistence behavior
Persistent build outputs live under `OUTPUT`: libraries, symlinks, generated header, pkg-config file, temporary ABI symbol lists, and object directories. Installation persists files under `$(prefix)/lib*`, `include/bpf`, and pkg-config directories.

## Dependencies and integration points
It depends on the Linux tools build system, architecture make fragments, `readelf`, `awk`, `grep`, `sort -V`, `scripts/bpf_doc.py`, libelf, zlib, and `libbpf.map`. It is shared by kernel selftests, perf, and external libbpf builds from the tools tree.

## Risks and edge cases
`-Werror` is unconditional in appended CFLAGS, so compiler drift can break builds. ABI checks depend on `readelf` output formats. Generated helper definitions depend on a synchronized `tools/include/uapi/linux/bpf.h`. Out-of-tree `srctree` detection is make-environment-sensitive.

## Test signals
Run `make -C tools/lib/bpf` for static/shared outputs, `make check` for ABI/version validation, install into a temporary `DESTDIR`, verify `pkg-config --cflags --libs` output, and build BPF selftests against the produced headers/library.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/lib/bpf/Makefile -->
