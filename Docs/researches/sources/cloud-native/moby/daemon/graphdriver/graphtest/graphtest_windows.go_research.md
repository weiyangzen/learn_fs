# sources/cloud-native/moby/daemon/graphdriver/graphtest/graphtest_windows.go

Purpose: Windows package placeholder for `graphtest`.

Important APIs and control flow: the file only declares package `graphtest`, preventing Unix-specific test helper files from being compiled on Windows while allowing package references to resolve.

State, dependencies, and risks: no runtime state, APIs, or tests are defined here. Windows graphdriver coverage must come from Windows-specific tests elsewhere; the Unix graphtest conformance suite is not available on Windows through this file.
