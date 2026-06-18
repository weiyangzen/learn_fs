# sources/distributed-fs/ceph-client/tools/testing/selftests/kmod/Makefile

This Makefile registers the kmod loader selftest script without building binaries. A no-op `all` target prevents an argument-less make from accidentally triggering test execution.

Important elements are `all:`, `TEST_PROGS := kmod.sh`, inclusion of `../lib.mk`, and an empty `clean` target. There is no generated build state.

Dependencies are common selftest make rules and the runtime modules named in `config`. Integration is standard kselftest script discovery.

Risks are minimal in the Makefile itself; all heavy behavior is in `kmod.sh`. Pass signal is that `kmod.sh` is installed and invoked as a selftest program.
