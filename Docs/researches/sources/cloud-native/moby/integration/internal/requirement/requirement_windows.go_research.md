# sources/cloud-native/moby/integration/internal/requirement/requirement_windows.go

Purpose: Windows stubs for requirement helpers that are Linux-specific.

Important APIs and helpers: `overlayFSSupported` and `Overlay2Supported`.

Control flow: both functions return false unconditionally on Windows.

State and persistence: no state is read or written.

Dependencies and integration: no imports. Build tag `windows` selects this file for Windows builds.

Risks: any test using these helpers on Windows will see overlay support as unavailable, which is appropriate for overlay2-specific Linux behavior.

Test signals: helper-only; ensures requirement package compiles and produces conservative answers on Windows.
