# sources/distributed-fs/glusterfs/xlators/meta/src/version-file.c

Purpose: implements the root-level virtual `version` file, reporting the build `PACKAGE_VERSION` in a small JSON-like object.

Important APIs/types/functions: `version_file_fill()` writes `Package Version`; `meta_version_file_hook()` attaches `version_file_ops`.

Control flow: root directory lookup of `version` installs the file ops. Readv invokes the default file generation path.

State and persistence behavior: no mutable state. The value is compile-time package metadata rendered at runtime.

Dependencies and integration points: depends on the build-defined `PACKAGE_VERSION` macro and `strfd`.

Risks and edge cases: output is JSON-like but not followed by a newline and should be treated as diagnostic text unless consumers validate it. Package version may not uniquely identify downstream patches.

Test signals: read `.meta/version`, parse expected package version string, and verify offset reads.
