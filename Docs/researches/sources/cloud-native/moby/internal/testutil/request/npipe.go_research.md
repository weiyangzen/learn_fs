<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/npipe.go -->
# sources/cloud-native/moby/internal/testutil/request/npipe.go

Purpose: non-Windows fallback for named-pipe dialing. `npipeDial` panics because the npipe protocol is only supported on Windows. Control flow exists only to fail loudly if non-Windows code attempts to dial an npipe daemon. State and persistence are absent. Dependencies are `net` and `time` for signature compatibility. Risks are intentional: callers must route by daemon URL scheme correctly. Test signal is compile-time portability plus runtime guard.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/npipe.go -->
