<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/time_unsupported.go -->
# sources/cloud-native/containers-storage/pkg/archive/time_unsupported.go

Purpose: fallback timestamp conversion for non-Linux platforms without Linux `UTIME_OMIT` semantics.

Important APIs/types/functions: `timeToTimespec`.

Control flow: zero time maps to Unix nanoseconds `0`; non-zero times map to `time.UnixNano()`, then `syscall.NsecToTimespec`.

State/persistence: none.

Dependencies/integration: used by shared archive timestamp code on non-Linux platforms.

Risks/test signal: zero time becomes epoch instead of omit, so behavior can diverge from Linux. Platform tests for timestamp behavior outside this subset cover user-visible effects.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/archive/time_unsupported.go -->
