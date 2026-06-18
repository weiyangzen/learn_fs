# sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_unix.go

Purpose: implements basic OS name lookup for FreeBSD and Darwin.

Important APIs, types, and functions: `GetOperatingSystem` and `IsContainerized`.

Control flow: `GetOperatingSystem` runs `uname -s` and returns its raw output. `IsContainerized` always returns false with an explanatory error because jail/container detection is not implemented.

State and persistence: no persistence; reads system command output.

Dependencies and integration points: depends on `errors` and `os/exec`; selected for FreeBSD or Darwin builds.

Risks and edge cases: returned OS name includes the trailing newline. Container detection callers must handle the non-nil error.

Test signals: no FreeBSD/Darwin-specific tests in requested files.
