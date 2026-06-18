# sources/control-plane/csi-driver-nfs/release-tools/contrib/get_supported_version_csi-sidecar.py

Purpose: helper script for listing supported Kubernetes CSI sidecar release versions and optional Docker images for documentation updates.

Important APIs and functions: `check_gh_command`, `duration_ago`, `parse_version`, `end_of_life_grouped_versions`, `get_release_docker_image`, `get_versions_from_releases`, and `main`.

Control flow: parses one or more `--repo owner/repo` arguments, ensures `gh` is installed, calls `gh release list`, groups semantic `vX.Y.Z` releases by major/minor, applies CSI support policy heuristics where latest is always supported, releases younger than one year are supported, and older minors with a patch younger than three months are supported, then prints supported versions and optionally release-page Docker image references.

State and persistence behavior: reads live GitHub release data via the GitHub CLI and current local time. It prints results; it does not write files.

Dependencies and integration points: depends on Python, `python-dateutil`, GitHub CLI authentication/network access, and release-note text conventions containing `docker pull ...`.

Risks: output changes over time because it uses current date and GitHub release state. Release list parsing assumes tab-delimited `gh release list` columns. Docker image extraction is regex-based and can miss changed release-note formats.

Test signals: no tests in this subset; correctness is manual and depends on GitHub CLI output.
