# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/ceph-conf.yaml

Purpose: renders the RBD chart's Ceph configuration ConfigMap.

Important APIs/types/functions: emits a `v1/ConfigMap` named from `.Values.cephConfConfigMapName`, with standard chart labels, `data.ceph.conf` from `tpl .Values.cephconf`, and an empty `keyring` key required by Ceph clients.

Control flow: Helm evaluates the templated `cephconf` string, allowing values to reference other chart fields, then mounts the resulting ConfigMap into provisioner and nodeplugin pods under `/etc/ceph/`.

State and persistence behavior: persisted as Kubernetes ConfigMap state. Running pods observe mounted ConfigMap contents according to Kubernetes volume update behavior.

Dependencies and integration points: depends on RBD chart helper templates for labels and on pod volume mounts in Deployment/DaemonSet templates.

Risks: malformed `cephconf` breaks Ceph client startup. `tpl` increases flexibility but also allows value-provided template evaluation. The keyring is deliberately empty, so credentials must come from CSI Secrets rather than this ConfigMap.

Test signals: Helm rendering, chart install smoke tests, and driver startup failures validate this path.
