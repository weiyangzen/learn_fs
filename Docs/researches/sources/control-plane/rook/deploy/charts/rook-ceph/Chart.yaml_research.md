## sources/control-plane/rook/deploy/charts/rook-ceph/Chart.yaml

Purpose: declares the Helm chart for installing the Rook Ceph operator and related operator-level resources.

Important metadata: apiVersion v2, name `rook-ceph`, description, version/appVersion `0.0.1`, icon/source, dependency on local `library`, and dependency on `ceph-csi-operator` version `1.0.1` from the Ceph repository with alias `ceph-csi-operator`, conditioned by `csi.installCsiOperator`.

Control flow: chart dependencies determine whether Helm also renders/manages the CSI operator subchart. Operator templates in this chart configure RBAC, ConfigMaps, and the operator Deployment.

State and persistence: chart install creates cluster-wide/operator namespace resources and optionally the CSI operator resources.

Dependencies and integration points: local library chart, external ceph-csi-operator chart, and values under `csi.installCsiOperator`. Risks: release automation must stamp versions; external dependency availability affects dependency update/install; disabling CSI operator changes driver management assumptions. Tests should include dependency rendering with condition true and false.
