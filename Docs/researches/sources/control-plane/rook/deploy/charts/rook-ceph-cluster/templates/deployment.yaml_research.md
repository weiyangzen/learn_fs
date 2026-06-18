## sources/control-plane/rook/deploy/charts/rook-ceph-cluster/templates/deployment.yaml

Purpose: renders the optional `rook-ceph-tools` toolbox Deployment when `.Values.toolbox.enabled` is true.

Important template behavior: creates one replica with labels, optional revision history, host networking if the CephCluster network provider is host, configurable image/security/resources/tolerations/affinity/priority, and service account `rook-ceph-default`. The container runs an inline bash script that builds `/etc/ceph/ceph.conf` from mon endpoints, writes a keyring from `ROOK_CEPH_SECRET` or mounted secret file, merges optional config override, and watches mon endpoint ConfigMap changes every 10 seconds.

Control flow: template conditional for the whole Deployment, plus inline shell loops for runtime config regeneration.

State and persistence: mounts mon secret, mon endpoints ConfigMap, optional config override, and emptyDir ceph config. It writes generated config/keyring inside the pod only. Persistent cluster effects come from user actions run inside the toolbox.

Dependencies and integration points: depends on Rook-created `rook-ceph-mon` secret and `rook-ceph-mon-endpoints` ConfigMap. Risks: inline shell parsing of mon endpoints is brittle; env-secret fallback is less secure; toolbox grants admin access to users with pod exec; host networking follows cluster network choice. Tests should render enabled toolbox with host and non-host networking.
