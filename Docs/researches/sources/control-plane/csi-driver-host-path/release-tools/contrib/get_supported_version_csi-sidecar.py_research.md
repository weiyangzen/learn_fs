## sources/control-plane/csi-driver-host-path/release-tools/contrib/get_supported_version_csi-sidecar.py

Purpose: helper for maintainers to list supported Kubernetes CSI sidecar versions and, optionally, release Docker images for documentation updates.

Important APIs are `check_gh_command`, `duration_ago`, `parse_version`, `end_of_life_grouped_versions`, `get_release_docker_image`, `get_versions_from_releases`, and `main`. Control flow uses `gh release list` to group releases by major/minor, treats latest minor as supported, supports older minors if first release is under one year old or latest patch under three months old, and can scrape `docker pull` lines from release notes.

State is remote GitHub release metadata read through the `gh` CLI. Dependencies include `dateutil.relativedelta`, subprocess, regex parsing, and authenticated/available GitHub CLI. Risks include policy drift, timezone/current-date dependence, fragile tab field parsing of `gh` output, and regex assumptions in release notes. Test signal is manual output review; no automated tests are present.
