<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/memcpy_thread/Makefile -->
# sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/memcpy_thread/Makefile

## Purpose

This Makefile builds and installs the pthread-based `memcpy_thread` CoreSight workload.

## Research

It includes `../Makefile.miniconfig`, sets `BIN=memcpy_thread` and `LIB=-pthread`, and compiles the C source only for `CORESIGHT` arm64 builds. `install-tests` creates `$(perfexec_instdir)/$(INSTDIR_SUB)/memcpy_thread` and installs the binary there; `clean` removes it. State is the local executable and optional installed test binary. Dependencies are a C compiler, pthread library, arm64 CoreSight build gates, and perf install variables. Integration supports `memcpy_thread_16k_10.sh`. Risks are no-op build on unsupported architectures, pthread link failures in static/cross environments, and shell tests skipping if binary is absent. Test signal is successful binary creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/tests/shell/coresight/memcpy_thread/Makefile -->
