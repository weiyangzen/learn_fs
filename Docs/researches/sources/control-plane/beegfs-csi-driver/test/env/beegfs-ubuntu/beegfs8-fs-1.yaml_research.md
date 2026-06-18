<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs8-fs-1.yaml -->
# sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs8-fs-1.yaml

Purpose: BeeGFS 8 test filesystem with TLS enabled for the management daemon and connection auth.
Important surface: Secret `beegfs-env` provides `CONN_AUTH_FILE_DATA`, `TLS_CERT_FILE_DATA`, and `TLS_KEY_FILE_DATA`; mgmtd runs `beegfs-mgmtd --init` and starts with `--tls-disable=false`, while meta/storage keep classic setup commands and auth env injection.
Control flow/state: StatefulSet starts mgmtd/meta/storage in one host-networked pod and exposes standard BeeGFS service ports. TLS material is rendered into env vars from templated indented certificate/key data.
Dependencies/integration: depends on BeeGFS 8 container entrypoint behavior and template substitution for `${TLS_CERT_FILE_DATA_INDENTED}` and `${TLS_KEY_FILE_DATA_INDENTED}`.
Risks/test signals: only mgmtd is TLS-enabled here, so test config must match expected BeeGFS 8 TLS behavior; malformed indentation breaks Secret data. Successful CSI connection using TLS cert config is the key signal.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/beegfs8-fs-1.yaml -->
