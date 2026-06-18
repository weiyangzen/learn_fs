## sources/control-plane/rook/deploy/charts/rook-ceph/templates/configmap.yaml

Purpose: renders operator configuration ConfigMaps, including mutable operator settings and CSI image-set values.

Important template behavior: always creates `rook-ceph-operator-config` in the operator namespace with data such as `ROOK_LOG_LEVEL`, Ceph command timeout, OBC watch/provisioner settings, loop devices, mon root setting, unused CRUSH rule deletion, discovery daemon enablement, optional udev blacklist, revision history limit, host network enforcement, metrics bind address, and other optional settings. A second ConfigMap `rook-csi-operator-image-set-configmap` is rendered within `.Values.csi`, adding image references for provisioner, attacher, resizer, snapshotter, registrar, cephcsi plugin, and csi-addons when repository and tag are set.

Control flow: optional keys are rendered only when values are non-empty; CSI image map is under a `with .Values.csi`.

State and persistence: stores operator settings read at runtime and image choices consumed by the CSI operator/driver specs.

Dependencies and integration points: operator code watches `rook-ceph-operator-config`; ceph-csi driver defaults reference the image-set ConfigMap. Risks: some settings require operator restart despite comments separating mutable settings; string values must match operator env parsing; missing CSI image keys may defer to defaults elsewhere. Tests should render minimal and full CSI image settings.
