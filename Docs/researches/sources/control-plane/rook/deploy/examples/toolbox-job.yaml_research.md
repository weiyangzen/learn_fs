# sources/control-plane/rook/deploy/examples/toolbox-job.yaml

Purpose: runs a one-shot toolbox job and a script container against the Ceph cluster.

Important APIs/types/functions: `Job/rook-ceph-toolbox-job`, primary container using `/usr/local/bin/toolbox.sh --skip-watch`, a second script container, Ceph admin secret, monitor endpoint config, config override, and emptyDir config volume.

Control flow: the toolbox script writes Ceph config/keyring from mounted secrets and exits without endpoint watch; the script container can run scripted Ceph commands.

State and persistence: job completion is stored in Kubernetes; Ceph commands may modify cluster state depending on script content.

Dependencies/integration: requires Rook-created admin secret and mon endpoint ConfigMap.

Risks: example runs with admin credentials; scripts can mutate Ceph irreversibly.

Test signals: job completes and `ceph status` from the job succeeds.
