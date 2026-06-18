# sources/control-plane/csi-driver-iscsi/test/sanity/run-test.sh

Purpose: launches the iSCSI CSI plugin locally and runs the CSI sanity suite against its Unix socket.

Important APIs and types: functions `cleanup` and `install_csi_sanity_bin`; constants include endpoint `unix:///tmp/csi.sock`, default node ID `CSINode`, csi-test version `v4.3.0`, and skipped test regex `Controller Server|should work|should be idempotent|should remove target path`.

Control flow: installs `csi-sanity` into GOPATH when missing, starts `bin/iscsiplugin` with sudo on GitHub Actions or directly locally, then runs `csi-sanity` with secrets, params, endpoint, verbose Ginkgo output, and skip list. Cleanup kills `iscsiplugin` and removes the cloned `csi-test` directory.

State and persistence: creates/clones under GOPATH, starts/kills a local plugin process, uses `/tmp/csi.sock`, and may remove a local `csi-test` directory.

Dependencies and integration: depends on Go/GOPATH, git, make, csi-test, built `bin/iscsiplugin`, sudo in GitHub Actions, and the YAML fixtures in this folder.

Risks: `GO111MODULE=off` and old csi-test version may be stale. `pkill -f iscsiplugin` can terminate unrelated matching processes. The broad skip regex means only a subset of sanity coverage runs.

Test signals: csi-sanity output and process cleanup behavior.
