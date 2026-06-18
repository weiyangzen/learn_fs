<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/csi-beegfs-tlscerts.yaml -->
# sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/csi-beegfs-tlscerts.yaml

Purpose: TLS certificate snippet for BeeGFS CSI test configuration.
Important surface: list item with `sysMgmtdHost: localhost` and `tlsCert` rendered from `${TLS_CERT_FILE_DATA_INDENTED}`.
Control flow/state: no Kubernetes resource by itself; consumed by deployment tooling that embeds TLS material into driver config.
Dependencies/integration: used with BeeGFS 8 TLS test manifests and config parsing.
Risks/test signals: certificate indentation is critical because YAML block scalar is used; successful TLS connection to mgmtd is the runtime signal.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/csi-beegfs-tlscerts.yaml -->
