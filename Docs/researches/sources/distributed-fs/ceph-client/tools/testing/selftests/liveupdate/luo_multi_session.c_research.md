# sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/luo_multi_session.c

Purpose: kexec lifecycle selftest for multiple LUO sessions, including empty sessions and sessions with one or more preserved memfds.

Important APIs/types/functions: uses `luo_create_session()`, `create_and_preserve_memfd()`, `luo_retrieve_session()`, `restore_and_verify_memfd()`, `luo_session_finish()`, and the generic `luo_test()` stage dispatcher.

Control flow: stage 1 writes state stage `2`, creates two empty sessions and two populated sessions, preserving one memfd in `SESSION_FILES_1` and two memfds in `SESSION_FILES_2`. It then daemonizes to pin resources for kexec. Stage 2 reads the state memfd, retrieves all four sessions, verifies all three payloads by token, finishes every test session, finishes the state session, and reports success.

State and persistence: the test asserts that LUO preserves both session namespace and per-token file payloads across kexec. Empty sessions are significant because they validate metadata preservation independent of files.

Dependencies and integration points: same LUO/kexec/manual orchestration dependencies as `luo_kexec_simple.c`. Integrates through shared helper callbacks.

Risks: a partial prior run can leave named sessions that affect detected stage or duplicate-name behavior. Empty-session finalization is an important cleanup step because otherwise persistent metadata may remain.

Test signals: exact data matches for three restored memfds, successful retrieval of two empty sessions, and successful finish calls are the key pass signals.
