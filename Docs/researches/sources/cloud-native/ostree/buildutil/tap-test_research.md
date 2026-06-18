<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/buildutil/tap-test -->
## sources/cloud-native/ostree/buildutil/tap-test

### Purpose
This wrapper runs one GLib test binary in TAP mode inside an isolated temporary directory.

### APIs, Types, and Control Flow
It derives the test source directory and basename from `$1`, creates `TEST_TMPDIR` under `/var/tmp` by default, marks it with `.testtmp`, runs the binary with `-k --tap` under `timeout` with ABRT and a 600 second base timeout multiplied by `TEST_TIMEOUT_FACTOR`, then cleans the tempdir based on `TEST_SKIP_CLEANUP` policy.

### State, Dependencies, and Integration
It creates and usually deletes a temporary directory. It integrates with `glib-tap.mk` as `LOG_COMPILER`, ensuring tests run away from the source/build tree and can use user xattrs unavailable on tmpfs.

### Risks and Test Signals
The cleanup guard prevents deleting arbitrary paths, but failures with `TEST_SKIP_CLEANUP=err` intentionally leave directories for debugging. Test signal is TAP output consumed by `tap-driver.sh` and timeout failures represented in automake logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/buildutil/tap-test -->
