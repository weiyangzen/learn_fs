# Research: sources/cloud-native/buildkit/contrib/cdisetup/venus/venus_windows.go

Purpose: provides an empty Windows package stub for the Venus CDI setup package.

Important behavior: the file only declares `package venus`; no registration or setup code is compiled for Windows.

State and dependencies: no state, imports, or side effects.

Risks and test signals: this prevents Unix-specific device probing and `/etc/cdi` writes on Windows, but also means the `venus` build tag import has no setup effect there. No tests are needed beyond successful Windows compilation.
