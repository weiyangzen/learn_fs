# sources/control-plane/beegfs-csi-driver/release-tools/contrib/get_supported_version_csi-sidecar.py

Purpose: Helper script for determining currently supported Kubernetes CSI sidecar release versions from GitHub releases according to Kubernetes CSI support policy, with optional Docker image extraction for documentation updates.

Important APIs/types/functions: `check_gh_command` verifies GitHub CLI availability. `duration_ago` formats release age. `parse_version` parses `vX.Y.Z`. `end_of_life_grouped_versions` groups minor releases and chooses supported patch versions based on latest, one-year, and recent-patch windows. `get_release_docker_image` extracts a `docker pull` image from a release page. `get_versions_from_releases` shells out to `gh release list`. `main` parses repeated `--repo/-R`, `--display`, and `--doc`.

Control flow: For each repo, the script obtains all releases via `gh`, groups semantic versions by major/minor, sorts groups descending, always includes the latest minor's latest version, includes latest patch for minor releases whose first release is less than a year old, and includes older minors with a patch less than three months old. It prints versions and ages, and optionally release Docker image strings.

State and persistence: No persistent writes. Reads GitHub release data via the `gh` command and current local time.

Dependencies and integration points: Requires Python, `python-dateutil`, and GitHub CLI authentication/network access. Intended to support manual updates to Kubernetes CSI documentation tables.

Risks: Relies on the tabular output shape of `gh release list`, specifically timestamp position. `--display` defaults true and cannot be turned off by a paired false flag. The policy implementation is date-sensitive and should be checked against current CSI policy before relying on it. If a release description lacks a matching `docker pull` line, image output is blank.

Test signals: No tests in this subset. Manual output can be compared against GitHub release pages and CSI policy.
