<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/time_linux.go -->
# sources/cloud-native/containers-storage/pkg/archive/time_linux.go

Purpose: Linux conversion from Go `time.Time` to `syscall.Timespec` for timestamp syscalls that support `UTIME_OMIT`.

Important APIs/types/functions: `timeToTimespec`.

Control flow: returns a timespec with `Nsec` equal to `(1<<30)-2` for zero time, matching Linux `UTIME_OMIT`; otherwise converts `UnixNano` with `syscall.NsecToTimespec`.

State/persistence: none.

Dependencies/integration: used by archive timestamp application paths to leave timestamps unchanged when a zero time means omitted.

Risks/test signal: Linux-specific sentinel behavior differs from unsupported platforms. Incorrect sentinel values would unexpectedly set timestamps to epoch or current time.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/time_linux.go -->
