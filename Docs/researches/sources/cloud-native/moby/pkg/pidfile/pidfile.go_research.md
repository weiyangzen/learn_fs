<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/pidfile/pidfile.go -->
# sources/cloud-native/moby/pkg/pidfile/pidfile.go

Purpose: small PID file reader/writer that ignores stale or malformed content but prevents overwriting a live process PID. Important APIs are `Read` and `Write`. Control flow reads and trims file content, parses an integer, returns zero for malformed/dead/zero PIDs, checks liveness via `process.Alive`, rejects non-positive new PIDs, and writes decimal PID with 0644 permissions. State is the pidfile path on disk and live process table observation. Dependencies include `os`, `strconv`, and Moby `process`. Risks include PID reuse races, malformed files silently treated as empty, and permissions. Test signal is in `pidfile_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/pidfile/pidfile.go -->
