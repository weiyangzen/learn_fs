# sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel.go

Purpose: defines cross-Unix kernel version representation, parsing, comparison, and minimum-version checks.

Important APIs, types, and functions: `VersionInfo`, `String`, `CompareKernelVersion`, `CheckKernelVersion`, and `ParseRelease`.

Control flow: `ParseRelease` uses `fmt.Sscanf` to parse kernel and major components plus a partial tail, then parses optional minor/flavor. `CompareKernelVersion` compares kernel, major, and minor numerically. `CheckKernelVersion` calls platform `GetKernelVersion`, logs warning on error, and returns true unless a successfully read version is below the requested threshold.

State and persistence: no persistence. State is returned as `VersionInfo`.

Dependencies and integration points: depends on `errors`, `fmt`, and `logrus`. Platform files provide `GetKernelVersion` for Unix variants.

Risks and edge cases: flavor is ignored by comparisons. `CheckKernelVersion` defaults to true if version lookup fails, favoring permissive behavior. Parser accepts versions without a third numeric component by setting minor zero.

Test signals: `kernel_unix_test.go` covers parse formats, invalid strings, and numeric comparisons.
