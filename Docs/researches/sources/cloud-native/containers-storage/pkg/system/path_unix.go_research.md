# sources/cloud-native/containers-storage/pkg/system/path_unix.go

Purpose: Unix no-op implementation of Windows system-drive path normalization.

Important APIs/types/functions: `CheckSystemDriveAndRemoveDriveLetter(path string) (string, error)`.

Control flow: returns the input path unchanged with nil error.

State/persistence: none.

Dependencies/integration: lets shared code call the path-normalization API without build-tag branching.

Risks: Unix callers get no validation or slash conversion, which is correct only because drive-letter checks are Windows-specific.

Test signals: compile coverage on non-Windows platforms and cross-platform tests that expect no-op behavior.
