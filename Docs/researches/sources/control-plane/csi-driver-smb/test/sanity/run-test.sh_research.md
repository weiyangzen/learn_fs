# sources/control-plane/csi-driver-smb/test/sanity/run-test.sh

## Purpose
This script runs CSI sanity tests for the SMB CSI driver against a locally launched Samba container and local SMB plugin process.

## Important APIs, Types, And Functions
Functions are `cleanup`, `install_csi_sanity_bin`, and `provision_samba_server`. Important variables are `endpoint=unix:///tmp/csi.sock`, `nodeid`, normalized `ARCH`, `CSI_SANITY_BIN`, and `skipTests`.

## Control Flow
The script starts a Samba Docker container, installs `csi-sanity` from `kubernetes-csi/csi-test` v5.4.0 if absent, starts `_output/${ARCH}/smbplugin` with the Unix endpoint and node ID, sleeps briefly, then runs `csi-sanity` with secrets, volume parameters, endpoint, and skip regex. Cleanup kills `smbplugin`, removes `csi-test`, and deletes the Samba container.

## State, Persistence, And Dependencies
It creates a Docker container named `samba`, may clone into `$GOPATH/src/github.com/kubernetes-csi/csi-test`, starts a local plugin process, and uses `/tmp/csi.sock`. Dependencies include Docker, Go/GOPATH, Make, the built `_output/<arch>/smbplugin`, and possibly sudo on GitHub Actions.

## Integration Points
It consumes `params.yaml` and `secrets.yaml` and tests the driver through the CSI gRPC endpoint.

## Risks And Test Signals
`pkill -f smbplugin` can kill unrelated local processes. The install path disables modules while cloning csi-test. Fixed Samba image and skipped tests define the expected compatibility envelope. Signals are csi-sanity pass/fail and cleanup behavior.
