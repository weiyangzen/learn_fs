# sources/cloud-native/containers-storage/pkg/system/meminfo.go

Purpose: defines a portable memory statistics data structure.

Important APIs, types, and functions: `MemInfo` with fields `MemTotal`, `MemFree`, `SwapTotal`, and `SwapFree`.

Control flow: none; data type only.

State and persistence: no state. Instances represent a snapshot of host memory/swap values in bytes.

Dependencies and integration points: platform-specific `ReadMemInfo` implementations populate this type.

Risks and edge cases: field semantics vary by platform source and may not include available/cached memory. Values are int64 bytes.

Test signals: Linux `meminfo_unix_test.go` validates parser population of all four fields.
