# sources/control-plane/rook/images/ceph/toolbox.sh

Purpose: initializes Ceph CLI configuration inside toolbox containers.

Important APIs/types/functions: constants `CEPH_CONFIG`, `MON_CONFIG`, `KEYRING_FILE`, `CONFIG_OVERRIDE`; functions `write_endpoints` and `watch_endpoints`; reads `ROOK_CEPH_SECRET` or `/var/lib/rook-ceph-mon/secret.keyring` and writes `[client]` keyring.

Control flow: reads monitor endpoints, strips mon names to produce `mon_host`, writes `/etc/ceph/ceph.conf`, appends config override if present, writes keyring, then watches endpoint ConfigMap symlink mtime unless `--skip-watch` is passed.

State and persistence: generated config/keyring are container-local; source secrets/configmaps persist in Kubernetes.

Dependencies/integration: used by toolbox deployment/job manifests and the Rook image.

Risks: shell parsing of endpoints depends on expected `name=addr` format; admin secret is written to disk in the pod.

Test signals: running with mounted secrets creates valid `ceph.conf`; changing mon endpoints rewrites config.
