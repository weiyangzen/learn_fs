# sources/control-plane/external-snapshotter/release-tools/contrib/get_supported_version_csi-sidecar.py

Purpose: helper script that queries GitHub releases for CSI sidecar repositories and prints versions still supported under Kubernetes CSI support-window policy, optionally with release image names.

Important APIs/functions: `check_gh_command`, `duration_ago`, `parse_version`, `end_of_life_grouped_versions`, `get_release_docker_image`, `get_versions_from_releases`, and `main`.

Control flow: validates `gh` availability, parses one or more `--repo` arguments, fetches `gh release list`, groups semver releases by major/minor, selects latest release always plus recent minor/patch lines based on one-year and three-month windows, prints dates/ages, and optionally calls `gh release view` to extract `docker pull` image names.

State and persistence: read-only network interaction through GitHub CLI; no local files are written.

Dependencies and integration: depends on Python, `python-dateutil`, GitHub CLI authentication/network access, CSI release naming conventions, and release-note text containing docker pull commands.

Risks and test signals: risks include current-date-dependent output, GitHub CLI table format changes, regex ignoring prereleases/non-v semver tags, and policy drift. Signal is plausible supported-version table output for known sidecar repos.
