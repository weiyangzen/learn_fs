# sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel_darwin.go

Purpose: implements Darwin kernel version retrieval.

Important APIs, types, and functions: `GetKernelVersion` and private `getRelease`.

Control flow: runs `system_profiler SPSoftwareDataType`, scans for `Kernel Version`, splits after the colon, parses the value with shellwords, expects `Darwin x.x.x`, and returns the version string to `ParseRelease`.

State and persistence: no persistence; reads current system profiler output.

Dependencies and integration points: depends on `fmt`, `os/exec`, `strings`, and `github.com/mattn/go-shellwords`. It plugs into common kernel parsing.

Risks and edge cases: external command can be slow, unavailable, localized, or produce unexpected formatting. Empty release returns through `ParseRelease` as an error.

Test signals: no Darwin-specific tests in the requested set; common parser tests cover release parsing after retrieval.
