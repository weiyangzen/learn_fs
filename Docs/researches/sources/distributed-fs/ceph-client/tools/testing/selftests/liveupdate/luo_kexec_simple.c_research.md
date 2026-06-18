# sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/luo_kexec_simple.c

Purpose: manual two-stage kexec selftest for LUO persistence of one named session containing one memfd across a kexec reboot.

Important APIs/types/functions: imports `luo_test_utils.h`. Defines session/token/data constants and implements `run_stage_1()` and `run_stage_2()` callbacks consumed by `luo_test()`.

Control flow: stage 1 creates a state-tracking LUO session with token `999` containing next-stage value `2`, creates the main test session, preserves a memfd with token `0x1A`, closes the LUO device, and daemonizes so FDs remain pinned while the operator performs kexec. Stage 2 verifies the state memfd contains stage `2`, retrieves the named test session, restores and verifies the memfd payload, then finishes both the test and state sessions.

State and persistence: relies on LUO preserving sessions and memfd payloads across kexec. State progression is stored inside a preserved memfd, not in the filesystem. A daemonized child intentionally holds session references after stage 1.

Dependencies and integration points: requires `/dev/liveupdate`, kexec-capable environment, the LUO kernel module/device, memfd support, and manual or external reboot orchestration.

Risks: stage mismatch fails hard; stale state sessions from a previous interrupted run can make the system appear to be in stage 2. The daemonized holder must be cleaned through test completion or process management.

Test signals: emits kselftest messages; success requires exact payload recovery and successful `LIVEUPDATE_SESSION_FINISH` for both sessions.
