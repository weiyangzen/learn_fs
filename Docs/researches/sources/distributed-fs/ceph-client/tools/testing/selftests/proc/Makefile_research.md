# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/Makefile

Purpose: builds a broad set of procfs selftests, including the fd and kthread tests researched in this subset.

Important APIs/types/functions: sets `CFLAGS += -Wall -O2 -Wno-unused-function`, `CFLAGS += $(TOOLS_INCLUDES)`, `LDFLAGS += -pthread`, and appends many `TEST_GEN_PROGS`.

Control flow: includes `../lib.mk` after listing test programs.

State and persistence behavior: build-only, generating test binaries under kselftest output.

Dependencies and integration points: relies on common proc test headers such as `proc.h` and kselftest build infrastructure.

Risks and test signals: this Makefile covers more tests than the current work item; build failures in unrelated proc tests can affect running the whole directory.
