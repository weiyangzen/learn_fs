# sources/distributed-fs/ceph-client/tools/tracing/rtla/Makefile

## Purpose
This Makefile builds the `rtla` realtime Linux analysis tool, optional BPF skeletons/actions, unit tests, documentation, and installation artifacts through the Linux tools build system.

## Important APIs, Types, and Functions
It derives `srctree`, normalizes `OUTPUT`, defines `RTLA`, `RTLA_IN`, `VERSION`, `DOCSRC`, feature probes for tracefs/traceevent/cpupower/check/libbpf/clang-bpf-co-re/bpftool-skeletons, and includes `Makefile.rtla` plus unit-test definitions. BPF-specific targets compile `src/timerlat.bpf.c` and example/test BPF objects with clang and generate `src/timerlat.skel.h` with bpftool when `BUILD_BPF_SKEL=1`; otherwise they create a disabled skeleton header or skip objects.

## Control Flow
Normal `all` builds `rtla`. Feature detection and `Makefile.config` are included for build/check goals but skipped for `clean`, `install`, tarball, and documentation-only goals. `$(RTLA_IN)` depends on `fixdep`, `FORCE`, and the generated skeleton header, then invokes `make $(build)=rtla`. Link targets produce dynamic and optional static binaries. `check` runs Perl `prove` tests with `RTLA` and `BPFTOOL` variables. `examples` builds the BPF action example.

## State and Persistence
Build output is placed in `OUTPUT` or the source directory. Generated artifacts include `src/timerlat.bpf.o`, `src/timerlat.skel.h`, BPF example/test objects, `rtla`, `rtla-static`, feature directories, and unit-test outputs. Install/doc targets are defined by included files.

## Dependencies and Integration Points
The Makefile integrates with the kernel tools build framework, libtraceevent, libtracefs, optional libcpupower, libcheck, libbpf, clang, bpftool, BPF CO-RE support, and RTLA documentation/test subtrees.

## Risks and Edge Cases
When BPF skeleton support is disabled, a stub skeleton header is generated, so C code must compile fallback paths cleanly. Cleaning removes generated skeletons and BPF objects in the source tree. Static linking depends on all external libraries having static forms. Feature detection skips some targets, so invoking install/check without prior build or dependencies can fail late.

## Test Signals
Run builds with and without BPF support, `make static`, `make examples`, `make check`, `make clean`, and out-of-tree `O=` builds. Verify generated skeleton handling and fallback compilation.
