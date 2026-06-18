<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/unroll_loop_thread/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/unroll_loop_thread/Makefile

## Purpose

This Makefile builds and installs the `unroll_loop_thread` CoreSight workload.

## Research

It includes `../Makefile.miniconfig`, sets `BIN=unroll_loop_thread`, links with `-pthread`, and compiles only for CoreSight-enabled arm64 builds. Installation creates the named perf exec test directory and installs the binary; clean removes it. State is the build artifact and installed copy. Dependencies are a C compiler, pthreads, perf make install variables, and arm64 CoreSight gating. Integration supports `unroll_loop_thread_10.sh`, which records a large unrolled instruction stream. Risks are skipped builds outside the supported environment and compiler behavior changes affecting inline assembly expansion. Test signal is executable availability for the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/unroll_loop_thread/Makefile -->
