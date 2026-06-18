# sources/distributed-fs/ceph-client/tools/testing/selftests/riscv/sigreturn/Makefile

Purpose: builds the static RISC-V `sigreturn` vector-context selftest. It adds `tools/include`, sets `TEST_GEN_PROGS := sigreturn`, includes `../../lib.mk`, and explicitly links `sigreturn.c` statically. State is only the output binary. Dependencies are RISC-V vector-capable toolchain headers and static link support. Risks are running on kernels without vector signal context support or hardware without V extension. Test signals are successful build and two harness tests in `sigreturn`.
