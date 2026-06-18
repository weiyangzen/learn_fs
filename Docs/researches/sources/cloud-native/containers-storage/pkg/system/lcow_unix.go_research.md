# sources/cloud-native/containers-storage/pkg/system/lcow_unix.go

Purpose: reports Linux Containers on Windows unsupported on non-Windows platforms.

Important APIs, types, and functions: `LCOWSupported`.

Control flow: returns false.

State and persistence: no state.

Dependencies and integration points: selected for non-Windows builds. Provides cross-platform API compatibility with Windows implementation.

Risks and edge cases: none beyond always-false behavior.

Test signals: no direct tests in requested files.
