# sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/testptp.mk

Purpose: standalone makefile for building the `testptp` utility outside the kselftest `lib.mk` flow.

Important APIs and functions: defines `CC`, kernel header include path `-I$(KBUILD_OUTPUT)/usr/include`, `CFLAGS=-Wall`, `LDLIBS=-lrt`, `PROGS=testptp`, and clean targets.

Control flow: default `all` builds `testptp` from `testptp.o`; `clean` removes object; `distclean` removes object and executable.

State and persistence: build artifacts only.

Dependencies and integration: expects exported `KBUILD_OUTPUT` and optional `CROSS_COMPILE`.

Risks and test signals: unlike the kselftest Makefile, it does not include `KHDR_INCLUDES`; wrong header path can build against stale or missing PTP UAPI.
