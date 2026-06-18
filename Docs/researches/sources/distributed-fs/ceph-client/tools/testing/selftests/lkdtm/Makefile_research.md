# sources/distributed-fs/ceph-client/tools/testing/selftests/lkdtm/Makefile

Purpose: build/install rule for LKDTM kselftests.

Important APIs/types/functions: includes `../lib.mk`, declares `TEST_FILES := tests.txt`, `TEST_PROGS := stack-entropy.sh`, and generates one shell wrapper per test name parsed from `tests.txt`.

Control flow: `TEST_GEN_PROGS` is computed by reading the first column of `tests.txt`, stripping leading `#`, and appending `.sh` under `$(OUTPUT)`. The pattern rule installs `run.sh` as each generated test wrapper.

State and persistence: no runtime state; it packages generic `run.sh` under many test-specific names.

Dependencies and integration points: depends on `tests.txt`, `run.sh`, `stack-entropy.sh`, and kselftest `lib.mk`. The generated script name is how `run.sh` selects the LKDTM trigger.

Risks: the generated list is only as accurate as `tests.txt`; commented-out tests still get wrappers and are skipped at runtime.

Test signals: kselftest discovers generated wrappers and the entropy script through `TEST_GEN_PROGS`/`TEST_PROGS`.
