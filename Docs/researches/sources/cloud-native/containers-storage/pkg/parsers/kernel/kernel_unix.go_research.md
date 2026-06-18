# sources/cloud-native/containers-storage/pkg/parsers/kernel/kernel_unix.go

Purpose: implements kernel version retrieval for Unix platforms other than Darwin.

Important APIs, types, and functions: `GetKernelVersion`.

Control flow: calls `unix.Uname`, converts `uts.Release` to a Go string, and passes it to `ParseRelease`.

State and persistence: no persistence; reads current kernel release from uname.

Dependencies and integration points: depends on `golang.org/x/sys/unix` and common parser code. Selected for `unix && !darwin`.

Risks and edge cases: parsing can fail for unusual release strings. Uname errors are propagated.

Test signals: common Unix tests validate parser behavior; this function itself is not mocked in the requested tests.
