# sources/cloud-native/containers-storage/pkg/system/lcow_windows.go

Purpose: reports Windows LCOW support based on initialized package state.

Important APIs, types, and functions: `LCOWSupported`.

Control flow: returns `lcowSupported`, which is initialized from `LCOW_SUPPORTED` in `init_windows.go`.

State and persistence: reads in-memory package-global state; no persistence.

Dependencies and integration points: selected on Windows. Used by callers that conditionally enable Linux-container-on-Windows behavior.

Risks and edge cases: support detection is environment-variable-based and fixed at init time.

Test signals: no direct tests in requested files.
