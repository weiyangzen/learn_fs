# sources/cloud-native/soci-snapshotter/.github/workflows/releases.yml

Purpose: builds, validates, and drafts GitHub release artifacts for semver tags.

Important APIs/types/functions: jobs `setup`, `generate-artifacts`, `validate-artifacts`, and `create-release`; Make target `release`; script `verify-release-artifacts.sh`; artifact upload/download; `softprops/action-gh-release`.

Control flow: on tag push or release-related PRs, builds release artifacts across available runners, sets release tag and output names, creates dummy license/tag values for PR testing, uploads release artifacts, validates them per runner, and on tag push creates a draft GitHub release with merged assets.

State and persistence: creates release tarballs in workspace, GitHub artifacts, and draft release assets on tag pushes.

Dependencies/integration: uses setup matrix, Makefile release target, static library installation on AL2 ARM, and GitHub release permissions.

Risks: output names hard-code `linux-amd64` even matrix includes `al2-arm`, so naming should be verified against scripts. PR path tests use dummy tag and empty license file.

Test signals: PR workflow validates artifact generation/verification; tag push validates draft release creation.
