# sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/Makefile

Purpose: kselftest makefile for PTP clock tests.

Important APIs and functions: adds `$(KHDR_INCLUDES)` to CFLAGS, builds generated program `testptp`, links with `-lrt`, and lists `phc.sh` as a shell test.

Control flow: includes `../lib.mk` to inherit selftest build/run rules.

State and persistence: no runtime state.

Dependencies and integration: depends on kernel UAPI headers for `linux/ptp_clock.h` and realtime library linkage.

Risks and test signals: the generated C tool is broad and hardware-dependent; the shell test requires an explicit PTP device argument and root.
