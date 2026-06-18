# sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/liveupdate.c

Purpose: kselftest harness coverage for the Live Update Orchestrator character device at `/dev/liveupdate`. It validates ordinary device access, exclusive open behavior, LUO session creation/retrieval constraints, and preservation of supported file descriptors, especially memfds.

Important APIs/types/functions: uses `linux/liveupdate.h` ioctl structs and commands: `liveupdate_ioctl_create_session`, `LIVEUPDATE_IOCTL_CREATE_SESSION`, `liveupdate_session_preserve_fd`, and `LIVEUPDATE_SESSION_PRESERVE_FD`. Local helpers `create_session()` and `preserve_fd()` convert ioctl failures to negative errno values for assertions. Tests are expressed through `kselftest_harness.h` `FIXTURE`, `TEST_F`, `ASSERT_*`, `EXPECT_*`, and `SKIP`.

Control flow: a fixture initializes two device FDs and closes them in teardown. Early tests open `/dev/liveupdate`, skip on `ENOENT`, and check exclusive access returns `EBUSY`. Session tests create duplicate and distinct named sessions. Preservation tests allocate memfds, write known strings, preserve them by token, then seek/read to confirm visible content remains intact. Complex coverage spans two sessions, empty memfds, non-empty memfds, unsupported `/dev/null`, and double-preservation rejection with `EBUSY`.

State and persistence: state is mostly kernel-side LUO session/file tracking. The test keeps session and memfd FDs alive long enough to verify immediate post-ioctl visibility; it does not exercise reboot persistence.

Dependencies and integration points: requires a kernel/device exposing `/dev/liveupdate`, memfd support, and the liveupdate uapi header. Integrates with kselftest result semantics.

Risks: tests assume `/dev/null` has no LUO preservation handler and that LUO enforces process-wide exclusive device open. Some failure paths may leak FDs after a fatal assertion, acceptable for short kselftest runs.

Test signals: pass/fail is assertion-driven; missing device is reported as skip. Key expected errno signals are `ENOENT`, `EBUSY`, and `EEXIST`.
