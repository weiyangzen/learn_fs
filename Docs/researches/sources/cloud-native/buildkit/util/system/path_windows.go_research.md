<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/path_windows.go -->
# sources/cloud-native/buildkit/util/system/path_windows.go

Purpose: Windows host path helpers that account for default system volume prefixing.

Important APIs and types: `DefaultSystemVolumeName`, `IsAbsolutePath`, and `GetAbsolutePath`.

Control flow: `IsAbsolutePath` cleans a path, prepends `C:` when it starts with a separator, then calls `filepath.IsAbs`. `GetAbsolutePath` cleans the path, returns it unchanged if it already starts with `C:` case-insensitively, otherwise prefixes `C:`.

State and persistence: pure path helpers.

Dependencies and integration: used in Windows-specific path handling outside the container-root normalization in `path.go`.

Risks: assumes default system volume is `C:`. Network/UNC and alternate drive semantics are not preserved by `GetAbsolutePath`.

Test signals: Windows-specific direct tests are not included in this subset; `path_test.go` tests cross-platform path logic in `path.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/path_windows.go -->
