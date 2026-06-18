<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/platform/platform_linux.go -->
# sources/cloud-native/moby/daemon/internal/platform/platform_linux.go

Purpose: implements Linux host architecture and possible CPU discovery.

Important APIs and types: `possibleCPUs`, `parsePossibleCPUs`, and `runtimeArchitecture`.

Control flow: `possibleCPUs` reads `/sys/devices/system/cpu/possible`, trims whitespace, and parses comma-separated single CPU IDs or ranges. `runtimeArchitecture` calls `unix.Uname` and returns the machine string.

State and persistence: possible CPU list is cached with `sync.OnceValue`.

Dependencies and integration: used by `platform.go`.

Risks: parser returns nil for any malformed segment and does not validate range start <= end beyond loop behavior. Cached nil means transient read failures persist for process lifetime.

Test signals: `platform_linux_test.go` covers continuous, non-continuous, single, empty, invalid, and malformed inputs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/platform/platform_linux.go -->
