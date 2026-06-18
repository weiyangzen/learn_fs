<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/contrib/get_supported_version_csi-sidecar.py -->
# sources/control-plane/csi-driver-smb/release-tools/contrib/get_supported_version_csi-sidecar.py

Purpose: Helper script for maintainers to list supported Kubernetes CSI sidecar release versions and optionally associated Docker images for documentation updates.

Important APIs/functions: `check_gh_command` validates GitHub CLI availability. `duration_ago` formats relative ages. `parse_version` accepts `vX.Y.Z`. `end_of_life_grouped_versions` groups major/minor releases and applies CSI support policy: latest is always supported, minor releases younger than one year are supported at latest patch, and older minors with a patch newer than roughly three months are supported. `get_release_docker_image` parses release notes for a `docker pull` line. `get_versions_from_releases` shells out to `gh release list` and groups release dates. `main` parses repeated `--repo/-R`, display, and doc flags.

Control flow: For each repo, it reads releases via `gh`, computes supported patch versions, prints dates/ages, and optionally fetches release pages for Docker image lines.

State and persistence behavior: Read-only except terminal output; depends on GitHub CLI authentication/network state.

Dependencies and integration points: Uses Python stdlib plus `dateutil.relativedelta`, `gh`, GitHub release formatting, and CSI project support policy docs.

Risks: Release list column parsing assumes `gh release list` tab format and published timestamp position. `parse_version` ignores prereleases and nonstandard tags. The `--display` flag defaults true even when `--doc` is set, so doc output includes display output too.

Test signals: No automated tests; correctness is manual/documentation-support oriented.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/contrib/get_supported_version_csi-sidecar.py -->
