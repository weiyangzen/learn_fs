# sources/distributed-fs/ceph-client/tools/testing/selftests/liveupdate/luo_test_utils.c

Purpose: shared utility implementation for LUO kexec selftests. It abstracts LUO device open, session ioctls, memfd preservation/restoration, state-file handling, daemonization, and stage selection.

Important APIs/types/functions: wraps `LIVEUPDATE_IOCTL_CREATE_SESSION`, `LIVEUPDATE_IOCTL_RETRIEVE_SESSION`, `LIVEUPDATE_SESSION_PRESERVE_FD`, `LIVEUPDATE_SESSION_RETRIEVE_FD`, and `LIVEUPDATE_SESSION_FINISH`. Uses `memfd_create`, `ftruncate`, `mmap`, `read`, `fork`, `setsid`, `getopt_long`, and kselftest exit helpers.

Control flow: `luo_test()` parses `--stage`, opens `/dev/liveupdate`, probes for the named state session to detect stage 1 versus 2, enforces requested/detected stage agreement, and dispatches to caller-provided stage callbacks. `create_and_preserve_memfd()` creates a one-page memfd, maps and writes the payload, then preserves it under a token. `restore_and_verify_memfd()` retrieves by token, maps the file read-only, and optionally compares payload. `create_state_file()` creates a state session and deliberately leaves its FD open. `daemonize_and_wait()` forks, exits the parent, detaches the child, closes stdio, changes to `/`, and sleeps forever.

State and persistence: state is encoded in preserved memfds; the state session FD is intentionally retained to prevent unpreservation. Process persistence through the daemon child is part of the test contract.

Dependencies and integration points: central integration point for LUO stage tests. Depends on liveupdate uapi, kselftest, memfd, kexec workflow, and process/session semantics.

Risks: `fail_exit` reports current `errno`, so callers should preserve errno before unrelated operations. Infinite daemon children need operator awareness. `create_and_preserve_memfd()` closes the original memfd after preservation, assuming the kernel-side LUO reference is sufficient.

Test signals: skip on missing LUO device; failure on stage mismatch, ioctl errors, or payload mismatch.
