<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop/Makefile

## Purpose

This Makefile builds and installs the pthread/inline-assembly `thread_loop` CoreSight workload.

## Research

It includes `../Makefile.miniconfig`, sets `BIN=thread_loop` and `LIB=-pthread`, and compiles `thread_loop.c` only when CoreSight is enabled on arm64. Installation mirrors other CoreSight workloads by placing the binary in a named perf exec test subdirectory, and `clean` removes the executable. State is the build artifact and optional installed binary. Dependencies are arm64 compiler support, pthreads, perf make variables, and CoreSight configuration. Integration supplies the workload for TID verification scripts. Risks are skipped/no-op builds outside arm64 CoreSight, pthread link issues, and missing install causing shell wrapper skip. Test signal is an executable binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/thread_loop/Makefile -->
