# sources/control-plane/csi-driver-iscsi/release-tools/contrib/get_supported_version_csi-sidecar.py

Purpose: helper script for CSI documentation maintainers to list supported sidecar release versions and optionally associated Docker images.

Important APIs and types: functions include `check_gh_command`, `duration_ago`, `parse_version`, `end_of_life_grouped_versions`, `get_release_docker_image`, `get_versions_from_releases`, and `main`. CLI accepts repeated `--repo/-R`, `--display/-d`, and `--doc/-D`.

Control flow: verifies GitHub CLI availability, fetches releases with `gh release list`, groups semantic `vX.Y.Z` releases by major/minor, selects supported versions based on CSI support policy, prints release dates and age, and optionally fetches each release page to extract a `docker pull` command.

State and persistence: no files are written; all output goes to stdout.

Dependencies and integration: depends on `gh`, Python `dateutil.relativedelta`, GitHub release metadata, and release note text conventions for Docker image extraction.

Risks: release parsing assumes tab-separated `gh release list` fields and published timestamp at index 3. The latest grouped version is always supported even if malformed policy inputs exist. `--display` defaults to true even when `--doc` is requested, so doc output includes display output too.

Test signals: manual output can be compared with CSI sidecar docs and GitHub release pages.
