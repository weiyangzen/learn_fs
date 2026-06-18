## sources/cloud-native/containers-storage/pkg/chunked/internal/path/path.go

Purpose: tiny path-normalization helper package for chunked extraction and composefs-style flat file storage.

Important APIs/types/functions: `CleanAbsPath` and `RegularFilePathForValidatedDigest`.

Control flow: `CleanAbsPath` prefixes input with `/` and calls `filepath.Clean`, collapsing `.` and `..` into a root-confined absolute logical path. `RegularFilePathForValidatedDigest` requires a SHA256 digest and maps its encoded hex to `<first-two>/<rest>`.

State and persistence: stateless string transformation only.

Dependencies and integration points: used by `filesystem_linux.go` and `storage_linux.go` to sanitize TOC names/link targets and to derive flat composefs backing paths. Depends on `opencontainers/go-digest`.

Risks: `RegularFilePathForValidatedDigest` trusts the caller to provide a validated digest; it assumes SHA256 encoding has enough length for slicing. `CleanAbsPath` is logical normalization and not sufficient alone for filesystem containment, so fd-based opens still matter.

Test signals: `path_test.go` has broad path-cleaning examples and a SHA512 rejection case. Local test execution was blocked by missing `go`.
