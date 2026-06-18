# sources/control-plane/csi-lib-utils/release-tools/contrib/get_supported_version_csi-sidecar.py

## Purpose

This contributor utility queries GitHub releases for CSI sidecar repositories and reports supported versions according to Kubernetes CSI support policy timing. It can also print Docker image references for supported releases to help update documentation.

## Important APIs and Flow

`check_gh_command` ensures the GitHub CLI is present. `parse_version` accepts `vMAJOR.MINOR.PATCH` tags. `get_versions_from_releases` runs `gh release -R <repo> list`, parses tab-separated output and publication timestamps, and groups releases by major/minor. `end_of_life_grouped_versions` sorts each group and returns the latest patch when the first release is less than a year old or the latest patch is less than three months old. `get_release_docker_image` runs `gh release view` and regexes `docker pull ...` from release notes. `main` parses repeated `--repo`, optional display/doc flags, then prints version/date/age and optionally image names.

## State, Dependencies, and Integration

The script keeps only in-memory release lists. It depends on `gh`, Python `dateutil.relativedelta`, GitHub release formatting, and network/auth state. It integrates with manual maintenance of Kubernetes CSI documentation, especially sidecar container support tables.

## Risks and Test Signals

The release-list parser assumes `gh release list` column order and ISO timestamp format. Docker image extraction assumes release notes contain a matching `docker pull` line. The support-window logic depends on current wall-clock time. There are no automated tests; manual output sanity and `gh` failures are the test signals.
