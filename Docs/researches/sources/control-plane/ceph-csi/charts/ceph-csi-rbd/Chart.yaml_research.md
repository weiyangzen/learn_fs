# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/Chart.yaml

Purpose: Helm chart metadata for the Ceph RBD CSI chart.

Important APIs/types/functions: declares `apiVersion: v1`, `name: ceph-csi-rbd`, `appVersion: canary`, `version: 3-canary`, keywords, homepage, chart source URL, and icon.

Control flow: Helm tooling reads this file for packaging, indexing, dependency-free chart identity, and release metadata. `deploy.sh` rewrites `appVersion`, `version`, and source branch references during non-devel chart publication.

State and persistence behavior: no runtime state. The file contributes packaged chart metadata in chart repositories.

Dependencies and integration points: consumed by Helm, Artifact Hub/chart repositories, release automation, and humans browsing the chart.

Risks: `canary` values are appropriate for development but must be rewritten for stable releases. The chart metadata points to the devel branch by default, so release automation correctness matters.

Test signals: packaging/release jobs and `helm lint`/chart install checks are the primary validation.
