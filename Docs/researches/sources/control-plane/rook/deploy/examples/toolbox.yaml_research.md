# sources/control-plane/rook/deploy/examples/toolbox.yaml

Purpose: deploys the standard interactive Ceph toolbox using upstream Ceph image `quay.io/ceph/ceph:v20`.

Important APIs/types/functions: `Deployment/rook-ceph-tools`, service account `rook-ceph-default`, shell script that writes `/etc/ceph/ceph.conf` and `/etc/ceph/keyring`, admin secret, mon endpoint ConfigMap, and config override volume.

Control flow: the container writes initial config, watches monitor endpoint symlink changes, and remains available for `kubectl exec`.

State and persistence: generated config/keyring are pod-local; durable state remains in Ceph and Kubernetes secrets.

Dependencies/integration: requires Rook-created `rook-ceph-mon` secret and `rook-ceph-mon-endpoints` config.

Risks: admin key exposure in an exec-able pod; image version must match supported Ceph tooling.

Test signals: pod ready and Ceph CLI commands work without explicit config flags.
