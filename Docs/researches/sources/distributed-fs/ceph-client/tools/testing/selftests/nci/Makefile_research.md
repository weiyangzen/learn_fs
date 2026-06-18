# sources/distributed-fs/ceph-client/tools/testing/selftests/nci/Makefile

Purpose: Builds the NFC Controller Interface selftest binary `nci_dev`.

Important APIs/types/functions: Adds linker and compiler flags via `CFLAGS += -Wl,-no-as-needed -Wall` and `LDFLAGS += -lpthread`, declares `TEST_GEN_PROGS := nci_dev`, and includes `../lib.mk`.

Control flow: Kselftest `lib.mk` consumes `TEST_GEN_PROGS` to compile `nci_dev.c` into a generated test program. `-lpthread` is required because the test uses worker threads to emulate virtual NCI device responses.

State and persistence behavior: Build-only file; generated binaries land in the kselftest output tree according to `lib.mk`.

Dependencies and integration points: Depends on the kselftest build framework and pthreads. It pairs with `config`, which requests NFC and virtual NCI kernel support.

Risks: `LDFLAGS` rather than target-specific `LDLIBS` may vary with kselftest make rules. Missing pthread linkage breaks the virtual device protocol helpers in `nci_dev.c`.

Test signals: `make -C tools/testing/selftests/nci` should produce `nci_dev`; running the test requires `/dev/virtual_nci` and NFC generic netlink support.
