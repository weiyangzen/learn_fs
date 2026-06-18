# sources/distributed-fs/ceph-client/tools/testing/selftests/net/mptcp/Makefile

## Purpose
This Makefile builds and installs the MPTCP selftest suite programs and scripts.

## Important Targets and Variables
`CFLAGS` includes kernel UAPI and tools headers. `TEST_PROGS` lists shell tests such as `diag.sh`, `mptcp_connect.sh`, checksum/mmap/sendfile/splice wrappers, join, sockopt, path-manager, simultaneous-flow, and userspace PM tests. `TEST_GEN_FILES` builds `mptcp_connect`, `mptcp_diag`, `mptcp_inq`, `mptcp_sockopt`, and `pm_nl_ctl`. `TEST_FILES` installs `mptcp_lib.sh` and `settings`. `TEST_INCLUDES` includes shared net shell helpers. `EXTRA_CLEAN` removes packet captures.

## Control Flow and State
The Makefile delegates build and install behavior to `../../lib.mk`. Generated state is the compiled helper binaries and installed scripts/files.

## Dependencies and Integration
It depends on the kselftest framework, GCC/clang, kernel headers, and the wider MPTCP shell library. The wrapper scripts in this subset rely on `mptcp_connect.sh` and the generated `mptcp_connect` binary.

## Risks and Test Signals
Header mismatch can break compilation of newer MPTCP structs/options. Successful build produces all `TEST_GEN_FILES`; runtime suite signals are produced by the individual shell tests.
