<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/Makefile

Purpose: build rules for arm64 Guarded Control Stack selftests.

Important definitions: `TEST_GEN_PROGS` includes `basic-gcs`, `libc-gcs`, `gcs-locking`, `gcs-stress`, `gcspushm`, and `gcsstr`; `TEST_GEN_PROGS_EXTENDED` includes `gcs-stress-thread`; `LDLIBS += -lpthread`.

Control flow: includes `../../lib.mk` after target definitions. Custom rules build `basic-gcs` with nolibc/static/freestanding options to avoid toolchain/dynamic-linker interaction, and build assembly helpers with `-nostdlib`.

State and persistence: build artifacts only under kselftest output.

Dependencies and integration: depends on kselftest lib.mk, nolibc include path, kernel UAPI headers, pthread for libc tests, and assembler support for GCS instruction encodings used in `.S` files.

Risks: nolibc/static flags are sensitive to include path layout. GCS tests deliberately avoid normal runtime startup for some binaries.

Test signals: successful build creates all generated test programs and the extended stress thread helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/Makefile -->
