## sources/cloud-native/containers-storage/pkg/fileutils/fileutils_unix.go

Purpose: Linux/FreeBSD implementation of process file-descriptor count.

Important APIs/types/functions: `GetTotalUsedFds`.

Control flow: reads `/proc/<pid>/fd` and returns the number of directory entries; logs and returns `-1` on failure.

State and persistence: read-only `/proc` inspection.

Dependencies and integration points: diagnostics/resource tracking helper. Depends on procfs availability even on FreeBSD build tag.

Risks: environments without procfs return `-1`; logging an error on unsupported procfs may be noisy.

Test signals: no direct selected tests.
