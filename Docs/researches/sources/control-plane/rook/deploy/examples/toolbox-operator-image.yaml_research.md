# sources/control-plane/rook/deploy/examples/toolbox-operator-image.yaml

Purpose: deploys a long-running Ceph toolbox using the Rook operator image rather than the upstream Ceph image.

Important APIs/types/functions: `Deployment/rook-ceph-tools-operator-image`, service account `rook-ceph-default`, image `docker.io/rook/ceph:master`, shell command that writes `ceph.conf` and keyring, mounted admin secret and mon endpoints.

Control flow: the container continuously updates Ceph config as monitor endpoints change and then sleeps for interactive `kubectl exec` use.

State and persistence: pod-local config files are generated from Kubernetes secrets/configmaps; Ceph state is accessed externally through admin commands.

Dependencies/integration: requires admin secret, mon endpoint ConfigMap, and Rook image containing Ceph tooling.

Risks: mutable image tag and admin credentials in a long-running pod.

Test signals: deployment ready and `kubectl exec ... ceph status` succeeds.
