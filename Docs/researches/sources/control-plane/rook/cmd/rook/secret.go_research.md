## sources/control-plane/rook/cmd/rook/secret.go

Purpose: hidden key-management utility commands for retrieving KMS secrets and rotating OSD key encryption keys. It is intended for operator-controlled encrypted OSD workflows.

Important APIs and functions: `KeyManagementCmd` is the parent Cobra command. `startSecret()` builds signal-aware context, reads namespace and cluster name from env, fetches the `CephCluster`, validates KMS connection details when enabled, and returns a KMS config plus Rook context. `cliGetSecret()`/`getSecret()` fetch a KMS key and write it to a file. `cliRotateSecret()`/`rotateSecret()` invoke `osd.RotateKeyEncryptionKey()`.

Control flow: commands are added during init. Both operational handlers establish a shutdown-signal context. `getSecret()` requires exactly two args, gets a named secret, rejects empty values, and writes the output file with mode `0400`. `rotateSecret()` accepts a secret name plus data/metadata/wal device paths, then delegates key rotation.

State and persistence: reads `POD_NAMESPACE` and `ROOK_CLUSTER_NAME`; reads the CephCluster CR; may validate external KMS connectivity; writes secret material to a file; and mutates encrypted devices during rotation through downstream OSD logic.

Dependencies and integration points: KMS config, Ceph cluster client, operator shutdown signal list, Kubernetes/Rook clients, and encrypted OSD packages. Risks: secret file output path is user-provided; rotation is device-destructive if given wrong paths; fatal exits reduce composability. There are no direct tests here, so validation should include KMS-enabled e2e and rotation workflows.
