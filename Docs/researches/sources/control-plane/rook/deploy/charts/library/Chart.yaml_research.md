## sources/control-plane/rook/deploy/charts/library/Chart.yaml

Purpose: declares the Rook Helm library chart used to share template definitions across Rook charts.

Important metadata: apiVersion v2, name `library`, type `library`, version `0.0.1`, and description. Developer notes define conventions: all templates should start with `_`, helper names should use `library.*`, cluster-scoped definitions should use `library.cluster.*`, and feature templates are preferred over scattering related content.

Control flow: as a Helm library chart, it does not render standalone Kubernetes resources. It provides named templates included by dependent charts such as `rook-ceph` and `rook-ceph-cluster`.

State and persistence: no cluster state directly. It affects rendered manifests through included templates.

Dependencies and integration points: dependent chart `Chart.yaml` files reference this chart via `file://../library`. Notes describe symlink usage to avoid churn from `helm dependency update` archives. Risks: breaking helper names or assumptions can affect multiple charts at once; Helm dependency packaging behavior should be validated in chart tests. No direct runtime tests are represented in this file.
