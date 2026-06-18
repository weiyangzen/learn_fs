# sources/distributed-fs/ceph-client/tools/testing/selftests/lsm/Makefile

Purpose: builds LSM syscall kselftests.

Important APIs/types/functions: sets `CFLAGS += -Wall -O2 $(KHDR_INCLUDES)`, includes `common.h` as a local header, builds `lsm_get_self_attr_test`, `lsm_list_modules_test`, and `lsm_set_self_attr_test`, and links each with `common.c`.

Control flow: standard kselftest build using `../lib.mk`; target-specific prerequisites ensure common helper code is compiled into each test.

State and persistence: no runtime state.

Dependencies and integration points: requires installed/generated kernel headers containing `linux/lsm.h` and syscall numbers.

Risks: comments note headers should be installed first; stale or missing headers can break builds or test the wrong ABI shape.

Test signals: generated C programs are discovered through `TEST_GEN_PROGS`.
