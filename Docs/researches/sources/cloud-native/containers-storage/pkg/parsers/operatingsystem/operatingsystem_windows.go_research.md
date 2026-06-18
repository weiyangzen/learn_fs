# sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_windows.go

Purpose: retrieves the Windows product name and reports containerization unsupported/false.

Important APIs, types, and functions: `GetOperatingSystem` and `IsContainerized`.

Control flow: opens the Windows current-version registry key, reads `ProductName` into a UTF-16 buffer, converts it to string, and returns `"Unknown Operating System"` with an error on failures. `IsContainerized` returns false, nil.

State and persistence: reads registry state only.

Dependencies and integration points: depends on `unsafe` and `golang.org/x/sys/windows`; selected on Windows.

Risks and edge cases: registry access errors propagate with default string. Buffer size is fixed at 1024 UTF-16 code units. No Windows container detection is attempted.

Test signals: no Windows-specific tests in the requested set.
