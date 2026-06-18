<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/pidfile/pidfile_test.go -->
# sources/cloud-native/moby/pkg/pidfile/pidfile_test.go

Purpose: unit/integration tests for pidfile read/write semantics. Tests cover invalid PIDs, writing/reading the current or child process PID, stale/dead PID handling, malformed content, missing files, and existing live process protection. State includes temp pidfiles and sometimes a child process. Dependencies include os/exec, runtime branching, and testing. Risks covered include stale-file overwrite safety and parser tolerance; PID reuse remains inherently race-sensitive. Test signal is strong for filesystem behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/pidfile/pidfile_test.go -->
