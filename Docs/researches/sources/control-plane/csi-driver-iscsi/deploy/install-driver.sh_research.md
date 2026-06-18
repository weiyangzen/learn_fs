## sources/control-plane/csi-driver-iscsi/deploy/install-driver.sh

Purpose: installs the csi-driver-iscsi manifests into a cluster.

Control flow defaults version to `master`, builds a raw GitHub deploy URL or uses `./deploy` when the second argument contains `local`, appends `/$ver` for non-master, and applies driverinfo and node manifests with kubectl. State changes are Kubernetes API resources in the target cluster.

Dependencies are bash, kubectl, network access to GitHub for remote versions, and manifest paths. Risks include unquoted `[ $ver != "master" ]`, raw URL path assumptions for non-master versions, and applying privileged DaemonSet directly. Test signal is kubectl success and subsequent DaemonSet rollout.
