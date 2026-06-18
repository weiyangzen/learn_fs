<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/platform/platform.go -->
# sources/cloud-native/moby/daemon/internal/platform/platform.go

Purpose: exposes runtime host architecture and possible CPU IDs with platform-specific implementations.

Important APIs and types: `Architecture`, `PossibleCPU`, package variables `arch` and `onceArch`.

Control flow: `Architecture` calls `runtimeArchitecture` once and logs errors. `PossibleCPU` returns platform `possibleCPUs` if available; otherwise it falls back to a slice from 0 through `runtime.NumCPU()`.

State and persistence: caches architecture for process lifetime. CPU list may be cached in platform-specific code.

Dependencies and integration: used by daemon info/resource code that needs host rather than compiler architecture.

Risks: fallback loop uses `<= runtime.NumCPU()`, producing one more CPU index than conventional 0..N-1. Architecture errors leave cached `arch` empty.

Test signals: Linux parsing is covered in `platform_linux_test.go`; generic fallback is not.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/platform/platform.go -->
