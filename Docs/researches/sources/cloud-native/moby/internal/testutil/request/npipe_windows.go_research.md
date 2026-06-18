<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/npipe_windows.go -->
# sources/cloud-native/moby/internal/testutil/request/npipe_windows.go

Purpose: Windows implementation for named-pipe Docker daemon connections. `npipeDial` delegates to `winio.DialPipe` with the caller's timeout. State is the returned pipe connection. Dependencies are `github.com/Microsoft/go-winio`. Risks include path formatting, timeout behavior, and Windows-only daemon host semantics. Test signal is through request helpers on Windows.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/request/npipe_windows.go -->
