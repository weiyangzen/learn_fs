# sources/cloud-native/cri-o/scripts/utils/utils.go

This utility package centralizes constants and helper functions used by CRI-O release automation. Constants define environment variable names, important file paths, branch/tag prefixes, and the canonical CRI-O org/repo string.

Important APIs are `GetCurrentVersionFromReleaseBranch`, `ConvertStringToSemver`, and `GetCurrentVersionFromVersionFile`. The first checks out a release branch with release-sdk git, reads the version file, logs it, and converts it to semver. `ConvertStringToSemver` accepts tag-like strings through release-utils helpers and clears prerelease data. `GetCurrentVersionFromVersionFile` reads a Go file and extracts `const Version = "..."` using a regular expression.

State changes are mainly branch checkout side effects in `GetCurrentVersionFromReleaseBranch`; other functions are read-only. Dependencies include semver, logrus, release-sdk git, release-utils helpers, regex, strings, and filesystem reads. Integration points are release PR creation and tag reconciliation. Risks include regex fragility if the version constant changes shape, branch checkout without restoring the prior branch, and prerelease suffixes being silently cleared. Tests in `release_test.go` cover version extraction from a mock file.
