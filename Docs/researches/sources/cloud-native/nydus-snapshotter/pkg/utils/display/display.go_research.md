<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/display/display.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/display/display.go

Purpose: provides small formatting helpers for displaying byte and latency values in human-readable units.

Important APIs: `ByteToReadableIEC(uint32)` formats bytes using IEC units (`B`, `KiB`, `MiB`, etc.) with one decimal beyond bytes. `MicroSecondToReadable(uint64)` formats microseconds as `us`, milliseconds, or seconds with three decimals.

Control flow and state: both functions are pure and stateless. Byte formatting divides by 1024 until the appropriate IEC exponent; time formatting switches at 1000 and 1,000,000 microseconds.

Dependencies/integration: only depends on `fmt`; likely used by logging, metrics, or CLI display code.

Risks and test signals: `ByteToReadableIEC` accepts `uint32`, so it cannot display values above 4 GiB accurately if callers have larger counters. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/display/display.go -->
