# sources/cloud-native/cri-o/scripts/version_bump.go

This standalone script bumps CRI-O's version in a version Go file and RPM spec file. It accepts `-bump` (`major`, `minor`, `patch`, default patch), `-f` for the version file, and `-spec` for the spec file.

Important functions are `getCurrentVersion`, `bumpVersion`, `incrementVersionPart`, `updateSpecVersion`, and `updateVersion`. Control flow reads the current version by regex, increments the selected semantic version segment using string splitting, rewrites the version file by replacing `const Version = "..."`, rewrites the first matching `Version: oldVersion` in the spec, and prints the result. State/persistence is direct in-place file mutation.

Dependencies are only standard library packages. Integration is developer or CI version bump workflow, separate from the more elaborate `scripts/release` automation. Risks include no validation that the version has exactly three numeric parts, invalid numeric parts becoming `0` after increment failure, defaulting unknown bump types to patch, regex replacement across any matching const, and spec update requiring exact old version text. No direct tests are present in this subset.
