<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/path.go -->
# sources/cloud-native/buildkit/util/system/path.go

Purpose: normalizes Dockerfile/build paths across Linux and Windows semantics, especially WORKDIR/COPY-like paths rooted in container filesystems.

Important APIs and types: `DefaultPathEnv`, `NormalizePath`, `ToSlash`, `FromSlash`, `NormalizeWorkdir`, `IsAbs`, `CheckSystemDriveAndRemoveDriveLetter`, and `cleanPath`.

Control flow: `NormalizePath` converts to slash form, defaults parent to root, removes/validates Windows drive letters, absolutizes relative paths against parent, optionally preserves trailing slash or `/.`, and returns slash form. `NormalizeWorkdir` then converts slash form to platform separators. Windows drive handling rejects non-system drives, bare drive letters, and UNC paths, while stripping `C:` from valid paths.

State and persistence: pure string processing.

Dependencies and integration: used by frontend/build path handling to normalize user-provided container paths. Uses `path` rather than `filepath` to make slash-form handling independent of host OS.

Risks: Windows semantics are intentionally container-root-specific and differ from `filepath.IsAbs`. UNC paths are not supported. `keepSlash` behavior preserves selected trailing syntax and can produce `/.` suffixes.

Test signals: `path_test.go` covers Linux and Windows workdir normalization, drive-letter removal, slash preservation, and Windows absolute detection.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/system/path.go -->
