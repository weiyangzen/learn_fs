# sources/cloud-native/containers-storage/pkg/system/utimes_unsupported.go

Purpose: unsupported-platform stub for symlink timestamp updates.

Important APIs/types/functions: `LUtimesNano(path string, ts []syscall.Timespec) error` returns `ErrNotSupportedPlatform`.

Control flow: no syscall is attempted.

State/persistence: none.

Dependencies/integration: selected on platforms other than Linux and FreeBSD, letting callers compile and handle unsupported symlink timestamp preservation.

Risks: archive extraction on unsupported platforms may lose symlink timestamp fidelity.

Test signals: platform tests should assert unsupported errors where callers expose this behavior.
