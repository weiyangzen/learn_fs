# sources/distributed-fs/ceph-client/tools/testing/selftests/kcmp/Makefile

This Makefile builds the `kcmp_test` generated selftest program. It adds kernel header includes, declares the generated binary, and arranges cleanup for the temporary runtime file.

Important variables are `CFLAGS += $(KHDR_INCLUDES)`, `TEST_GEN_PROGS := kcmp_test`, and `EXTRA_CLEAN := $(OUTPUT)/kcmp-test-file`. It includes `../lib.mk`.

Control flow is the default kselftest build/clean path. Dependencies are kernel headers, `linux/kcmp.h`, a compiler, and common selftest make rules. The main risk is cleanup path mismatch if runtime and output directories differ. Pass signals are successful compilation and cleanup of `kcmp-test-file`.
