# sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel_unix_test.go

Purpose: tests kernel release parsing and version comparison on non-Windows builds.

Important APIs, types, and functions: `assertParseRelease`, `TestParseRelease`, `assertKernelVersion`, and `TestCompareKernelVersion`.

Control flow: parse tests feed representative kernel strings with flavors and missing minor components, then compare parsed results with expected `VersionInfo`. Invalid strings check exact error text. Comparison tests exercise equality and less/greater cases across kernel, major, and minor fields.

State and persistence: no state beyond test data.

Dependencies and integration points: depends on `fmt` and `testing`; validates `kernel.go` independently of actual host kernel.

Risks and edge cases: tests do not cover `CheckKernelVersion` or platform `GetKernelVersion`. Flavor comparison is only checked for parse preservation, not ordering.

Test signals: strong parser coverage for common Linux/Debian/Gentoo-style release forms and numeric ordering.
