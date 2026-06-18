# sources/control-plane/ceph-csi/e2e/upgrade.go

Purpose: small helper layer for upgrade tests that checks out a requested ceph-csi release branch and deploys the selected driver from that checkout.

Important APIs and flow: `upgradeCSI` runs `git clone --single-branch --branch <version> https://github.com/ceph/ceph-csi.git /tmp/ceph-csi`, streams output to the test process, and changes directory to `/tmp/ceph-csi/e2e`. `upgradeAndDeployCSI` calls `upgradeCSI`, then dispatches to `deployCephfsPlugin` or `deployRBDPlugin` based on `testtype`.

State and persistence: writes a clone under `/tmp/ceph-csi` and mutates process current working directory. It deploys Kubernetes resources indirectly through driver-specific deploy helpers.

Dependencies and integration: uses local `git`, OS process execution, and driver deployment functions. It is called from `upgrade-cephfs.go` and `upgrade-rbd.go`.

Risks and test signals: no cleanup or pre-removal of `/tmp/ceph-csi` is performed, so reruns can fail if the directory exists. Working-directory mutation is process-global and relies on callers to restore `cwd`. The only direct validation is successful clone, chdir, and deploy helper completion.
