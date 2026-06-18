# sources/control-plane/csi-driver-iscsi/test/sanity/secrets.yaml

Purpose: provides CSI sanity secrets for node-stage operations.

Important APIs and types: YAML key `NodeStageVolumeSecret` contains `username: sanity` and `password: sanitytestpassword`.

Control flow: passed to `csi-sanity` through `--csi.secrets` by `run-test.sh`.

State and persistence: static test credentials stored in the repo; not production secrets.

Dependencies and integration: consumed by csi-test and the iSCSI plugin's secret parsing.

Risks: because names are generic, failures may be hard to distinguish from missing real CHAP parameters. It should not be reused outside test context.

Test signals: sanity tests that require node-stage secret input can parse the YAML.
