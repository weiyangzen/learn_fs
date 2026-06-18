# Research: sources/cloud-native/buildkit/cmd/buildkitd/config/gcpolicy_windows.go

Purpose: supplies Windows-specific default GC cap constants used by `DetectDefaultGCCap`.

Important constants: Windows builds reserve 10% up to 10 GB, set max cache use to 60% up to 50 GB, and target 20% free disk space. The lower max-byte cap differs from Unix.

State and dependencies: no runtime state or imports. The constants feed default GC policies for Windows workers.

Risks and test signals: incorrect constants can cause over-aggressive or under-aggressive cache cleanup on Windows. There are no file-local tests; behavior is indirectly exercised when config defaults are built on Windows.
