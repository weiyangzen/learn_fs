# sources/distributed-fs/ceph-client/tools/testing/selftests/locking/Makefile

Purpose: kselftest Makefile for locking selftests in this subset.

Important APIs/types/functions: declares an empty `all` target to avoid accidentally invoking runtime tests during a plain build, sets `TEST_PROGS := ww_mutex.sh`, and includes `../lib.mk`.

Control flow: build-time only; no binaries are generated.

State and persistence: none.

Dependencies and integration points: delegates runtime behavior to `ww_mutex.sh` and kselftest `lib.mk`.

Risks: if more locking tests are added, they must be explicitly listed or they will not run.

Test signals: kselftest discovers the shell program via `TEST_PROGS`.
