# sources/cloud-native/soci-snapshotter/scripts/update-version-in-docs.sh

Purpose: updates release version strings in getting-started documentation and optionally asserts the resulting diff.

Important APIs/types/functions: parses `--assert` and `--verbose`, validates release version with optional leading `v`, runs `sed -i -E` on `docs/getting-started.md` and `docs/eks.md`, and `assert_diff` verifies git diff contains `+version="<VERSION>"`.

Control flow: parse flags, strip leading `v`, validate major.minor.patch with optional suffix, edit docs, optionally print diff, and optionally assert expected diff was produced.

State and persistence: mutates documentation files.

Dependencies/integration points: used by release automation. Requires GNU-compatible `sed` and git for assertion.

Risks: regex only matches existing `version="x.y.z"` strings without suffix, so prerelease existing versions may not update. `VERSION=${VERSION/v/}` removes the first `v` anywhere, not just prefix. Assert checks for at least one added line but not all target docs.

Test signals: assert mode provides automation signal that docs changed to target version.
