# sources/control-plane/csi-driver-iscsi/test/sanity/params.yaml

Purpose: supplies CSI sanity test volume parameters for the iSCSI driver.

Important APIs and types: YAML defines `source: "//127.0.0.1/share"`.

Control flow: `test/sanity/run-test.sh` passes this file to `csi-sanity` with `--csi.testvolumeparameters`.

State and persistence: declarative test input only.

Dependencies and integration: integrates with csi-test/csi-sanity and the iSCSI plugin's expected volume parameters.

Risks: the value resembles an SMB/NFS-style source rather than an iSCSI target tuple, so it may only be meaningful for skipped or limited sanity cases depending on driver expectations.

Test signals: sanity test startup and parameter parsing.
