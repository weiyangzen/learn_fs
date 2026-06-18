# sources/distributed-fs/ceph-client/tools/testing/selftests/ir/Makefile

This Makefile registers the infrared loopback selftest. The runnable test is `ir_loopback.sh`; the generated extended helper is the C program `ir_loopback`.

Important variables are `TEST_PROGS := ir_loopback.sh`, `TEST_GEN_PROGS_EXTENDED := ir_loopback`, `APIDIR := ../../../include/uapi`, and `CFLAGS += -Wall -O2 -I$(APIDIR)`. The file then includes `../lib.mk`.

Control flow is standard kselftest build logic: build the helper and run/install the shell wrapper. It depends on UAPI headers for LIRC and rc protocol constants, a compiler, and common selftest make rules. The main risk is stale or incompatible UAPI headers, partly mitigated by fallback constants in the C file. Pass signal is a successful helper build and wrapper registration.
