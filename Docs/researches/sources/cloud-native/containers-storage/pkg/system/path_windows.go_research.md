# sources/cloud-native/containers-storage/pkg/system/path_windows.go

Purpose: validates Windows paths used by operations such as copying files into or out of containers, removing an optional system-drive prefix and converting slashes to Windows semantics.

Important APIs/types/functions: `CheckSystemDriveAndRemoveDriveLetter` rejects bare drive-relative forms like `C:`, rejects absolute paths on non-system drives, strips `C:` from absolute paths, and applies `filepath.FromSlash`.

Control flow: two-character drive-only paths fail as relative paths. Non-absolute or short paths are slash-normalized and returned. Absolute drive-letter paths must use `C:` case-insensitively, then the drive prefix is removed before slash normalization.

State/persistence: no persistent state; returns normalized path strings.

Dependencies/integration: depends on `filepath`, `strings`, and `fmt`. Used by Windows path validation in user-facing copy/extract code and by tests in `path_windows_test.go`.

Risks: system drive is hard-coded to `C:`. Error text currently uses lower-case messages in implementation, while the test file expects older capitalized messages, so test drift is a signal. UNC and extended-length path behavior is not explicitly handled here.

Test signals: tests cover non-system drive rejection, relative paths, slash conversion, system-drive stripping, and bare-drive failures; they should be kept in sync with exact error strings.
